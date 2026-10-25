"""Best-effort competition decisions, with explicit omissions and no guessed rows.

Partial plans are score candidates, not a claim of exhaustive investigation.
Every emitted INCOMPLETE still requires a supported policy violation. COMPLETE
continues through the strict proof gates. Public labels never enter prediction.
"""
import re
import unicodedata
from .models import AuditError, timestamp
from .intent import classify_intent
from .policy import assess_policy


def competition_intent(text):
    try:
        return classify_intent(text)
    except AuditError:
        pass
    text = unicodedata.normalize('NFKC', text).casefold().replace('’', "'")
    # Explicit preservation and information/correction/marketing requests.
    non = [r'not (?:asking for deletion|a request to erase)', r'(?:leave|keep) (?:the |my )?(?:account|profile|purchase history).{0,25}(?:active|as it is|in place)',
           r'without removing any of my records', r'marketing lists only', r'do not close the account',
           r"please don't delete or change anything", r'want to continue using the service']
    if any(re.search(p, text) for p in non):
        # Do not silently accept a contradictory positive deletion instruction.
        remainder = re.sub(r"(?:do not|don't|not a request to|not asking for)\s+(?:delete|close|erase|deletion)[^.?!]*", '', text)
        if re.search(r'\b(?:please delete|please erase|permanently delete)\b', remainder):
            raise AuditError('Conflicting positive deletion and preservation instructions')
        return 'NON_DELETION'
    first = re.split(r'[.。!?]', text)[0]
    if re.search(r'\b(?:unless|only if|cancel|withdraw|revoke|hypothetical|maybe)\b', first):
        raise AuditError('Unresolved conditional deletion intent')
    patterns = [
        r'^please (?:permanently )?(?:delete|erase|close) (?:the|this|my) account\b',
        r'^please (?:treat this message as a request for permanent account deletion|process a permanent account-deletion request|begin the deletion process for the account)\b',
        r'^i (?:am requesting deletion of the account|would like to submit a request to delete this account|am asking you to remove my account|want to close this account)\b',
        r'^i (?:no longer use this account and would like it permanently deleted|would like the account .{0,80} to be erased)\b',
        r'^solicito (?:a exclusão permanente da conta|la eliminación permanente de la cuenta)\b',
        r'^je demande la suppression définitive du compte\b',
        r'^このメールアドレスに関連するアカウントの完全な削除を依頼します',
        r'^이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다',
    ]
    if any(re.search(p, first) for p in patterns):
        # Ancillary identity checks/retention instructions are not conditions on
        # the clear first-clause authorization. Later explicit revocation is.
        if re.search(r"\b(?:do not|don't|cancel|revoke|withdraw)\b.{0,25}\b(?:delete|deletion|erase|close)\b", text):
            raise AuditError('Later revocation conflicts with deletion authorization')
        return 'DELETION'
    raise AuditError('Request intent remains unresolved in best-effort mode')


def best_effort_policy(observations, rules, cutoff):
    decisions, omitted = [], []
    for o in observations:
        try:
            decisions.extend(assess_policy([o], rules, cutoff, check_relationship=False))
        except AuditError as exc:
            omitted.append(dict(system_id=o.system_id, resource_id=o.resource_id, reason=str(exc)))
    retained = any(d.action == 'RETAIN' and d.observation.present for d in decisions)
    if not retained:
        tombstones = [d for d in decisions if d.observation.category == 'ACCOUNT_TOMBSTONE']
        for d in tombstones:
            omitted.append(dict(system_id=d.observation.system_id, resource_id=d.observation.resource_id,
                                reason='Tombstone reference has no supported retained-record relationship'))
        # A clean tombstone still needs the retained-reference proof before it
        # can certify compliance. Directly measured prohibited identifiers do
        # not become safe when a different record's retention is unresolved.
        # assess_policy has already required DELETED and the stable subject ID;
        # REDACT preserves that reference and never invents a retained edge.
        decisions = [d for d in decisions if d not in tombstones or not d.compliant]
    # An unresolved physical copy cannot be hidden by a compliant other copy.
    unknown = {(x['system_id'], x['resource_id']) for x in omitted}
    decisions = [d for d in decisions if not (d.compliant and
                 (d.observation.system_id, d.observation.resource_id) in unknown)]
    return tuple(decisions), omitted


def relevant_unprocessed_media(files, subject, observations, activity=(), cutoff=None):
    """Known reviewed media for other subjects cannot block every case globally.

Unknown media stays open. A relevant image with unresolved semantics stays open.
PDF customer statements stay open for their explicit subject, not everyone else.
"""
    from .pdf_evidence import read_pdf
    from .reviewed_images import review
    keys = {subject.user_id, *subject.aliases['email'], *subject.aliases['email_hash'],
            *(o.resource_id for o in observations)}
    result = []
    for file in files:
        if file.path.suffix == '.pdf':
            doc = read_pdf(file)
            text = '\n'.join(doc.pages)
            if not text.strip() or any(re.search(r'(?<![\w@.])'+re.escape(k)+r'(?![\w@.])',text,re.I) for k in keys if k):
                result.append(file)
        elif file.path.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
            data = review(file)
            if not data:
                result.append(file)
                continue
            related = any(k.casefold() in {v.casefold() for v in data['selectors']} for k in keys)
            # Identity-free storage names may correlate via a later catalog;
            # keep that unresolved image open rather than infer its owner.
            linked_names = any(event.get('event_type') == 'LINK_RESOURCE_IDENTITY'
                               and event.get('activity_id') not in {o.facts.get('_lineage_evidence') for o in observations}
                               and (cutoff is None or timestamp(event['event_time']) <= cutoff)
                               and any(name in event.get('details', '') for name in data.get('filenames', ()))
                               and any(re.search(r'(?<![\w@.])'+re.escape(k)+r'(?![\w@.])', event.get('details', ''), re.I)
                                       for k in keys if k) for event in activity)
            if linked_names or (related and data.get('unresolved')):
                result.append(file)
        else:
            result.append(file)
    return result
