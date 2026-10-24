"""Deterministic readback logs and pipe-delimited handover records.

Noise, mutation acknowledgements and failed queries never establish data state.
Trace context is isolated by file, service, trace and instance; it flows forward.
"""
import json
import re

from .models import AuditError, timestamp

KV = re.compile(r'(\w+)=("(?:\\.|[^"\\])*"|[^\s]+)')


def value(raw):
    if raw.startswith('"'):
        raw = json.loads(raw)
    if raw == 'null':
        return None
    if raw in ('true', 'false'):
        return raw == 'true'
    return raw


def parse_line(line):
    when, _, body = line.partition(' ')
    observed = timestamp(when)
    if body.startswith('{'):
        fields = json.loads(body)
        fields = {k: value(v) if isinstance(v, str) else v for k, v in fields.items()}
    else:
        fields = {m[1]: value(m[2]) for m in KV.finditer(body)}
        if 'message' in fields and isinstance(fields['message'], str):
            fields.update({m[1]: value(m[2]) for m in KV.finditer(fields['message'])})
        bracket = re.match(r'\[\w+\] \[([^]]+)\] \[([^]]+)\] (\w+):', body)
        syslog = re.match(r'<\d+>1 \S+ (\S+) (\S+) - - ', body)
        pipe = re.match(r'\|\s*\w+\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(\w+)\s*\|', body)
        if bracket:
            fields.update(service=bracket[1], trace_id=bracket[2], event=bracket[3])
        elif syslog:
            fields.update(service=syslog[1], trace_id=syslog[2])
        elif pipe:
            fields.update(service=pipe[1], trace_id=pipe[2], event=pipe[3])
        if 'function' in fields:
            fields['service'] = fields['function']
        if 'requestId' in fields:
            fields['trace_id'] = fields['requestId']
    return observed, fields


