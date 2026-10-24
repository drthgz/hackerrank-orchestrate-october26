import re
from dataclasses import asdict

from .intent import classify_intent
from .contract import order_steps, validate_result
from .identity import resolve_subject
from .models import AuditError, Result, Step, timestamp
from .policy import assess_policy
from .evidence import extract_observations
from .pdf_evidence import read_pdf
from .sql_evidence import latest_per_copy, read_sql, TABLES, JSON_TABLES, COLLECTIONS


def authorize_deletion(text):
    if classify_intent(text) != 'DELETION':
        raise AuditError('Request does not authorize deletion')


def plan(decisions, case_id, complete_scope=False):
    if not decisions:
        raise AuditError('No evidence-backed resources to verify')
    grouped = {}
    for decision in decisions:
        o = decision.observation
        grouped.setdefault((o.system_id, o.resource_id), []).append(decision)
    incomplete = any(not d.compliant for d in decisions)
    if not incomplete and not any(d.observation.category == 'USER_PROFILE' and not d.observation.present for d in decisions):
        raise AuditError('Complete account deletion requires positive scoped profile-absence evidence')
    if not incomplete and not complete_scope:
        raise AuditError('Compliant observations do not close the unprocessed evidence scope')
    steps = []
    actions = {
        'DELETE': ('REPORT_REMAINING_RECORD', 'PRESENT', 'DELETE_RECORD'),
        'REDACT': ('REPORT_EXPOSED_PII', 'PRESENT', 'REDACT_RECORD'),
        'ANONYMIZE': ('REPORT_EXPOSED_PII', 'PRESENT', 'ANONYMIZE_RECORD'),
        'DISABLE_DATA_FLOW': ('REPORT_ACTIVE_DATA_FLOW', 'ACTIVE', 'DISABLE_DATA_FLOW'),
        'BLOCK_RESTORE': ('REPORT_RESTORE_RISK', 'ACTIVE', 'BLOCK_RESTORE'),
    }
    for (system, resource), copies in sorted(grouped.items()):
        if len({(d.action, d.verify_operation, d.final_state) for d in copies}) != 1:
            raise AuditError('Copies disagree on required policy treatment')
        violations = [d for d in copies if not d.compliant]
        select = lambda ds: max(ds, key=lambda d: (d.observation.observed_at, d.observation.evidence_id))
        representative = select(violations or copies)
        if violations:
            finding, state, action = actions[representative.action]
            steps.extend([
                Step(0, 'FINDING', system, resource, finding, state, representative.observation.evidence_id),
                Step(0, 'REMEDIATION', system, resource, action, representative.final_state, ''),
            ])
        if not incomplete and any(
                any(eid != d.observation.evidence_id for eid in d.observation.facts.get('_policy_evidence', {}).values())
                for d in copies):
            raise AuditError('Complete verification requires policy metadata from another witness')
        if not incomplete and len({d.observation.evidence_id for d in copies}) > 1:
            # A single output citation must prove all copies covered by this
            # logical verification; do not arbitrarily hide other witnesses.
            raise AuditError('Complete verification needs multiple copy witnesses; single-citation proof unavailable')
        steps.append(Step(0, 'VERIFICATION', system, resource, representative.verify_operation,
                          representative.final_state, '' if incomplete else representative.observation.evidence_id))
    ordered = order_steps(steps)
    positions = {(s.system_id, s.resource_id): s.step_no for s in ordered if s.phase == 'REMEDIATION'}
    for decision in decisions:
        o = decision.observation
        source = o.facts.get('source_resource_id')
        if source and (o.system_id, o.resource_id) in positions:
            downstream_pos = positions[(o.system_id, o.resource_id)]
            if any(resource == source and position < downstream_pos for (_, resource), position in positions.items()):
                raise AuditError('Dependency-safe remediation conflicts with canonical order; needs clarification')
    return Result(case_id, 'INCOMPLETE' if incomplete else 'COMPLETE', ordered)


