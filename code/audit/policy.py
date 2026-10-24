"""Policy predicates over observed structured facts, never workflow claims."""
from .models import AuditError, PolicyDecision, timestamp

CONDITIONS = {
    'ANALYTICS_PROFILE': ('Record is still attributable to a user', 'ANONYMIZE'),
    'SECURITY_AUDIT_LOG': ('Record is within the supplied retention period', 'RETAIN'),
    'LEGAL_HOLD_RECORD': ('A supplied legal hold is active', 'RETAIN'),
    'BACKUP_ARCHIVE': ('Restore access can be blocked', 'RETAIN'),
    'ACCOUNT_TOMBSTONE': ('Account is deleted and only a stable internal user_id is needed to preserve references to retained records', 'REDACT'),
    'SUPPORT_MESSAGE': ('Conversation contains shared customer, agent, or order context that must be retained', 'REDACT'),
    'SUPPORT_ATTACHMENT': ('Attachment belongs only to the deletion subject', 'DELETE'),
}


def boolean(facts, field):
    if field not in facts or type(facts[field]) not in (bool, int) or facts[field] not in (0, 1):
        raise AuditError(f'Missing or invalid boolean fact: {field}')
    return bool(facts[field])


def identifiers_cleared(facts, required):
    if not set(required) <= facts.keys():
        raise AuditError('Missing identifier fields needed to prove redaction/anonymization')
    optional = {'name', 'full_name', 'display_name', 'owner_email', 'owner_phone', 'requester_name', 'requester_email', 'requester_phone', 'subject_selector'}
    fields = set(required) | (optional & facts.keys())
    return all(facts[k] in (None, '') for k in fields)


def assess_policy(observations, rules, cutoff=None):
    decisions = []
    for o in observations:
        facts = o.facts
        category = o.category
        rule_id = 'contract:data-flow'
        if category == 'DATA_FLOW':
            if not o.present:
                raise AuditError('Missing connector configuration is not proof of disablement')
            decisions.append(PolicyDecision(o, 'DISABLE_DATA_FLOW', rule_id, not boolean(facts, 'enabled'), 'VERIFY_DATA_FLOW_DISABLED', 'DISABLED'))
            continue
        candidates = [r for r in rules if r['data_category'] == category]
        if len(candidates) != 1:
            raise AuditError('Missing or ambiguous category policy')
        rule = candidates[0]
        action, rule_id = rule['required_action'], rule['rule_id']
        if category in {'USER_PROFILE', 'SEARCH_INDEX_ENTRY', 'USER_EXPORT', 'SECONDARY_IDENTIFIER', 'CACHE_ENTRY', 'MARKETING_PROFILE'}:
            if (rule['condition'], action) != ('Always', 'DELETE'):
                raise AuditError('Unsupported unconditional deletion policy')
            compliant, verify, state = not o.present, 'VERIFY_RECORD_ABSENT', 'ABSENT'
        else:
            if CONDITIONS.get(category) != (rule['condition'], action):
                raise AuditError('Unsupported conditional policy')
            if not o.present and category != 'SUPPORT_ATTACHMENT':
                raise AuditError('Required preserved record is missing; restoration is not an allowed operation')
            if category == 'SECURITY_AUDIT_LOG':
                end = facts.get('retention_until')
                if not end or cutoff is None or timestamp(end) < cutoff:
                    raise AuditError('Security retention applicability not established at audit time')
                compliant, verify, state = True, 'VERIFY_RECORD_PRESENT', 'PRESENT'
            elif category == 'LEGAL_HOLD_RECORD':
                if not boolean(facts, 'legal_hold_active') or not facts.get('retained_until') or cutoff is None or timestamp(facts['retained_until']) < cutoff:
                    raise AuditError('Active legal retention not established')
                compliant, verify, state = True, 'VERIFY_RECORD_PRESENT', 'PRESENT'
            elif category == 'ACCOUNT_TOMBSTONE':
                if facts.get('account_status') != 'DELETED' or not o.subject_id or (facts.get('subject_reference') or facts.get('user_id')) != o.subject_id:
                    raise AuditError('Deleted tombstone with stable reference not established')
                compliant = identifiers_cleared(facts, ('name', 'email', 'phone', 'email_hash'))
                verify, state = 'VERIFY_RECORD_REDACTED', 'REDACTED'
            elif category == 'ANALYTICS_PROFILE':
                ref = 'customer_reference' if 'customer_reference' in facts else 'user_id'
                compliant = False if facts.get('identifier_exposure') is True else identifiers_cleared(facts, (ref, 'email', 'phone', 'email_hash'))
                compliant = compliant and all(facts.get(k) in (None, '') for k in ('user_id', 'customer_reference', 'subject_reference'))
                verify, state = 'VERIFY_RECORD_ANONYMIZED', 'ANONYMIZED'
            elif category == 'BACKUP_ARCHIVE':
                compliant = not boolean(facts, 'restore_allowed')
                action, verify, state = 'BLOCK_RESTORE', 'VERIFY_RESTORE_BLOCKED', 'BLOCKED'
            elif category == 'SUPPORT_MESSAGE':
                if not boolean(facts, 'shared_context'):
                    raise AuditError('Shared support context not established')
                # Positive exposure proves a violation even in partial text.
                # Proving compliance needs a full-text scan and cleared fields.
                if facts.get('identifier_exposure') is True:
                    compliant = False
                else:
                    if not boolean(facts, 'text_scan_complete'):
                        raise AuditError('Support text needs interpretation')
                    compliant = (identifiers_cleared(facts, ('requester_name', 'requester_email', 'requester_phone'))
                                 and not boolean(facts, 'text_has_subject_identifiers'))
                verify, state = 'VERIFY_RECORD_REDACTED', 'REDACTED'
            elif category == 'SUPPORT_ATTACHMENT':
                if not boolean(facts, 'belongs_only_to_subject'):
                    raise AuditError('Attachment ownership condition not established')
                compliant, verify, state = not o.present, 'VERIFY_RECORD_ABSENT', 'ABSENT'
            else:
                raise AuditError('Unsupported policy category')
        decisions.append(PolicyDecision(o, action, rule_id, compliant, verify, state))
    if any(d.observation.category == 'ACCOUNT_TOMBSTONE' for d in decisions):
        if not any(d.action == 'RETAIN' and d.observation.present for d in decisions):
            raise AuditError('Tombstone reference has no supported retained-record relationship')
    return tuple(decisions)
