"""Typed support predicates with the exact witness and extraction scope.

No category/subject match implies shared context or exclusive ownership. A
positive identifier hit is useful even when the complete text was not read.
"""
import re

FIELDS = ('shared_context', 'belongs_only_to_subject', 'text_scan_complete')


def establish(facts, field, value, evidence_id, source, observed_at, available_at, basis):
    if type(value) not in (bool, int) or value not in (0, 1):
        return  # Leave invalid input unresolved for the policy validator.
    facts[field] = bool(value)
    facts.setdefault('_support_fact_provenance', {})[field] = dict(
        value=bool(value), evidence_id=evidence_id, source=source,
        observed_at=observed_at.isoformat(), available_at=available_at.isoformat(), basis=basis)


def extracted(facts, category, evidence_id, source, observed_at, available_at):
    facts = dict(facts)
    if category not in {'SUPPORT_MESSAGE', 'SUPPORT_ATTACHMENT'}:
        return facts
    # Source payloads cannot supply their own trusted extraction provenance.
    facts['_support_fact_provenance'] = {}
    for field in FIELDS:
        if field in facts:
            establish(facts, field, facts[field], evidence_id, source,
                      observed_at, available_at, 'explicit predicate in record')
    return facts


def text_context(text):
    # Actual order/delivery content or a described customer/agent exchange is
    # shared context under the policy; a category or a bare keyword is not.
    return bool(re.search(r'\b(?:my order|the (?:affected )?order|order (?:update|includes)|'
                          r'delivery (?:update|query|details)|customer (?:contacted|followed up)|'
                          r'agent (?:replied|responded|said))\b', text, re.I))
