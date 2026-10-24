# Interview briefing: structured evidence milestone

## What now works

The Python pipeline handles explicit non-deletion intent, evidence-backed INCOMPLETE assessments, and carefully scoped COMPLETE assessments. It interprets relational SQL inventories and known JSON records embedded inside primary, failover, regional, reporting and read-replica SQL dumps. It preserves temporal identity history and physical copies independently.

Supported policy predicates include unconditional profile/search/export deletion, attributable analytics, retained security records with supplied retention dates, deleted-account tombstones, restore controls, and connector state. Conditional policy needs structured facts. Missing facts are not guessed.

Explicit English export, correction, marketing opt-out and no-deletion requests return NOT_APPLICABLE with no steps. This decision happens before subject/evidence inspection: a request for access is not authorization to delete or verify deletion. Mixed or ambiguous requests remain unsupported.

Runtime AI use remains zero. This is the deterministic foundation of the approved hybrid architecture, not a completed competition entry.

## COMPLETE needs positive evidence

A failed search can mean the identity was wrong, the table was incomplete, or the relevant copy was never inspected. It does not prove deletion.

For COMPLETE, a resource must first be linked to the subject. A subsequent admissible, declared SQL snapshot can then prove it absent. All known copies must comply, retained records must remain, policy conditions must be established, and no admissible evidence source may remain outside the supported SQL interpretation scope. A retained security record alone cannot establish account deletion. Every verification must have a valid citation that covers its relevant copies; unsupported multiple-witness cases are refused.

A known remaining row independently supports INCOMPLETE, but the complete remediation/verification plan may still be incomplete when other formats have not been interpreted. The benchmark measures this distinction honestly.

## Historical identities and replicas

The resolver builds alias sets only from snapshots/history available by audit_at. It uses exact stable references, emails, phones and hashes, including nested structured SQL document fields. Names alone do not merge people. Conflicting stable references fail instead of silently combining identities.

Resource lineage persists after redaction or anonymization removes the original identifiers. State is indexed by system, resource and physical-copy lineage, so a newer clean primary never overwrites a surviving failover row. Conflicting simultaneous observations are errors, not arbitrary tie-breaks.

Tombstones preserve the actual internal subject ID, not an email disguised as a reference. Direct identifiers must be cleared. Analytics must also lose subject references to be anonymous.

## Important concept: a closed evidence scope

A closed scope means the system has interpreted the evidence needed to justify its conclusion within the supplied supported corpus. It is stronger than finding no violations in the files it happened to read. An unparsed screenshot or an unknown SQL table leaves that scope open. This implementation therefore refuses COMPLETE while such admissible sources remain, even if its SQL observations look clean.

## Measured result and limitations

58 tests pass. The public benchmark produces 2/32 rows: both statuses are correct, but only case_05 matches its entire label. case_09 has the correct restore-risk finding and blocking action but lacks account-absence and retained-security verification. Baseline regressions: zero. Synthetic fixtures validate COMPLETE and NOT_APPLICABLE; public coverage does not yet demonstrate those paths.

No OCR, PDF/image interpretation, standalone JSON/log/text adapters, broad multilingual intent, paid inference, or full submission run. Missing retention/ownership facts, unlinked resources, incompatible dependency/order constraints, and unsupported citation coverage are explicit boundaries. Status accuracy is not a substitute for a complete ordered answer.

## Three likely questions

**How do you avoid unauthorized deletion?**
A narrow intent classifier distinguishes explicit non-deletion requests and returns an empty plan. Uncertain or mixed language is rejected rather than treated as permission. No live service is modified; outputs are audit plans.

**How do you prove COMPLETE rather than assume it?**
I require historical resource linkage, positive scoped absence for the profile, compliant known copies and retained records, supported policy conditions, closed SQL evidence scope and evidence-backed verification. No matching row alone is insufficient.

**How do you avoid overfitting the samples?**
The predictor never reads labels or infers people/resources from case numbers. Independent fixtures use unrelated IDs and mutated timelines, identities and copies. The evaluator opens public labels only after attempting prediction and reports unsupported cases, missing steps and regressions separately. The remaining case_09 error is documented rather than patched with its expected IDs.
