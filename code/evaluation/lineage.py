"""Experimental, label-free temporal ownership index. Never a state oracle.

Edges record positive ownership observations, not an assumption that all later
copies are clean. Unknown interval starts/ends stay unknown. Queries exclude
late witnesses and stop forward continuity at an observed reassignment.
"""
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from functools import lru_cache

from audit.evidence import flattened, json_records, observation
from audit.identity import normalize
from audit.models import timestamp
from audit.models import AuditError
from audit.policy import assess_policy
from audit.pdf_evidence import read_pdf
from audit.reviewed_images import read_image
from audit.sql_evidence import COLLECTIONS, JSON_TABLES, TABLES, read_sql
from audit.text_evidence import read_logs, read_text, parse_line


@dataclass(frozen=True)
class Alias:
    subject: str
    kind: str
    value: str
    valid_from: datetime | None
    valid_until: datetime | None
    available_at: datetime
    provenance: str


@dataclass(frozen=True)
class Edge:
    subject: str
    system: str
    resource: str
    copy: str
    valid_from: datetime
    valid_until: datetime | None
    available_at: datetime
    provenance: tuple[str, ...]
    source: str
    basis: str


def aliases(identities, history):
    result = []
    grouped = defaultdict(list)
    for h in history:
        if h['field_name'] in {'email', 'phone', 'email_hash'}:
            grouped[h['user_id'], h['field_name']].append(h)
    for identity in identities:
        uid = identity['user_id']
        for kind in ('email', 'phone', 'email_hash'):
            events = sorted(grouped[uid, kind], key=lambda h: (h['event_time'], h['audit_id']))
            for i, h in enumerate(events):
                when = timestamp(h['event_time'])
                # Old value is explicitly known before this rotation, but no
                # invented beginning-of-time timestamp is assigned to it.
                if h['old_value']:
                    start = timestamp(events[i-1]['event_time']) if i and events[i-1]['new_value'] == h['old_value'] else None
                    result.append(Alias(uid, kind, normalize(kind, h['old_value']), start, when, when, h['audit_id']))
                if h['new_value']:
                    end = timestamp(events[i+1]['event_time']) if i+1 < len(events) else None
                    result.append(Alias(uid, kind, normalize(kind, h['new_value']), when, end, when, h['audit_id']))
            if identity.get(kind):
                when = timestamp(identity['updated_at'])
                # A snapshot supplies no evidence of pre-snapshot ownership.
                result.append(Alias(uid, kind, normalize(kind, identity[kind]), when, None, when, 'user_identities:'+uid))
    return tuple(result)


DIRECT = {
    'email': ('email', 'customer_email', 'owner_email', 'requester_email', 'uploaded_by'),
    'phone': ('phone', 'owner_phone', 'requester_phone'),
    'email_hash': ('email_hash',),
}


