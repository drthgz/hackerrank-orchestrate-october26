import re
from dataclasses import asdict

from .contract import order_steps, validate_result
from .identity import resolve_subject
from .models import AuditError, Result, Step, timestamp
from .policy import assess_policy
from .sql_evidence import extract_observations, latest_per_copy, read_sql, TABLES, JSON_TABLES, COLLECTIONS


def classify_intent(text):
    text = text.casefold().replace('’', "'").strip()
    sentences = [s.strip() for s in re.split(r'[.!\n]+', text) if s.strip()]
    non_deletion = [
        r"(?:please )?(?:export|download|send me a copy of) my (?:data|personal data|account data)",
        r"(?:please )?(?:correct|update) my (?:email address|phone number|name)",
        r"(?:please )?(?:unsubscribe me from|opt me out of) (?:marketing|marketing emails)",
        r"(?:please )?(?:do not|don't) (?:delete|remove|erase) my (?:account|profile|data)",
    ]
    # Every clause must be explicitly understood: mixed deletion/non-deletion,
    # negation, qualifications and unknown clauses do not imply authorization.
    if sentences and all(any(re.fullmatch(p, s) for p in non_deletion) for s in sentences):
        return 'NON_DELETION'
    if re.search(r"\b(no|not|never|don't|do not|except|unless|if|only|cancel|revoke|withdraw)\b|\?", text):
        raise AuditError('Ambiguous or restricted intent is unsupported')
    patterns = [
        r'please (?:permanently )?(?:delete|remove|erase) [\w\s-]*\b(?:account|profile|personal data)(?: associated with this email address| linked to this email address)?',
        r'please treat this message as a request for permanent account deletion',
    ]
    if any(any(re.fullmatch(p, s) for p in patterns) for s in sentences):
        return 'DELETION'
    raise AuditError('Request intent is outside the supported explicit English grammar')


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
        raise AuditError('Compliant SQL observations do not close the unprocessed evidence scope')
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


def audit(request, inputs):
    if classify_intent(request.request_text) == 'NON_DELETION':
        result = Result(request.case_id, 'NOT_APPLICABLE', ())
        validate_result(result, request, inputs.citation_times())
        return result, {'scope': 'Non-deletion intent; no deletion or verification authorized'}
    subject = resolve_subject(request.email, request.audit_at, inputs.identities, inputs.history)
    observations = extract_observations(inputs.evidence, subject, request.audit_at)
    latest = latest_per_copy(observations, request.audit_at)
    if not latest:
        raise AuditError('No supported SQL resource lineage links to subject')
    resources = {o.resource_id for o in latest}
    for event in inputs.activity:
        if timestamp(event['event_time']) > request.audit_at or event['resource_id'] in resources:
            continue
        keys = {subject.user_id, *subject.aliases['email'], *subject.aliases['email_hash']}
        if any(re.search(r'(?<![\w@.])' + re.escape(k) + r'(?![\w@.])', event.get('details', ''), re.I) for k in keys if k):
            raise AuditError('Subject-linked activity resource lacks scoped SQL evidence')
    claims = [x for x in inputs.activity if x['resource_id'] in resources
              and timestamp(x['event_time']) <= request.audit_at]
    for claim in claims:
        relevant = [o for o in latest if o.resource_id == claim['resource_id']]
        if timestamp(claim['event_time']) > max(o.observed_at for o in relevant):
            raise AuditError('Post-snapshot activity requires state reconstruction beyond this slice')
    decisions = assess_policy(latest, inputs.rules, request.audit_at)
    unprocessed = [e for e in inputs.evidence if e.captured_at <= request.audit_at and e.path.suffix != '.sql']
    closed_scope = not unprocessed
    if closed_scope:
        for file in inputs.evidence:
            if file.captured_at <= request.audit_at:
                tables = read_sql(file)
                if set(tables) - (set(TABLES) | JSON_TABLES | {'snapshot_scope'}):
                    closed_scope = False
                if any(row['collection_name'] not in COLLECTIONS for table, rows in tables.items() if table in JSON_TABLES for row in rows):
                    closed_scope = False
    result = plan(decisions, request.case_id, complete_scope=closed_scope)
    validate_result(result, request, inputs.citation_times())
    # Diagnostics retain physical copies, policy reasons and claims separately.
    details = {
        'scope': 'Structured SQL audit; unprocessed formats remain outside interpretation',
        'evidence_scope_closed': closed_scope,
        'subject': asdict(subject),
        'observations': [asdict(o) for o in observations],
        'latest_copy_states': [asdict(o) for o in latest],
        'policy_rules': sorted({d.rule_id for d in decisions}),
        'activity_claims': claims,
        'unprocessed_evidence_formats': sorted({e.path.suffix for e in inputs.evidence if e.path.suffix != '.sql' and e.captured_at <= request.audit_at}),
    }
    return result, details
