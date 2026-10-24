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
        # A post-cutoff snapshot cannot introduce aliases. Earlier audit events
        # may independently establish an alias even when that snapshot is later.
        if timestamp(identity['updated_at']) <= cutoff:
            for kind in values:
                if identity[kind]:
                    values[kind].add(normalize(kind, identity[kind]))
            sources.append('user_identities:' + identity['user_id'])
        for event in relevant:
            kind = event['field_name']
            if kind in values:
                for key in ('old_value', 'new_value'):
                    if event[key]:
                        values[kind].add(normalize(kind, event[key]))
                sources.append(event['audit_id'])
        if normalize('email', email) in values['email']:
            candidates.append(Subject(identity['user_id'],
                                      {k: frozenset(v) for k, v in values.items()},
                                      tuple(sorted(set(sources)))))
    if len(candidates) != 1:
        raise AuditError(f'Expected one temporally supported identity, found {len(candidates)}')
    return candidates[0]


def matches(row, subject):
    for key in ('user_id', 'customer_reference', 'subject_reference'):
        if row.get(key) == subject.user_id:
            return True
    for kind, columns in {
        'email': ('email', 'customer_email', 'owner_email', 'requester_email'),
        'phone': ('phone', 'owner_phone', 'requester_phone'),
        'email_hash': ('email_hash',),
    }.items():
        for column in columns:
            value = row.get(column)
            if isinstance(value, str) and normalize(kind, value) in subject.aliases[kind]:
                # A conflicting stable reference must not be silently merged.
                refs = [row.get(k) for k in ('user_id', 'customer_reference', 'subject_reference')]
                if any(ref and ref != subject.user_id for ref in refs):
                    raise AuditError('Identifier matches a conflicting stable subject reference')
                return True
    return False
