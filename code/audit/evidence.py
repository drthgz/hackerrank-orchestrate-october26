"""Participant evidence adapters feeding the existing Observation/policy planner.

Record identifiers establish lineage; transport/export times control availability.
A missing row only establishes absence in an explicitly scoped collection snapshot.
"""
import json
import re
from dataclasses import replace

from .identity import matches, normalize
from .models import AuditError, Observation, timestamp
from .text_evidence import read_logs, read_text
from .pdf_evidence import read_pdf, supplement_retention
from .sql_evidence import COLLECTIONS, extract_observations as extract_sql

SERVICE_COLLECTIONS = {
    ('account_service', 'profile_lookups'): 'USER_PROFILE',
    ('analytics_platform', 'profiles'): 'ANALYTICS_PROFILE',
    ('backup_service', 'restore_entries'): 'BACKUP_ARCHIVE',
    ('export_service', 'exports'): 'USER_EXPORT',
    ('integration_service', 'connectors'): 'DATA_FLOW',
    ('search_service', 'index_queries'): 'SEARCH_INDEX_ENTRY',
    ('security_service', 'audit_records'): 'SECURITY_AUDIT_LOG',
    ('support_platform', 'tickets'): 'SUPPORT_MESSAGE',
}


def flattened(row):
    """Unwrap known record containers, never unrelated records in a list."""
    facts = dict(row)
    for key in ('document', 'profile'):
        if isinstance(row.get(key), dict):
            for field, value in flattened(row[key]).items():
                if field in facts and facts[field] != value:
                    raise AuditError('Conflicting nested record fields')
                facts[field] = value
    return facts


def observation(file, system, resource, category, facts, observed, present=True, copy_id=None, source=''):
    observed = timestamp(observed) if isinstance(observed, str) else observed
    if observed > file.captured_at:
        raise AuditError(f'{file.file_id}: observation later than capture')
    updated = facts.get('updated_at')
    if updated and timestamp(updated) > observed:
        raise AuditError(f'{file.file_id}: record update later than observation')
    return Observation(system, resource, category, copy_id or (system + ':' + str(facts['copy_id']) if facts.get('copy_id') else system + ':service'), present,
                       observed, timestamp(updated) if updated else None, file.file_id,
                       file.captured_at, source,
                       tuple((k, str(v)) for k, v in facts.items() if k in
                             {'user_id', 'customer_reference', 'subject_reference', 'email', 'phone', 'email_hash'} and v), facts)


def lookup_facts(row):
    """Readback result vocabulary, distinct from mutation/workflow success."""
    facts = dict(row)
    facts['_lookup_values'] = tuple(str(row[k]) for k in ('lookup_value', 'subject_reference') if row.get(k))
    result = row.get('result')
    allowed = {
        'USER_PROFILE': {'FOUND', 'NOT_FOUND'}, 'SEARCH_INDEX_ENTRY': {'FOUND', 'NOT_FOUND'},
        'USER_EXPORT': {'FOUND', 'NOT_FOUND'}, 'SECONDARY_IDENTIFIER': {'FOUND', 'NOT_FOUND'},
        'ANALYTICS_PROFILE': {'IDENTIFIABLE', 'ANONYMIZED'},
        'DATA_FLOW': {'ACTIVE', 'DISABLED'}, 'BACKUP_ARCHIVE': {'ACTIVE', 'BLOCKED'},
        'SECURITY_AUDIT_LOG': {'FOUND'}, 'LEGAL_HOLD_RECORD': {'FOUND'},
        'SUPPORT_MESSAGE': {'IDENTIFIABLE', 'REDACTED'}, 'SUPPORT_ATTACHMENT': {'FOUND', 'NOT_FOUND'},
    }
    if result not in allowed.get(row.get('record_type'), set()):
        raise AuditError('Unsupported resource readback result; workflow success is not state')
    if result in {'IDENTIFIABLE', 'ANONYMIZED'}:
        facts['identifier_exposure'] = result == 'IDENTIFIABLE'
        if result == 'ANONYMIZED':
            facts.update(user_id=None, email=None, phone=None, email_hash=None, subject_reference=None)
    if row.get('record_type') == 'DATA_FLOW' and result in {'ACTIVE', 'DISABLED'}:
        facts['enabled'] = result == 'ACTIVE'
    if row.get('record_type') == 'BACKUP_ARCHIVE' and result in {'ACTIVE', 'BLOCKED'}:
        facts['restore_allowed'] = result == 'ACTIVE'
    return facts


