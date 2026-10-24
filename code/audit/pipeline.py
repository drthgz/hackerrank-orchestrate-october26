import re
from dataclasses import asdict

from .contract import order_steps, validate_result
from .identity import resolve_subject
from .models import AuditError, PolicyDecision, Result, Step, timestamp
from .sql_evidence import extract_observations, latest_per_copy


def authorize_deletion(text):
    # Deliberately narrow intent support for this milestone. Ambiguity is an
    # error, not permission. No case IDs, subject identifiers or label data.
    text = text.casefold().replace('’', "'")
    if re.search(r"\b(no|not|never|don't|do not|except|unless|if|only)\b|\?", text):
        raise AuditError('Ambiguous or restricted intent is unsupported in the SQL slice')
    for sentence in re.split(r'[.!\n]+', text):
        if re.fullmatch(r'\s*please (?:permanently )?(?:delete|remove|erase) [\w\s-]*\b(?:account|profile|personal data)\s*', sentence):
            return
    raise AuditError('Request intent is outside the supported explicit English deletion grammar')


def assess_policy(observations, rules):
    decisions = []
    for observation in observations:
        candidates = [r for r in rules if r['data_category'] == observation.category]
        if len(candidates) != 1:
            raise AuditError('Missing or ambiguous category policy')
        rule = candidates[0]
        # No guessing at conditional retention/redaction policy applicability.
        if rule['condition'] != 'Always' or rule['required_action'] != 'DELETE':
            raise AuditError('SQL profile slice only supports unconditional DELETE policy')
        decisions.append(PolicyDecision(observation, rule['required_action'], rule['rule_id']))
    return tuple(decisions)


def plan(decisions, case_id):
    remaining = {}
    for decision in decisions:
        observation = decision.observation
        if decision.action != 'DELETE':
            raise AuditError('Unsupported policy in planner')
        if observation.present:
            key = (observation.system_id, observation.resource_id)
            previous = remaining.get(key)
            if previous is None or (observation.observed_at, observation.evidence_id) > (previous.observed_at, previous.evidence_id):
                remaining[key] = observation
    if not remaining:
        raise AuditError('No surviving supported profile; global COMPLETE assessment is outside this slice')
    steps = []
    for (system, resource), observation in sorted(remaining.items()):
        steps.extend([
            Step(0, 'FINDING', system, resource, 'REPORT_REMAINING_RECORD', 'PRESENT', observation.evidence_id),
            Step(0, 'REMEDIATION', system, resource, 'DELETE_RECORD', 'ABSENT', ''),
        ])
    # Verify every discovered resource, including already-absent peers.
    for system, resource in sorted({(d.observation.system_id, d.observation.resource_id) for d in decisions}):
        steps.append(Step(0, 'VERIFICATION', system, resource, 'VERIFY_RECORD_ABSENT', 'ABSENT', ''))
    return Result(case_id, 'INCOMPLETE', order_steps(steps))


def audit(request, inputs):
    authorize_deletion(request.request_text)
    subject = resolve_subject(request.email, request.audit_at, inputs.identities, inputs.history)
    observations = extract_observations(inputs.evidence, subject, request.audit_at)
    latest = latest_per_copy(observations, request.audit_at)
    if not latest:
        raise AuditError('No supported account snapshot links to subject')
    resources = {o.resource_id for o in latest}
    claims = [x for x in inputs.activity if x['resource_id'] in resources
              and timestamp(x['event_time']) <= request.audit_at]
    for claim in claims:
        relevant = [o for o in latest if o.resource_id == claim['resource_id']]
        if timestamp(claim['event_time']) > max(o.observed_at for o in relevant):
            raise AuditError('Post-snapshot activity requires state reconstruction beyond this slice')
    decisions = assess_policy(latest, inputs.rules)
    result = plan(decisions, request.case_id)
    validate_result(result, request, inputs.citation_times())
    # Diagnostics retain physical copies, policy reasons and claims separately.
    details = {
        'scope': 'SQL primary/failover profile vertical slice; not a complete multi-format audit',
        'subject': asdict(subject),
        'observations': [asdict(o) for o in observations],
        'latest_copy_states': [asdict(o) for o in latest],
        'policy_rules': sorted({d.rule_id for d in decisions}),
        'activity_claims': claims,
        'unprocessed_evidence_formats': sorted({e.path.suffix for e in inputs.evidence if e.path.suffix != '.sql'}),
    }
    return result, details
