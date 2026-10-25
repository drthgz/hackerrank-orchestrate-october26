from .models import AuditError, Subject, timestamp


def normalize(kind: str, value: str) -> str:
    value = value.strip()
    if kind in {'email', 'email_hash'}:
        return value.casefold()
    if kind == 'phone':
        return ''.join(c for c in value if c.isdigit())
    return value


def resolve_subject(email, cutoff, identities, history) -> Subject:
    candidates = []
    for identity in identities:
        relevant = [x for x in history if x['user_id'] == identity['user_id']
                    and timestamp(x['event_time']) <= cutoff]
        values = {k: set() for k in ('email', 'phone', 'email_hash')}
        sources = []
        names = set()
        # A post-cutoff snapshot cannot introduce aliases. Earlier audit events
        # may independently establish an alias even when that snapshot is later.
        if timestamp(identity['updated_at']) <= cutoff:
            if identity.get('name'):
                names.add(identity['name'])
            for kind in values:
                if identity[kind]:
                    values[kind].add(normalize(kind, identity[kind]))
            sources.append('user_identities:' + identity['user_id'])
        for event in relevant:
            kind = event['field_name']
            if kind == 'name':
                sources.append(event['audit_id'])
                names.update(event[k] for k in ('old_value', 'new_value') if event[k])
            if kind in values:
                for key in ('old_value', 'new_value'):
                    if event[key]:
                        values[kind].add(normalize(kind, event[key]))
                sources.append(event['audit_id'])
        if normalize('email', email) in values['email']:
            candidates.append(Subject(identity['user_id'],
                                      {k: frozenset(v) for k, v in values.items()},
                                      tuple(sorted(set(sources))), frozenset(names)))
    if len(candidates) != 1:
        raise AuditError(f'Expected one temporally supported identity, found {len(candidates)}')
    return candidates[0]


def matches(row, subject):
    """Exact typed keys only; nested SQL JSON documents retain their structure."""
    # Connectors can select an internal subject ID as well as an email alias.
    # Stable IDs remain exact and share the existing conflicting-reference guard.
    stable = ('user_id', 'customer_reference', 'subject_reference', 'subject_selector')
    refs = [row[k] for k in stable if isinstance(row.get(k), str) and row[k]]
    direct = subject.user_id in refs
    alias = False
    for kind, columns in {
        'email': ('email', 'customer_email', 'owner_email', 'requester_email', 'uploaded_by', 'subject_selector', 'subject_reference'),
        'phone': ('phone', 'owner_phone', 'requester_phone'),
        'email_hash': ('email_hash',),
    }.items():
        for column in columns:
            value = row.get(column)
            if isinstance(value, str) and normalize(kind, value) in subject.aliases[kind]:
                alias = True
    # subject_reference may contain an email instead of an internal ID.
    conflicts = [ref for ref in refs if ref != subject.user_id
                 and normalize('email', ref) not in subject.aliases['email']]
    if (direct or alias) and conflicts:
        raise AuditError('Identifier matches a conflicting stable subject reference')
    def nested_match(value):
        if isinstance(value, dict):
            return matches(value, subject)
        if isinstance(value, list):
            return any(nested_match(item) for item in value)
        return False
    nested = any(nested_match(value) for value in row.values() if isinstance(value, (dict, list)))
    if nested and conflicts:
        raise AuditError('Nested identity conflicts with enclosing stable subject reference')
    return direct or alias or nested