def json_records(file):
    try:
        data = json.loads(file.path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise AuditError(f'{file.file_id}: malformed JSON evidence') from exc
    if not isinstance(data, dict):
        raise AuditError('Unsupported JSON evidence root')
    captured = data.get('exported_at', data.get('captured_at'))
    if captured and timestamp(captured) != file.captured_at:
        raise AuditError('JSON capture metadata conflicts with manifest')
    observations, snapshots = [], []
    for snap in data.get('snapshots', [data] if 'collection' in data else []):
        collection = snap['collection']
        if collection == 'operational_record_history':
            for row in snap['records']:
                if timestamp(row['recorded_at']) > file.captured_at:
                    continue
                observations.append(observation(file, row['system'], row['resource_id'], row['record_type'],
                                                lookup_facts(row), row['recorded_at'], row['result'] != 'NOT_FOUND', source=collection))
            continue
        if collection not in COLLECTIONS:
            raise AuditError('Unsupported JSON collection: ' + collection)
        system, category = COLLECTIONS[collection]
        if snap.get('data_store', system) != system:
            raise AuditError('Conflicting JSON collection/system')
        observed = snap.get('captured_at', captured)
        if timestamp(observed) > file.captured_at:
            continue
        rows = [flattened(r) for r in snap['records']]
        snapshots.append((file, system, category, observed, rows, collection, snap.get('copy_id')))
        for row in rows:
            observations.append(observation(file, system, row['resource_id'], category, row, observed, copy_id=system + ':' + str(snap['copy_id']) if snap.get('copy_id') else None, source=collection))
    if 'records' in data and 'collection' not in data:
        for row in data['records']:
            if timestamp(row['recorded_at']) > file.captured_at:
                continue
            observations.append(observation(file, row['system'], row['resource_id'], row['record_type'], lookup_facts(row),
                                            row['recorded_at'], row['result'] != 'NOT_FOUND', source='record_lookup'))
    for system, collections in data.get('service_exports', {}).items():
        for collection, rows in collections.items():
            if (system, collection) not in SERVICE_COLLECTIONS:
                raise AuditError('Unsupported service export collection')
            category = SERVICE_COLLECTIONS[system, collection]
            for row in rows:
                if timestamp(row['observed_at']) > file.captured_at:
                    continue
                facts = flattened(row)
                present = True
                if collection == 'profile_lookups':
                    if row['status_code'] not in (200, 404):
                        continue
                    present = row['status_code'] == 200
                    if present and not isinstance(row['profile'], dict):
                        raise AuditError('Successful profile read lacks payload')
                    facts['account_status'] = 'ACTIVE' if present else 'DELETED'
                elif collection == 'index_queries':
                    present = row['hits']['total'] > 0
                    documents = row['hits']['documents']
                    if present:
                        selected = [d for d in documents if d['resource_id'] == row['resource_id']]
                        if len(selected) != 1:
                            raise AuditError('Search hit resource is not unique')
                        facts.update(selected[0])
                observations.append(observation(file, system, row['resource_id'], category, facts,
                                                row['observed_at'], present, source=collection))
    if not any(key in data for key in ('snapshots', 'collection', 'records', 'service_exports')):
        raise AuditError('Unsupported JSON evidence schema')
    return observations, snapshots


def linked_facts(facts, subject):
    # Typed selectors include internal IDs as well as historical direct IDs.
    expanded = dict(facts)
    if facts.get('subject_selector') == subject.user_id:
        expanded['user_id'] = subject.user_id
    if matches(expanded, subject):
        return True
    for v in (*facts.get('_lookup_values', ()), facts.get('matched_value')):
        if not isinstance(v, str):
            continue
        if v == subject.user_id or any(normalize(k, v) in aliases for k, aliases in subject.aliases.items()):
            return True
    return False


def enrich(observations, subject, cutoff):
    """Supplement policy metadata, never overwrite measured identifier state."""
    result = []
    for o in observations:
        facts = dict(o.facts)
        related = [x for x in observations if x.system_id == o.system_id and x.resource_id == o.resource_id]
        for field in ('retention_until', 'retained_until', 'legal_hold_active', 'shared_context', 'belongs_only_to_subject'):
            sources = [x for x in related if field in x.facts]
            if field not in facts and sources:
                source = max(sources, key=lambda x: (x.observed_at, x.evidence_id))
                facts[field] = source.facts[field]
                facts.setdefault('_policy_evidence', {})[field] = source.evidence_id
        if o.category == 'SUPPORT_MESSAGE':
            if any(facts.get(k) for k in ('requester_name', 'requester_email', 'requester_phone')):
                facts['identifier_exposure'] = True
            text = facts.get('message_text', facts.get('message_excerpt'))
            if isinstance(text, str):
                # Evidence of order/delivery or an actual support exchange
                # establishes context to preserve, not permission to erase it.
                if re.search(r'\b(?:order|delivery|customer (?:contacted|followed up)|agent)\b', text, re.I):
                    facts.setdefault('shared_context', True)
                identifiers = [v for k, values in subject.aliases.items() if k != 'phone' for v in values] + list(subject.names)
                exposed = any(re.search(r'(?<![\w@.])' + re.escape(v) + r'(?![\w@.])', text, re.I)
                              for v in identifiers if v)
                if 'message_text' in facts:
                    facts['text_scan_complete'] = True
                exposed = exposed or any(re.search(r'(?<!\d)' + r'[\s()+.-]*'.join(re.escape(c) for c in phone) + r'(?!\d)', text)
                                         for phone in subject.aliases['phone'] if phone)
                facts['text_has_subject_identifiers'] = exposed
                if exposed:
                    facts['identifier_exposure'] = True
            if facts.get('identifier_exposure') is True:
                facts['text_has_subject_identifiers'] = True
                facts['text_scan_complete'] = True
        if o.category == 'LEGAL_HOLD_RECORD' and facts.get('retention_reason') == 'LEGAL_HOLD':
            facts.setdefault('legal_hold_active', bool(facts.get('retained_until') and timestamp(facts['retained_until']) >= cutoff))
        result.append(replace(o, facts=facts, subject_id=subject.user_id))
    return tuple(result)


def extract_observations(files, subject, cutoff, include_images=False):
    observations = []
    extra, snapshots = [], []
    documents = []
    for file in sorted(files, key=lambda f: (f.captured_at, f.file_id)):
        if file.captured_at > cutoff:
            continue
        if include_images and file.path.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
            from .reviewed_images import read_image
            extra.extend(read_image(file))
            continue
        if file.path.suffix == '.pdf':
            document = read_pdf(file)
            documents.append(document)
            extra.extend(document.observations)
            continue
        if file.path.suffix == '.log':
            extra.extend(read_logs(file))
            continue
        if file.path.suffix == '.txt':
            extra.extend(read_text(file))
            continue
        if file.path.suffix != '.json':
            continue
        records, scoped = json_records(file)
        extra.extend(records)
        snapshots.extend(scoped)
    # Collect identifier-backed lineage before querying inventories for absence.
    seeds = [o for o in extra if linked_facts(o.facts, subject)]
    lineage = {}
    for o in seeds:
        if o.facts.get('source_resource_id'):
            lineage.setdefault(('account_service', 'USER_PROFILE'), set()).add(o.facts['source_resource_id'])
    initial_sql = extract_sql(files, subject, cutoff, allow_pending=include_images)
    for o in initial_sql:
        if o.facts.get('source_resource_id'):
            lineage.setdefault(('account_service', 'USER_PROFILE'), set()).add(o.facts['source_resource_id'])
    observations = list(extract_sql(files, subject, cutoff, lineage, allow_pending=include_images))
    linked = {(o.system_id, o.resource_id) for o in observations}
    linked.update((o.system_id, o.resource_id) for o in extra if linked_facts(o.facts, subject))
    changed = True
    while changed:
        previous = len(linked)
        known_ids = {resource for _, resource in linked}
        linked.update((o.system_id, o.resource_id) for o in extra
                      if any(v in known_ids for v in o.facts.get('_lookup_values', ())))
        changed = len(linked) != previous
    # Identity-free compliant/absent records require prior grounded resource lineage.
    selected = [o for o in extra if (o.system_id, o.resource_id) in linked]
    for file, system, category, observed, rows, collection, copy_id in snapshots:
        ids = {r['resource_id'] for r in rows}
        lineage = {o.resource_id for o in extra + observations if o.system_id == system and o.category == category
                   and (system, o.resource_id) in linked and o.evidence_id == file.file_id
                   and o.source_table == collection and o.observed_at <= timestamp(observed)
                   and o.copy_id == (system + ':' + str(copy_id) if copy_id else system + ':service')}
        for resource in lineage - ids:
            selected.append(observation(file, system, resource, category, {}, observed, False, copy_id=system + ':' + str(copy_id) if copy_id else None, source=collection))
    for o in selected:
        # Validate known resource ownership even if its identity was removed.
        has_link = linked_facts(o.facts, subject)
        if not has_link and o.present:
            surviving = [v for k, v in o.facts.items() if k in {'email', 'phone', 'email_hash', 'customer_email', 'owner_email', 'requester_email'} and v]
            if surviving:
                raise AuditError('Known resource has conflicting surviving identifiers')
        refs = [o.facts[k] for k in ('user_id', 'customer_reference', 'subject_reference') if o.facts.get(k)]
        if any(r != subject.user_id and normalize('email', r) not in subject.aliases['email'] for r in refs):
            raise AuditError('Resource reassigned to another subject')
    return enrich(supplement_retention(observations + selected, documents, subject, cutoff), subject, cutoff)