class LineageIndex:
    def __init__(self, identities, history, observations, activity):
        self.subjects = {r['user_id'] for r in identities}
        self.provenance_times = {
            **{'user_identities:'+r['user_id']:timestamp(r['updated_at']) for r in identities},
            **{r['audit_id']:timestamp(r['event_time']) for r in history},
        }
        self.aliases = aliases(identities, history)
        self.by_alias = defaultdict(list)
        for a in self.aliases:
            self.by_alias[a.kind, a.value].append(a)
        self.observations = tuple(observations)
        self.activity = tuple(activity)

    def identifier_owners(self, kind, value, at, cutoff):
        """Historical aliases may discover stale PII only if never ambiguous.

        A reused/shared value cannot identify a subject by itself, even if a
        guessed record creation date might make one person more likely.
        """
        candidates = [a for a in self.by_alias[kind, normalize(kind, value)]
                      if a.available_at <= cutoff and (a.valid_from is None or a.valid_from <= at)]
        owners = {a.subject for a in candidates}
        return owners, tuple(sorted({a.provenance for a in candidates}))

    def owners(self, facts, at, cutoff):
        facts = flattened(facts)
        stable = {facts[k] for k in ('user_id', 'customer_reference', 'subject_reference', 'subject_selector', 'subject_ref')
                  if isinstance(facts.get(k), str) and facts[k] in self.subjects}
        unknown_stable = [facts[k] for k in ('user_id', 'customer_reference')
                          if facts.get(k) and facts[k] not in self.subjects]
        if unknown_stable:
            return set(), (), 'unknown stable reference'
        sets, provenance = [], set()
        for kind, columns in DIRECT.items():
            for k in columns:
                if isinstance(facts.get(k), str) and facts[k]:
                    owners, sources = self.identifier_owners(kind, facts[k], at, cutoff)
                    if owners:
                        sets.append(owners); provenance.update(sources)
        for value in (*facts.get('_lookup_values', ()), facts.get('matched_value'),
                      facts.get('lookup_key'), facts.get('subject_reference'), facts.get('subject_selector')):
            if not isinstance(value, str) or not value:
                continue
            if value in self.subjects:
                stable.add(value)
            else:
                possible, sources = set(), set()
                for kind in DIRECT:
                    owners, refs = self.identifier_owners(kind, value, at, cutoff)
                    possible.update(owners); sources.update(refs)
                if possible:
                    sets.append(possible); provenance.update(sources)
        if len(stable) > 1:
            return set(), (), 'conflicting stable references'
        if stable:
            owner = next(iter(stable))
            if any(owner not in s for s in sets):
                return set(), (), 'stable reference conflicts with identifiers'
            return stable, tuple(sorted(provenance)), 'stable subject reference'
        if not sets:
            return set(), (), 'no identity witness'
        common = set.intersection(*sets)
        if len(common) != 1 or any(len(s) != 1 for s in sets):
            return set(), (), 'shared or conflicting identifiers'
        return common, tuple(sorted(provenance)), 'unique historical identifier'

    @lru_cache(maxsize=1024)
    def edges_at(self, cutoff):
        edges, rejected = [], []
        for o in self.observations:
            if o.observed_at > cutoff or o.available_at > cutoff:
                continue
            owners, provenance, basis = self.owners(o.facts, o.observed_at, cutoff)
            if len(owners) == 1:
                edges.append(Edge(next(iter(owners)), o.system_id, o.resource_id, o.copy_id,
                    o.observed_at, None, max([o.available_at,*(self.provenance_times[p] for p in provenance)]),
                    (o.evidence_id, *provenance), o.source_table, basis))
            elif basis != 'no identity witness':
                rejected.append(dict(system=o.system_id, resource=o.resource_id,
                    evidence_id=o.evidence_id, observed_at=o.observed_at, reason=basis))
        for a in self.activity:
            when = timestamp(a['event_time'])
            if when > cutoff or a['event_type'] != 'LINK_RESOURCE_IDENTITY':
                continue
            # Full explicit catalog sentence, including literal repeated ID.
            # SUCCESS, mutation acknowledgements and loose token hits do not
            # establish ownership or current state.
            resource = re.escape(a['resource_id'])
            pattern = (r'(?:Data catalog linked|Attachment catalog confirmed) '+resource+
                       r' \([^()]+\) (?:to|belongs only to) (\S+) and (\S+?)(?:\.|; no other subject is linked\.)')
            match = re.fullmatch(pattern, a['details'])
            if not match:
                rejected.append(dict(evidence_id=a['activity_id'], reason='unrecognized explicit-link grammar'))
                continue
            email, uid = match.groups()
            owners, refs = self.identifier_owners('email', email, when, cutoff)
            if uid not in self.subjects or uid not in owners:
                rejected.append(dict(evidence_id=a['activity_id'], reason='catalog identity conflict or unavailable identity'))
                continue
            edges.append(Edge(uid, a['target_system'], a['resource_id'], '', when, None,
                              max([when,*(self.provenance_times[p] for p in refs)]),
                              (a['activity_id'], *refs), 'system_activity', 'explicit catalog link'))
        # Only documented lookup values can carry a cross-system join. A bare
        # ID must resolve to exactly one system/owner; numbers never participate.
        changed = True
        while changed:
            changed = False
            known = {(e.system, e.resource) for e in edges}
            by_resource = defaultdict(list)
            for e in edges:
                by_resource[e.resource].append(e)
            for o in self.observations:
                if o.observed_at > cutoff or o.available_at > cutoff:
                    continue
                if (o.system_id, o.resource_id) in known:
                    continue
                owners, _, reason = self.owners(o.facts, o.observed_at, cutoff)
                if reason != 'no identity witness':
                    continue
                for value in o.facts.get('_lookup_values', ()):
                    found = [e for e in by_resource[value] if e.valid_from <= o.observed_at]
                    if len({e.system for e in found}) != 1:
                        continue
                    # A resource lookup cannot carry an earlier owner's link
                    # past a newer explicit ownership observation.
                    if found:
                        newest = max(e.valid_from for e in found)
                        found = [e for e in found if e.valid_from == newest]
                        if any(x.get('resource') == value and x.get('system') == found[0].system
                               and newest <= x['observed_at'] <= o.observed_at for x in rejected):
                            continue
                    keys = {(e.subject, e.system) for e in found}
                    if len(keys) == 1:
                        parent = max(found, key=lambda e:e.valid_from)
                        edges.append(Edge(parent.subject, o.system_id, o.resource_id, o.copy_id,
                            o.observed_at, None, max(parent.available_at, o.available_at),
                            tuple(sorted(set((*parent.provenance, o.evidence_id)))), o.source_table,
                            'explicit resource lookup key'))
                        known.add((o.system_id, o.resource_id))
                        changed = True
                        break
        # Typed source_resource_id in the documented search snapshot is a
        # reference to the account, not a claim that the account is now absent.
        for o in self.observations:
            if o.observed_at > cutoff or o.available_at > cutoff or o.source_table != 'search_documents_primary':
                continue
            source = o.facts.get('source_resource_id')
            owners, refs, _ = self.owners(o.facts, o.observed_at, cutoff)
            if source and len(owners) == 1:
                edges.append(Edge(next(iter(owners)), 'account_service', source, '',
                    o.observed_at, None, max([o.available_at,*(self.provenance_times[p] for p in refs)]),
                    (o.evidence_id, *refs), o.source_table,
                    'documented source_resource_id'))
        # Another owner or an unresolved conflicting identity closes continuity.
        # Historical observations survive, but do not authorize later checks.
        bounded = []
        grouped, conflicts = defaultdict(list), defaultdict(list)
        for e in edges:
            grouped[e.system, e.resource].append(e)
        for x in rejected:
            if 'system' in x:
                conflicts[x['system'], x['resource']].append(x['observed_at'])
        for e in edges:
            ends = [x.valid_from for x in grouped[e.system, e.resource]
                    if x.subject != e.subject and x.valid_from >= e.valid_from]
            ends.extend(when for when in conflicts[e.system, e.resource] if when >= e.valid_from)
            bounded.append(Edge(**{**asdict(e), 'valid_until': min(ends) if ends else None}))
        return tuple(sorted(set(bounded), key=lambda e:(e.system,e.resource,e.valid_from,e.subject,e.provenance))), rejected

    @staticmethod
    def lineage_for(edges, observation):
        witnesses = [e for e in edges if (e.system,e.resource) == (observation.system_id,observation.resource_id)
                     and e.valid_from <= observation.observed_at
                     and (e.valid_until is None or observation.observed_at < e.valid_until)]
        return witnesses if len({e.subject for e in witnesses}) == 1 else []


