"""Conservative request-only grammar; no identities, workflow claims or labels.

DELETION includes requests to verify an earlier deletion. Unknown language and
unresolved conditions raise rather than becoming a NOT_APPLICABLE prediction.
"""
import re
import unicodedata

from .models import AuditError


def classify_intent(text):
    text = unicodedata.normalize('NFKC', text).casefold()
    text = text.replace('’', "'").replace('“', '"').replace('”', '"')
    text = re.sub(r'\s+', ' ', text).strip()
    clauses = [s.strip(' ,') for s in re.split(r'[.!?。！？;]+|\bbut\b|\bpero\b', text) if s.strip(' ,')]
    # Known ancillary qualifications do not make account deletion conditional.
    # Remove only their scoped condition, leaving any contradictory instruction.
    text = re.sub(
        r'(\b(?:retain backups|records can stay|keeping an internal deleted-account reference|contact me)\b[^.!?]*?)'
        r'\bif (?:policy requires (?:them|it)|required|other required records still depend on it|you need information to verify the request)\b',
        r'\1', text)
    if re.search(r'\b(?:no (?:eliminar|borrar)|ne .{0,30}(?:supprim|effac)|削除しない)\b', text):
        raise AuditError('Negated multilingual deletion is unsupported')
    if re.search(r'\b(?:how to|what happens|what would|thinking (?:of|about)|considering|not (?:requesting|authorizing|asking for))\b', text):
        raise AuditError('Informational or hypothetical wording is unsupported')
    if re.search(r'\b(?:unless|until|maybe|perhaps|later|cancel|revoke|withdraw|hypothetically)\b|\bif\b|\bonly (?:if|after)\b|\b(?:should|might) i\b', text):
        raise AuditError('Ambiguous or restricted intent is unsupported')

    negative = r"(?:do not|don't|never|not to) (?:permanently )?(?:delete|remove|erase|close) (?:my|this|the) (?:account|profile|data|personal data)\b"
    deletion = [
        r'\b(?:please )?remove records (?:linked to|under) both\b',
        r'\b(?:please |can you |could you |i (?:want|would like|am asking you) to )?(?:permanently )?(?:delete|erase|remove|close) (?:my|this|that|the|any remaining copy of my) (?:account|profile|records|personal (?:data|information|details)|name and contact details|rest|export file|search result)\b',
        r'\bi (?:want|would like) (?:the |my |this )?account\b.{0,100}\b(?:closed|erased|deleted|removed)\b',
        r'\brequest for (?:permanent )?account deletion\b|\bprocess the associated personal-data deletion\b',
        r"\bi(?: am|'m) deleting my account\b|\bfinish the deletion\b",
        r'\b(?:verify|check|confirm|confirmation|audit|inspect)\b.{0,160}\b(?:delet(?:ed|ion)|(?:profile|account) (?:is|was) (?:gone|fully removed)|(?:account|analytics data).{0,50}been removed)\b',
        r'\bcheck that nothing tied to (?:my|the) old address was left behind\b',
        r'\baccount (?:had been|was|has been) deleted\b.{0,200}\b(?:handle|remove|clean)\b',
        # Language-specific authorization and completion requests, not just keywords.
        r'\b(?:solicito|quiero|por favor)\b.{0,50}\b(?:eliminar|borrar) (?:mi|la) cuenta\b',
        r'\bcompletar la eliminaci[oó]n\b',
        r'\bje (?:demande|souhaite) la suppression (?:d[eé]finitive )?(?:de mon|du) compte\b',
        r'アカウントの(?:完全な)?削除を(?:依頼|お願い|要求)します',
    ]
    has_negative = bool(re.search(negative, text))
    # Negated actions cannot count as positive matches. Broad unknown negation
    # of deletion remains unsupported instead of guessing a no-deletion label.
    positive_text = re.sub(negative, '', text)
    positive_text = re.sub(r'\bno longer need\b', '', positive_text)
    if re.search(r"\b(?:not|don't|never|no)\b.{0,35}\b(?:delete|erase|remove|close|deletion)\b", positive_text):
        raise AuditError('Unresolved negation of deletion intent')
    positive_clauses = re.split(r'[.!?。！？;]+|\band\b(?=\s+(?:please )?(?:remove|delete|erase|close)\b)|\bbut\b|\bpero\b', positive_text)
    positive = (any(re.match(p, clause.strip()) for p in deletion[:2] for clause in positive_clauses)
                or any(re.search(p, positive_text) for p in deletion[2:]))
    if has_negative and positive:
        raise AuditError('Conflicting deletion and preservation instructions')
    # Partial scope restrictions must not silently authorize a whole-account audit.
    if positive and re.search(r'\b(?:only (?:delete|remove|erase)|(?:keep|preserve|retain) my (?:account|profile)|except (?:my|the))\b', text):
        raise AuditError('Restricted deletion scope is unsupported')
    non_deletion = [
        r"(?:please )?(?:export|download|send me a copy of|give me access to) my (?:data|personal data|account data|profile)",
        r"(?:please )?(?:correct|update) my (?:email address|phone number|name)",
        r"(?:please )?(?:unsubscribe me from|opt me out of) (?:marketing|marketing emails)",
        r'(?:please )?' + negative,
    ]
    non_matches = [any(re.fullmatch(p, s) for p in non_deletion) for s in clauses]
    if positive:
        # Export/correction plus deletion may specify ordering we cannot resolve.
        if any(non_matches) or re.search(r'\b(?:export|download|correct|update|unsubscribe|opt me out)\b.{0,50}\b(?:my data|my profile|my email|marketing)\b', text):
            raise AuditError('Mixed deletion and non-deletion actions are unsupported')
        return 'DELETION'
    if clauses and all(non_matches):
        return 'NON_DELETION'
    raise AuditError('Request intent is outside the supported deterministic grammar')
