"""Competition status predictions, explicitly separate from verified audits.

Fixed before benchmark evaluation: preserve every best-effort result; otherwise
predict INCOMPLETE when subject-linked observations still expose direct PII or an
enabled recreation path, COMPLETE otherwise. Lack of contradiction is a prediction
heuristic, never an absence proof. No reported status, labels, case IDs, invented
resources or inferred retention dates enter this rule. Confidence is qualitative
and uncalibrated. Missing facts remain outside the three-column CSV.
"""
import csv
import json
from dataclasses import asdict

from .competition import best_effort_policy
from .contract import ORDER, OUTPUT_HEADER, order_steps, validate_result
from .models import AuditError, Observation, Result, Step
from .pipeline import audit

FALLBACK_GATES = {
    'No supported evidence resource lineage links to subject',
    'No evidence-backed resources to verify',
    'Complete account deletion requires positive scoped profile-absence evidence',
    'Compliant observations do not close the unprocessed evidence scope',
}
PII_CATEGORIES = {'USER_PROFILE', 'SECONDARY_IDENTIFIER', 'SEARCH_INDEX_ENTRY', 'CACHE_ENTRY',
                  'MARKETING_PROFILE', 'USER_EXPORT', 'ANALYTICS_PROFILE', 'ACCOUNT_TOMBSTONE',
                  'SUPPORT_MESSAGE', 'SUPPORT_ATTACHMENT'}
DIRECT_FIELDS = {'name', 'full_name', 'display_name', 'email', 'phone', 'email_hash',
                 'owner_email', 'owner_phone', 'customer_email', 'requester_name',
                 'requester_email', 'requester_phone'}


def residual_signals(observations):
    signals = []
    for o in observations:
        if not o.present:
            continue
        facts = o.facts
        exposed = (facts.get('identifier_exposure') is True
                   or facts.get('text_has_subject_identifiers') is True
                   or any(facts.get(k) not in (None, '') for k in DIRECT_FIELDS if k in facts))
        if o.category in PII_CATEGORIES and exposed:
            signals.append(dict(system_id=o.system_id, resource_id=o.resource_id,
                                evidence_id=o.evidence_id, signal='observed_direct_identifiers'))
        if ((o.category == 'DATA_FLOW' and facts.get('enabled') in (True, 1))
                or (o.category == 'BACKUP_ARCHIVE' and facts.get('restore_allowed') in (True, 1))):
            signals.append(dict(system_id=o.system_id, resource_id=o.resource_id,
                                evidence_id=o.evidence_id, signal='observed_recreation_permission'))
    return signals


def supported_verifications(decisions, status):
    """Retain only checks whose policy and state are established, never guess IDs."""
    grouped = {}
    for d in decisions:
        grouped.setdefault((d.observation.system_id, d.observation.resource_id), []).append(d)
    steps = []
    for (system, resource), copies in sorted(grouped.items()):
        if any(not d.compliant for d in copies):
            continue
        if len({(d.verify_operation, d.final_state) for d in copies}) != 1:
            continue
        if status == 'COMPLETE':
            # Retain the audit engine's per-step witness restrictions; only
            # whole-case proof gates are bypassed by the status prediction.
            if len({d.observation.evidence_id for d in copies}) != 1:
                continue
            if any(any(eid != d.observation.evidence_id
                       for eid in d.observation.facts.get('_policy_evidence', {}).values()) for d in copies):
                continue
        chosen = max(copies, key=lambda d: (d.observation.observed_at, d.observation.evidence_id))
        steps.append(Step(0, 'VERIFICATION', system, resource, chosen.verify_operation,
                          chosen.final_state, chosen.observation.evidence_id if status == 'COMPLETE' else ''))
    return order_steps(steps)