def collect(files):
    """Read all manifest-listed records once, before subject filtering.

    Does not synthesize missing SQL rows. Scope/absence is investigated only
    after an ownership edge exists. Keeps each physical SQL copy distinct.
    """
    observations, coverage = [], []
    for f in files:
        suffix = f.path.suffix.lower()
        before = len(observations)
        if suffix == '.json':
            observations.extend(json_records(f)[0])
        elif suffix == '.log':
            observations.extend(read_logs(f))
            # This source literally names profile_service, not account_service.
            # Preserve its historical links in that namespace; no system alias
            # or policy category is inferred from resource-name prefixes.
            for number, line in enumerate(f.path.read_text().splitlines(), 1):
                if not line.strip():
                    continue
                observed, fields = parse_line(line)
                if (observed <= f.captured_at and fields.get('service') == 'profile_service'
                        and fields.get('event') == 'profile_lookup_completed'
                        and str(fields.get('rows')) == '1' and str(fields.get('http_status')) == '200'
                        and fields.get('resource_id')):
                    facts = {**fields, '_lookup_values': tuple(str(fields[k]) for k in ('correlation_key',) if fields.get(k))}
                    observations.append(observation(f, 'profile_service', fields['resource_id'],
                        'UNMAPPED_PROFILE', facts, observed, source=f'log:{number}:profile_lookup_completed'))
        elif suffix == '.txt':
            observations.extend(read_text(f))
        elif suffix == '.pdf':
            observations.extend(read_pdf(f).observations)
        elif suffix in {'.png','.jpg','.jpeg'}:
            observations.extend(read_image(f))
        elif suffix == '.sql':
            tables = read_sql(f)
            scopes = {r['origin_system']: timestamp(r['captured_at']) for r in tables.get('snapshot_scope', [])}
            for table, rows in tables.items():
                for number, row in enumerate(rows, 1):
                    if table in TABLES:
                        system, category, _ = TABLES[table]; facts = row
                    elif table in JSON_TABLES:
                        facts = json.loads(row['record_json'])
                        if row['collection_name'] not in COLLECTIONS:
                            continue
                        system, category = COLLECTIONS[row['collection_name']]
                        if facts.get('resource_id') != row['resource_id'] or system != row['origin_system']:
                            raise AuditError('SQL lineage resource/system conflicts with payload')
                        facts = {**facts, 'updated_at':row['updated_at']}
                    else:
                        continue
                    observations.append(observation(f, system, row['resource_id'], category, facts,
                        scopes.get(system, f.captured_at), copy_id=f.origin+':'+table, source=table))
        coverage.append(dict(evidence_id=f.file_id, path=str(f.path), observations=len(observations)-before))
    return tuple(observations), coverage