def read_logs(file):
    from .evidence import observation, lookup_facts
    observations = []
    contexts = {}
    lines = []
    for number, line in enumerate(file.path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        observed, fields = parse_line(line)
        if observed <= file.captured_at:
            lines.append((observed, number, fields))
    for observed, number, fields in sorted(lines):
        event = fields.get('event', '')
        system = fields.get('system', fields.get('service', ''))
        trace = fields.get('trace_id')
        key = (system, trace, fields.get('instance'))
        context = contexts.setdefault(key, {}) if trace else {}
        if event.endswith('_started'):
            # A reused trace starts a new lookup, not a union of subjects.
            context.clear()
        selectors = ('lookup_key', 'match_key', 'subject_key', 'subject_ref', 'scan_key', 'owner_key', 'correlation_key')
        for field in selectors:
            if fields.get(field):
                context[field] = fields[field]
        facts = dict(fields)
        facts['_lookup_values'] = tuple(str(v) for k, v in context.items() if k in selectors)
        if fields.get('subject_ref'):
            facts['subject_reference'] = fields['subject_ref']
        resource = fields.get('resource_id')
        if not resource:
            continue
        present, category = True, None
        if event == 'record_lookup':
            category = fields['record_type']
            facts = lookup_facts(facts)
            present = fields['result'] != 'NOT_FOUND'
        elif event == 'profile_lookup_completed' and system == 'account_service':
            category = 'USER_PROFILE'
            if str(fields.get('rows')) not in ('0', '1') or str(fields.get('http_status')) not in ('200', '404'):
                continue
            present = str(fields['rows']) == '1'
            if present != (str(fields['http_status']) == '200'):
                raise AuditError('Profile readback row/status conflict')
            facts['account_status'] = 'ACTIVE' if present else 'DELETED'
        elif event == 'index_query_completed' and system == 'search_service':
            if fields.get('result') not in ('hit', 'miss'):
                continue
            category, present = 'SEARCH_INDEX_ENTRY', fields['result'] == 'hit'
        elif event in ('analytics_identity_scan', 'analytics_profile_read', 'analytics_profile_read_completed') and system == 'analytics_platform':
            category = 'ANALYTICS_PROFILE'
            if 'direct_identifiers' in fields:
                facts['identifier_exposure'] = str(fields['direct_identifiers']) != '0'
                # A complete identifier scan with zero hits proves anonymity;
                # individual email/phone nulls alone would not.
                if not facts['identifier_exposure']:
                    facts.update(user_id=None, customer_reference=None, email=None, phone=None, email_hash=None)
        elif event in ('export_download_check_completed', 'export_metadata_read_completed') and system == 'export_service':
            category = 'USER_EXPORT'
        elif event in ('connector_heartbeat', 'connector_config_loaded', 'connector_config_read_completed') and system == 'integration_service':
            if 'enabled' not in fields:
                continue
            category = 'DATA_FLOW'
        elif event in ('restore_candidate_evaluated', 'restore_authorization_completed', 'restore_policy_read_completed') and system == 'backup_service':
            category = 'BACKUP_ARCHIVE'
            if event == 'restore_candidate_evaluated':
                if type(fields.get('eligible')) is not bool or type(fields.get('deletion_block')) is not bool:
                    continue
                facts['restore_allowed'] = fields['eligible'] and not fields['deletion_block']
            elif event == 'restore_authorization_completed':
                if fields.get('decision') not in ('allow', 'deny'):
                    continue
                facts['restore_allowed'] = fields['decision'] == 'allow'
        elif event == 'audit_record_read_completed' and system == 'security_service':
            if str(fields.get('rows')) != '1':
                continue
            category = 'SECURITY_AUDIT_LOG'
        elif event in ('message_pii_scan', 'message_read', 'support_ticket_read_completed') and system == 'support_platform':
            category = 'SUPPORT_MESSAGE'
            if event == 'message_pii_scan':
                facts['identifier_exposure'] = True
        elif event == 'attachment_pii_scan' and system == 'support_platform':
            category = 'SUPPORT_ATTACHMENT'
            facts['identifier_exposure'] = True
        elif event == 'contact_lookup_completed' and system == 'analytics_platform' and str(fields.get('rows')) == '1':
            category = 'SECONDARY_IDENTIFIER'
        elif event == 'contact_query_completed' and system == 'support_replica' and str(fields.get('rows')) == '1':
            # The contact index is a physical support-platform replica,
            # not a separate logical application system.
            system, category = 'support_platform', 'SECONDARY_IDENTIFIER'
            facts['copy_id'] = 'support_replica'
        if category:
            copy = None
            # Explicit replica services stay independent. Query pools/instances
            # are execution routes, not resource-copy IDs without a read target.
            if fields.get('copy_id'):
                copy = system + ':' + fields['copy_id']
            observations.append(observation(file, system, resource, category, facts, observed,
                                            present, copy_id=copy, source=f'log:{number}:{event}'))
    return observations


def read_text(file):
    from .evidence import observation, lookup_facts
    result = []
    text = file.path.read_text(encoding='utf-8')
    header = re.search(r'^Snapshot: (\S+)', text, re.M)
    if header and timestamp(header[1]) != file.captured_at:
        raise AuditError('Text capture metadata conflicts with manifest')
    for number, line in enumerate(text.splitlines(), 1):
        if not line.startswith('- '):
            continue
        fields = line[2:].split(' | ')
        if len(fields) != 6:
            raise AuditError('Unsupported handover record')
        observed, system, resource, category, state, selector = fields
        if timestamp(observed) > file.captured_at:
            continue
        facts = lookup_facts(dict(record_type=category, result=state,
                                  subject_reference='' if selector == 'no direct identifier' else selector))
        result.append(observation(file, system, resource, category, facts, observed,
                                  state != 'NOT_FOUND', source=f'text:{number}'))
    if not result:
        raise AuditError('Unsupported text evidence schema')
    return result