def predict(request, inputs):
    """Return a status prediction and a mandatory uncertainty/provenance sidecar."""
    try:
        result, detail = audit(request, inputs, mode='best-effort')
        detail = dict(detail)
        detail['prediction'] = dict(
            kind='preserved_best_effort', status_uncertain=False, confidence='high',
            confidence_calibrated=False, verified_compliance_decision=False,
            plan_complete=detail.get('plan_exhaustive', result.deletion_status == 'NOT_APPLICABLE'),
            interpretation='Evidence-backed status preserved; plan omissions remain diagnostic.')
        return result, detail
    except AuditError as exc:
        if str(exc) not in FALLBACK_GATES:
            raise  # Invalid input/identity/schema must not silently become a prediction.
        detail = dict(getattr(exc, 'details', {}))
        detail['audit_blocker'] = str(exc)
    observations = tuple(Observation(**row) for row in detail.get('latest_copy_states', []))
    decisions, omissions = best_effort_policy(observations, inputs.rules, request.audit_at)
    signals = residual_signals(observations)
    status = 'INCOMPLETE' if signals else 'COMPLETE'
    result = Result(request.case_id, status, supported_verifications(decisions, status))
    try:
        validate_result(result, request, inputs.citation_times())
        audit_validation_error = None
    except AuditError as exc:
        audit_validation_error = str(exc)
    detail['prediction'] = dict(
        kind='uncertain_fallback', status_uncertain=True, confidence='low', confidence_calibrated=False,
        verified_compliance_decision=False, plan_complete=False,
        heuristic='residual_identifiers_or_recreation_else_complete', residual_signals=signals,
        missing_proof=[detail['audit_blocker'], *sorted({o['reason'] for o in omissions})],
        audit_validation_error=audit_validation_error,
        interpretation='Competition prediction only; COMPLETE is not verified compliance. '
                       'No observed contradiction does not prove absence.')
    validate_prediction(result, request, inputs.citation_times())
    return result, detail


def validate_prediction(result, request, citation_times):
    """Validate CSV/step structure and citations, without certifying proof coverage.

    Unlike audit validation, an uncertain deletion prediction may have no known
    steps or only partial verification. This distinction is reported, not hidden.
    """
    if result.case_id != request.case_id or result.deletion_status not in {'COMPLETE', 'INCOMPLETE', 'NOT_APPLICABLE'}:
        raise AuditError('Invalid prediction identity/status')
    if result.deletion_status == 'NOT_APPLICABLE' and result.steps:
        raise AuditError('Non-deletion prediction must have no steps')
    seen = set()
    for i, step in enumerate(result.steps, 1):
        if type(step.step_no) is not int or step.step_no != i:
            raise AuditError('Invalid prediction step numbering')
        if any(not isinstance(v, str) for k, v in asdict(step).items() if k != 'step_no'):
            raise AuditError('Invalid prediction step field type')
        spec = ORDER.get(step.operation)
        if spec is None or (step.phase, step.state) != spec[2:] or not step.system_id or not step.resource_id:
            raise AuditError('Invalid prediction step vocabulary/resource')
        key = (step.phase, step.operation, step.system_id, step.resource_id)
        if key in seen:
            raise AuditError('Duplicate prediction step')
        seen.add(key)
        if result.deletion_status == 'COMPLETE' and step.phase != 'VERIFICATION':
            raise AuditError('COMPLETE prediction may contain only verification')
        needs_citation = step.phase == 'FINDING' or result.deletion_status == 'COMPLETE'
        if needs_citation:
            if step.evidence_id not in citation_times or citation_times[step.evidence_id] > request.audit_at:
                raise AuditError('Missing or future prediction citation')
        elif step.evidence_id:
            raise AuditError('Future prediction steps must not cite evidence')
    if tuple(result.steps) != order_steps(result.steps):
        raise AuditError('Noncanonical prediction steps')


def write_predictions(path, results, requests, citation_times):
    expected = {r.case_id: r for r in requests}
    results = sorted(results, key=lambda r: r.case_id)
    if len(results) != len(expected) or {r.case_id for r in results} != set(expected):
        raise AuditError('Prediction coverage differs from request set')
    for result in results:
        validate_prediction(result, expected[result.case_id], citation_times)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as target:
        writer = csv.writer(target, lineterminator='\n')
        writer.writerow(OUTPUT_HEADER)
        for result in results:
            writer.writerow([result.case_id, result.deletion_status,
                             json.dumps([asdict(s) for s in result.steps], separators=(',', ':'), ensure_ascii=False)])