def serial(value):
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(type(value).__name__)


def check_resource(index, edges, subject, system, resource, cutoff, rules):
    """Separate lineage, current measured state, and authoritative scope.

    Returns diagnostics, never an inferred deletion verdict. All *known* copies
    must be compliant; this function cannot certify unknown-copy exhaustiveness.
    """
    candidates = [o for o in index.observations if (o.system_id,o.resource_id) == (system,resource)
                  and o.available_at <= cutoff and o.observed_at <= cutoff]
    latest = {}
    for o in candidates:
        previous = latest.get(o.copy_id)
        if previous is not None and previous.observed_at == o.observed_at:
            if (previous.present, previous.facts) != (o.present,o.facts):
                return dict(lineage_proven=False, state_proven=False, scope_proven=False,
                            recoverable=False, reason='conflicting simultaneous copy states')
        if previous is None or (o.observed_at,o.evidence_id) > (previous.observed_at,previous.evidence_id):
            latest[o.copy_id] = o
    copies, decisions = [], []
    for o in latest.values():
        lineage = [e for e in index.lineage_for(edges,o) if e.subject == subject]
        # Positive scoped readbacks and explicit full-record payloads only.
        # A 404 without prior ownership is intentionally insufficient.
        scope = (o.source_table in {'profile_lookups', 'record_lookup', 'operational_record_history'}
                 or o.source_table.startswith(('log:', 'text:')) or o.source_table in TABLES
                 or o.source_table in JSON_TABLES or o.source_table in COLLECTIONS
                 or o.source_table == 'profiles')
        newer_claims = [a['activity_id'] for a in index.activity
                        if a['event_type'] not in {'LINK_RESOURCE_IDENTITY','CLASSIFY_REQUEST'}
                        and a['resource_id'] == resource
                        and o.observed_at < timestamp(a['event_time']) <= cutoff]
        try:
            d = assess_policy([o], rules, cutoff, check_relationship=False)[0]
            compliant = d.compliant
            decisions.append(d)
        except AuditError:
            compliant = False
        copies.append(dict(copy_id=o.copy_id, evidence_id=o.evidence_id, source=o.source_table,
            observed_at=o.observed_at, available_at=o.available_at, lineage_proven=bool(lineage),
            lineage_witnesses=[asdict(e) for e in lineage], current_state_proven=not newer_claims,
            scope_proven=scope, compliant=compliant, newer_claims=newer_claims))
    proven = lambda field: bool(copies) and all(c[field] for c in copies)
    current_edges = [e for e in edges if (e.system,e.resource) == (system,resource)
                     and e.valid_from <= cutoff and (e.valid_until is None or cutoff < e.valid_until)]
    resource_lineage = {e.subject for e in current_edges} == {subject}
    recoverable = (proven('lineage_proven') and proven('current_state_proven') and proven('scope_proven')
                   and proven('compliant') and len({o.evidence_id for o in latest.values()}) == 1)
    return dict(lineage_proven=resource_lineage, lineage_state_join_proven=proven('lineage_proven'),
                state_proven=proven('current_state_proven'),
                scope_proven=proven('scope_proven'), recoverable=recoverable, copies=copies,
                operation=decisions[0].verify_operation if recoverable else None,
                final_state=decisions[0].final_state if recoverable else None,
                evidence_id=next(iter(latest.values())).evidence_id if recoverable else None,
                reason='known-copy check only; no whole-case completeness assertion')
