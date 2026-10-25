"""Independent fact/policy diagnostics; never imported by prediction.

An observed value is not a policy conclusion or a submission step. These ledgers
preserve measured facts even when the official vocabulary cannot express them
without asserting an unresolved obligation. No labels or case IDs enter a track.
"""
from audit.models import AuditError
from audit.policy import assess_policy


def admissible(o, cutoff):
    if not o.subject_id:
        return 'Missing resolved subject-to-resource lineage'
    if o.available_at > cutoff or o.observed_at > cutoff:
        return 'Evidence observation or capture is after audit_at'
    if o.observed_at > o.available_at or (o.updated_at and o.updated_at > o.observed_at):
        return 'Evidence timestamps conflict'
    if type(o.present) is not bool:
        return 'Invalid observed presence type'
    return None


def fact(o, value, basis, field=None):
    witness = o.facts.get('_support_fact_provenance', {}).get(field)
    if witness:
        return dict(value=value, provenance=dict(witness))
    # Supplemental evidence is named separately; never attribute its contents
    # or observation time to the current readback.
    supplemental = o.facts.get('_policy_evidence', {}).get(field)
    return dict(value=value, provenance=dict(
        evidence_id=supplemental or o.evidence_id,
        source='supplemental policy metadata' if supplemental and supplemental != o.evidence_id else o.source_table,
        observed_at=None if supplemental and supplemental != o.evidence_id else o.observed_at.isoformat(),
        available_at=None if supplemental and supplemental != o.evidence_id else o.available_at.isoformat(),
        basis=basis))


def policy(o, rules, cutoff):
    try:
        decision, = assess_policy([o], rules, cutoff, check_relationship=False)
        return dict(established=True, action=decision.action, compliant=decision.compliant,
                    verify_operation=decision.verify_operation, rule_id=decision.rule_id)
    except AuditError as exc:
        return dict(established=False, action=None, compliant=None, verify_operation=None, reason=str(exc))


def base(o, cutoff):
    error = admissible(o, cutoff)
    return dict(system_id=o.system_id, resource_id=o.resource_id, copy_id=o.copy_id,
                subject_id=o.subject_id, evidence_id=o.evidence_id,
                admissible=error is None, exclusion=error,
                observed_facts={}, policy=None, submission_changes=[])


def security_track(observations, rules, cutoff):
    rows = []
    for o in observations:
        if o.category != 'SECURITY_AUDIT_LOG':
            continue
        row = base(o, cutoff)
        if row['admissible']:
            row['observed_facts']['present'] = fact(o, o.present, 'subject-linked resource readback')
            if 'retention_until' in o.facts:
                row['observed_facts']['retention_until'] = fact(o, o.facts['retention_until'],
                    'explicit supplied deadline, not derived from presence or an integrity seal', 'retention_until')
            row['policy'] = policy(o, rules, cutoff)
            if not row['policy']['established']:
                row['csv_blocker'] = 'VERIFY_RECORD_PRESENT requires a policy-required retained record, not mere presence'
        rows.append(row)
    return rows


def support_track(observations, rules, cutoff):
    rows = []
    for o in observations:
        if o.category not in {'SUPPORT_MESSAGE', 'SUPPORT_ATTACHMENT'}:
            continue
        row = base(o, cutoff)
        row['category'] = o.category
        if row['admissible']:
            measured = row['observed_facts']
            measured['present'] = fact(o, o.present, 'subject-linked resource readback')
            # Only positive exposure can be established from a partial record.
            # No hit is not a clean-text claim, even when contact fields are null.
            fields = ('requester_name', 'requester_email', 'requester_phone', 'name', 'email', 'phone',
                      'email_hash', 'owner_email', 'owner_phone')
            exposed = o.present and (o.facts.get('identifier_exposure') is True
                or o.facts.get('text_has_subject_identifiers') is True
                or any(o.facts.get(k) not in (None, '') for k in fields if k in o.facts))
            if exposed:
                measured['identifier_exposure'] = fact(o, True, 'positive measured identifier hit; not a policy violation conclusion')
            for field in ('shared_context', 'belongs_only_to_subject', 'text_scan_complete', 'text_has_subject_identifiers'):
                if type(o.facts.get(field)) is bool:
                    measured[field] = fact(o, o.facts[field], 'explicit predicate or scoped text scan', field)
                    if field == 'text_has_subject_identifiers':
                        measured[field]['scope'] = ('whole_message' if o.facts.get('text_scan_complete') is True
                            else 'message_excerpt' if 'message_excerpt' in o.facts else 'partial_or_unspecified')
            row['policy'] = policy(o, rules, cutoff)
            if not row['policy']['established']:
                row['csv_blocker'] = ('No neutral exposure/presence operation exists; findings assert policy-required treatment '
                    'and INCOMPLETE plans require supported remediation and verification')
        rows.append(row)
    return rows


def tracks(observations, rules, cutoff, enabled):
    """Combination is diagnostic union, with no promotion to submission steps."""
    unknown = set(enabled) - {'security', 'support'}
    if unknown:
        raise ValueError('Unknown policy track')
    functions = dict(security=security_track, support=support_track)
    return {name: functions[name](observations, rules, cutoff) for name in sorted(set(enabled))}