def audit(request, inputs, mode='strict'):
    if mode not in {'strict', 'best-effort'}:
        raise AuditError('Unknown audit mode')
    from .competition import competition_intent, best_effort_policy
    intent = competition_intent if mode == 'best-effort' else classify_intent
    omissions = []
    if intent(request.request_text) == 'NON_DELETION':
        result = Result(request.case_id, 'NOT_APPLICABLE', ())
        validate_result(result, request, inputs.citation_times())
        return result, {'scope': 'Non-deletion intent; no deletion or verification authorized'}
    subject = resolve_subject(request.email, request.audit_at, inputs.identities, inputs.history)
    observations = extract_observations(inputs.evidence, subject, request.audit_at,
                                        include_images=mode == 'best-effort', activity=inputs.activity)
    latest = latest_per_copy(observations, request.audit_at)
    if not latest:
        raise AuditError('No supported evidence resource lineage links to subject')
    resources = {o.resource_id for o in latest}
    for event in inputs.activity:
        if timestamp(event['event_time']) > request.audit_at or event['resource_id'] in resources:
            continue
        keys = {subject.user_id, *subject.aliases['email'], *subject.aliases['email_hash']}
        if any(re.search(r'(?<![\w@.])' + re.escape(k) + r'(?![\w@.])', event.get('details', ''), re.I) for k in keys if k):
            if mode == 'strict':
                raise AuditError('Subject-linked activity resource lacks scoped evidence')
            omissions.append(dict(resource_id=event['resource_id'], reason='Subject-linked activity resource lacks scoped evidence'))
    claims = [x for x in inputs.activity if x['resource_id'] in resources
              and timestamp(x['event_time']) <= request.audit_at]
    stale_resources = set()
    for claim in claims:
        if claim.get('event_type') in {'LINK_RESOURCE_IDENTITY', 'CLASSIFY_REQUEST'}:
            continue  # Catalog/request metadata cannot mutate the observed resource state.
        relevant = [o for o in latest if o.resource_id == claim['resource_id']]
        if timestamp(claim['event_time']) > max(o.observed_at for o in relevant):
            if mode == 'strict':
                raise AuditError('Post-snapshot activity requires state reconstruction beyond this slice')
            stale_resources.add(claim['resource_id'])
            omissions.append(dict(resource_id=claim['resource_id'], reason='Post-snapshot state-changing claim requires newer readback'))
    latest = tuple(o for o in latest if o.resource_id not in stale_resources)
    if mode == 'best-effort':
        decisions, policy_omissions = best_effort_policy(latest, inputs.rules, request.audit_at)
        omissions.extend(policy_omissions)
    else:
        decisions = assess_policy(latest, inputs.rules, request.audit_at)
    unprocessed = [e for e in inputs.evidence if e.captured_at <= request.audit_at and e.path.suffix not in {'.sql', '.json', '.txt', '.log'}
                   and not (e.path.suffix == '.pdf' and read_pdf(e).understood)]
    if mode == 'best-effort':
        from .competition import relevant_unprocessed_media
        unprocessed = relevant_unprocessed_media(unprocessed, subject, latest, inputs.activity, request.audit_at)
    closed_scope = not unprocessed and not omissions
    if closed_scope:
        for file in inputs.evidence:
            if file.captured_at <= request.audit_at and file.path.suffix == '.sql':
                tables = read_sql(file)
                if set(tables) - (set(TABLES) | JSON_TABLES | {'snapshot_scope'}):
                    closed_scope = False
                if any(row['collection_name'] not in COLLECTIONS for table, rows in tables.items() if table in JSON_TABLES for row in rows):
                    closed_scope = False
    result = plan(decisions, request.case_id, complete_scope=closed_scope)
    validate_result(result, request, inputs.citation_times())
    # Diagnostics retain physical copies, policy reasons and claims separately.
    details = {
        'mode': mode,
        'omissions': omissions,
        'plan_exhaustive': not omissions and not unprocessed,
        'scope': 'Deterministic SQL/JSON/text/log/PDF audit; images remain uninterpreted',
        'evidence_scope_closed': closed_scope,
        'subject': asdict(subject),
        'observations': [asdict(o) for o in observations],
        'latest_copy_states': [asdict(o) for o in latest],
        'policy_rules': sorted({d.rule_id for d in decisions}),
        'activity_claims': claims,
        'unprocessed_evidence_formats': sorted({e.path.suffix for e in unprocessed}),
    }
    return result, details
