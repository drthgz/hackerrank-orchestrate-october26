# Forensic accuracy gap analysis

Analysis of commit `a4a358b`; candidate preserved byte-for-byte. No inference API calls, push, submission, or predictor changes. Public references are used only for evaluation, never as production rules.

## Findings and measurement method

Root candidate: 518 rows; SHA-256 `b9045f0b71ec8025cfa1b67dd3b7ee5a82f7411787173743580d0f15aa9275b6`. Public requests are a separate 32-row request file, so comparisons use the existing `artifacts/prediction-benchmark/predictions.csv`, reproduced byte-for-byte at `/tmp/forensic-public.csv`. Public case IDs are not keys in the 518-row candidate. All 32 statuses match; only case_05 and case_06 match exactly.

The public reference contains 193 steps; the predictor emits 132. Matching all six content fields while ignoring step_no gives 129 matches, 64 unmatched reference steps, and 3 unmatched predictions: recall 66.84%, precision 97.73%. The three extras belong to one grounded object-storage resource. No emitted operation/state or resource-field substitution explains the gap.

Method: match complete step content as multisets, then align by phase/system/resource to detect substitutions; compare relative order only among matched steps. Reconcile each omission against adapter output, latest-copy state, policy omissions, and raw source contents. Search all manifest-listed text, JSON, SQL and log artifacts, PDF text via pdftotext, and existing hash-bound screenshot reviews; inspect matching records, traces and timestamps. Raw matches are discovery aids, not proof. Resource IDs shown below come from public references strictly as evaluation targets. “C” means the exact required tuple cannot be reconstructed from the inspected participant material without an unsupported link/fact; it is not a claim about private truth.

## Mismatch taxonomy

| Category | Steps | Cases | Interpretation |
| --- | ---: | ---: | --- |
| Missing FINDING | 5 | 5 | Unmatched expected content, not numbering offsets |
| Missing REMEDIATION | 5 | 5 | Unmatched expected content, not numbering offsets |
| Missing VERIFICATION | 54 | 30 | Unmatched expected content, not numbering offsets |
| Incorrect operations or states | 0 | 0 | No aligned substitutions or invalid vocabulary |
| Incorrect evidence citations | 0 | 0 | All 49 emitted findings/compliant checks that align with reference have the expected citation |
| Incorrect resource/system identification | 0 | 0 | No established substitutions; object_storage/object_19 is separately supported, not a renamed support resource |
| Incorrect ordering or numbering | 0 independent defects | 0 | 55 matched steps have shifted absolute numbers because other content is missing/extra; 0 relative-order inversions; all numbering consecutive |
| Extra steps versus reference | 3 | 1 | case_07 object_19 finding/remediation/check; supported, not demonstrated hallucinations |
| Extra unsupported steps | 0 established | 0 | Three benchmark extras require scope reconciliation, not blind deletion |
| Policy/retention interpretation gaps | 37 | 21 | G3 + G4 + G5; overlaps phase counts, not an additional 37 errors |

The earlier 49/50 emitted citation metric counts the extra object_19 citation as unmatched. It does not establish a wrong citation on a matching expected finding. Positional field accuracy also mixes absent content with shifted fields and must not be read as a count of independent field defects.

## Root-cause clusters

| Cluster | Cases | Missing steps | Root cause and code | Complexity | Risk | Evidence support |
| --- | ---: | ---: | --- | --- | --- | --- |
| G1: Account absence and missing resource lineage | 20 | 20 | Evidence correlation: evidence.extract_observations requires grounded resource ownership before scoped absence; sql_evidence links by real identifiers. Identity snapshots identify people but not account resource IDs. | High | High if inferred IDs | Absence scope exists; most exact IDs/links do not |
| G2: Anonymous analytics lineage | 7 | 7 | Evidence correlation: fully cleared profiles have no remaining subject selector; resource closure has no prior identifier-bearing seed. | Medium/high | High if assigned by row order/product/cohort | Compliant payload exists; ownership link missing |
| G3: Security retention and availability | 18 | 18 | Policy evaluation: policy.assess_policy requires retention_until; some expected records are absent or only captured after cutoff. | Medium | High if seal/presence becomes retention proof | Presence often established; dates unavailable |
| G4: Support treatment and full-text scope | 7 | 15 | Policy evaluation: shared_context / belongs_only_to_subject missing; excerpt-only clean fields cannot prove full-text redaction. | Medium | Medium/high | PII or clean fields exist; required contextual facts incomplete |
| G5: Tombstone dependency cascade | 2 | 4 | Planning/policy: competition.best_effort_policy removes ALL tombstones when no RETAIN decision survives; prediction fallback then emits no violation plan. | Low/medium | Low for exposed fields, medium for compliance | Direct exposure is explicit; retained-reference relationship remains partly unresolved |

G6 (reference scope): case_07 contributes 3 additional steps. reviewed_images.catalog_attachment_observations joins evidence_46 to activity_4007, which explicitly states sole ownership of object_19. This is separate from support_001. Both witnesses predate the audit. Suppressing the object to improve exact scoring would reduce evidence completeness unless a newer absence or exclusion is found. Complexity low to audit, regression risk high if globally suppressed.

No observed omission is caused by CSV/JSON serialization. Historical identity recovery works on linked records; the recurring failure is lack of a subject-to-resource edge after identifiers are removed. Planner verification is already emitted for accepted compliant decisions: adding a generic verification loop would not recover resources that never reached policy.

## Evidence scope and limits

Non-overlapping conservative disposition of the 64 missing steps: **A = 3, B = 27, C = 34**. These are supported-step opportunity estimates, not measured gains from implemented changes.

**A — Clearly recoverable (3 steps).** evidence_51 explicitly shows tombstone_9178 in DELETED state with stable subject_reference and populated name/email/phone/hash. The subject requests removal of those fields. Preserve the stable reference and carry the exposed-PII finding, redaction and subsequent redaction check through best-effort planning even when an unrelated security retention decision is unresolved. The current gate discards this direct violation. This adds content in case_32 but does not close its absent account-ID or retention gaps.

**B — Policy interpretation or proof scope (27 steps).** Eleven security-presence checks have an observed subject-linked record but no supplied retention deadline (cases 11–17, 19, 22, 31–32). Three support violations (11,18,19; nine steps) lack explicit shared-context facts; the attachment in 13 (three steps) lacks sole-ownership confirmation. The three clean support checks in 26–28 show cleared requester fields, shared_context=true and text_has_subject_identifiers=false, but only a message_excerpt. An authoritative whole-message scan scope could recover these; treating all excerpts as complete is unjustified. The clean tombstone in 31 contributes one further verification gated by the uncertain retained relationship.

**C — Missing reconstructable facts (34 steps).** Twenty account-absence checks lack a grounded subject/resource association, seven anonymized analytics checks lack such lineage, and seven security checks have no admissible adequate witness. Cases 09,23,24,29,30 have their only matching security artifact captured after audit_at; cases 18 and 20 have no matching security artifact at all. Some G1 resource IDs occur only in workflow claims or post-cutoff files; an absent row in a global snapshot cannot invent which account ID belonged to a subject. No per-case number mapping, chronology pairing, record-order pairing or product-cohort matching is permissible.

Concrete source checks:

- evidence_54 contains only four real account resource IDs across primary/failover tables; account_001, account_002 and account_004 never appear in any evidence artifact. Identity resolution plus an empty scoped query can prove no matching identity, but cannot recover these exact account IDs. Workflow acknowledgements naming an account do not link it to the requester.
- evidence_92 has account_6440 and similar 404 rows with no subject selector; its anonymous analytics rows also lack identifiers. evidence_94 has analytics_9406 with lookup_key=null and cleared customer_reference/email/phone/hash. evidence_56 analytics_901 likewise has all identifiers null. These are real compliant payloads with missing ownership links.
- evidence_06 is captured 2026-09-18, later than case_09 audit_at 2026-09-16, despite individual log event times on September 16. Availability and observation time are separate gates.
- evidence_02 is captured September 17, later than the September 15 cutoffs of cases 23,24,29,30. Copying its security-presence rows backward would violate the time contract.
- evidence_03 explicitly gives IDENTIFIABLE support_864 and FOUND support_4218, but no shared-context or sole-owner predicate. evidence_01 support_9553 proves a direct-identifier match without conversational context. evidence_94 support_5569 exposes requester_email without shared-context metadata.
- evidence_51 contains both tombstone fields and security record presence for users 541/542, but no account_4857/account_8858 ID and no security retention date. An integrity seal proves neither retention applicability nor account absence.

The reference therefore exposes evidence-sufficiency tensions. Do not promise 32/32 exact answers by parser work alone, and do not weaken cutoff or provenance rules to reproduce unsupported expected tuples.

## Top five recommended improvements and implementation sequence

| Order | Generalized improvement | Public opportunity ceiling | Implementation / risk |
| --- | --- | --- | --- |
| 1 | Preserve independently proved violations when another resource policy fails | G5: 2 cases / 4 missing steps; strongest safe initial gain is 3 steps in case_32 | Stop blanket tombstone removal for exposed direct identifiers; retain unresolved relationship diagnostic. Low/medium effort; assert stable reference preservation. |
| 2 | Capture policy facts and proof scope from support artifacts | G4: 7 cases / 15 steps | Add typed shared-context, sole-owner and full-message scan provenance only when source states them. Medium effort; no SUPPORT_MESSAGE→shared by default. |
| 3 | Build a timestamped, provenance-bearing subject/resource/copy graph | G1+G2: 21 distinct cases / 27 steps | Reuse explicit catalog, lookup selector and earlier identifier-bearing records across formats; distinguish lineage from state. High effort/risk. Current public exact-ID links largely absent; ceiling is not guaranteed gain. |
| 4 | Separate observed security presence from retention applicability | G3: 18 cases / 18 steps | Inventory all deadlines and preserve unresolved policy obligations instead of losing resources. Medium effort; do not default indefinite retention or infer dates from seals. Eleven ambiguous and seven unavailable checks, so no unconditional gain claim. |
| 5 | Make evidence scope and sequence evaluation auditable | G6: 1 case / 3 reference extras; all 30 non-exact cases get clearer diagnostics | Keep supported extras; add evaluation-only matching by semantic identity, availability diagnostics and dependency-aware planning checks. Low/medium effort; no measured missing-step gain. |

Implement narrowly in that order after review. For each adapter/policy change, use synthetic counterexamples and public evidence-based tests: exposed and clean tombstones with unknown retention; shared vs subject-only attachments; truncated vs full support scan; cross-person identical resources/cohorts; 404 with and without prior ownership; logs observed before but captured after cutoff; primary/replica disagreement. Re-evaluate all 32 only after label-free prediction. Then regenerate all 518 into a separate file and inspect changes before replacing any candidate. Dependency ordering must stay data-flow/restore protection first and downstream before source; no independent ordering failure was observed here.

Expected initial safe benefit: 129→132 matching steps (68.39% recall), with 132→135 emitted steps, if all three A steps are added correctly. Exact-case count can remain 2/32 because case_32 still lacks two checks. B opportunities require explicit policy/scope resolution. A+B would be 159/193 (82.38%) content recall as a conditional ceiling; it is not a forecast. G1–G5 counts overlap in cases, not in step membership. Public status accuracy is already saturated and says little about plan completeness or hidden-set accuracy.

## Independent NOT_APPLICABLE audit

Reviewed all 518 complete request texts (375 distinct texts), including every first clause, all 17 deletion-authorizing clause forms and every distinct continuation. Classification used only authorization language and scope; evidence, identity availability, reported_status and existing predictions were excluded until comparison. The 508 authorization texts comprise 446 English requests and 62 multilingual requests: Portuguese 14, Korean 12, Spanish 12, Japanese 12, French 12. Each explicitly requests permanent account deletion; trailing identity review/confirmation clauses do not revoke it.

Result: 508 DELETION and 10 NON_DELETION; 0 disagreements with the candidate’s NOT_APPLICABLE boundary. No deactivation-only, hypothetical account-deletion condition, or mixed export-plus-deletion request occurs in the 518. “Please contact me if you need information to verify the request” occurs 64 times and conditions contact, not deletion. All distinct continuation forms were inspected; multilingual continuations request identity review and confirmation.

| Case | Intent-only result | Reason | Candidate |
| --- | --- | --- | --- |
| case_533 | NON_DELETION | Phone correction; explicitly keep account active | NOT_APPLICABLE |
| case_534 | NON_DELETION | Marketing opt-out; explicitly not requesting deletion | NOT_APPLICABLE |
| case_535 | NON_DELETION | Portable data export; keep account unchanged | NOT_APPLICABLE |
| case_536 | NON_DELETION | Login recovery; do not close account | NOT_APPLICABLE |
| case_537 | NON_DELETION | Name correction; preserve all records | NOT_APPLICABLE |
| case_538 | NON_DELETION | Marketing lists only; retain receipts/service messages | NOT_APPLICABLE |
| case_539 | NON_DELETION | Access/information only; expressly not erasure | NOT_APPLICABLE |
| case_540 | NON_DELETION | Invoice copy; preserve profile and purchases | NOT_APPLICABLE |
| case_541 | NON_DELETION | Email correction; continue service | NOT_APPLICABLE |
| case_542 | NON_DELETION | Access/copy only; expressly no deletion/change | NOT_APPLICABLE |

Access/export-only: 4 (535,539,540,542). Marketing opt-out: 2 (534,538). Corrections: 3 (533,537,541). Login recovery: 1 (536). Explicit account/record preservation or no erasure: 9; case_538 instead limits removal to marketing lists while preserving transactional communication. Account deactivation without deletion: 0. Hypothetical/conditional deletion: 0. Mixed deletion and non-deletion authorization: 0. These tags overlap and are not additional status categories. This is an independent semantic audit, not a second call to competition_intent. No missing evidence is used to assign NON_DELETION.

## All 32 public cases: mismatch ledger

Each missing entry below lists its reference number, full system/resource, operation/state, expected evidence (∅ means empty string), root-cause cluster and scope class. Reference numbers are diagnostic, never production rules. Omissions of future checks use ∅ as required. All unchanged matched steps keep their relative order.

### case_01

Status COMPLETE matches; predicted/reference steps 0/1. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | VERIFICATION | account_service/account_001 | VERIFY_RECORD_ABSENT / ABSENT | evidence_54 | G1 | C |

### case_02

Status COMPLETE matches; predicted/reference steps 0/1. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | VERIFICATION | account_service/account_002 | VERIFY_RECORD_ABSENT / ABSENT | evidence_54 | G1 | C |

### case_03

Status COMPLETE matches; predicted/reference steps 2/3. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 3 | VERIFICATION | analytics_platform/analytics_9406 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_94 | G2 | C |

### case_04

Status COMPLETE matches; predicted/reference steps 0/2. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | VERIFICATION | account_service/account_004 | VERIFY_RECORD_ABSENT / ABSENT | evidence_54 | G1 | C |
| 2 | VERIFICATION | analytics_platform/analytics_901 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_56 | G2 | C |

### case_05

Status INCOMPLETE matches; predicted/reference steps 3/3. Exact case.

### case_06

Status INCOMPLETE matches; predicted/reference steps 4/4. Exact case.

### case_07

Status INCOMPLETE matches; predicted/reference steps 6/4. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 3 | VERIFICATION | account_service/account_007 | VERIFY_RECORD_ABSENT / ABSENT | ∅ | G1 | C |

Extra actual #1: FINDING object_storage/object_19 REPORT_REMAINING_RECORD/PRESENT; evidence evidence_46. Root G6, evidence-supported reference-scope difference.
Extra actual #3: REMEDIATION object_storage/object_19 DELETE_RECORD/ABSENT; evidence ∅. Root G6, evidence-supported reference-scope difference.
Extra actual #5: VERIFICATION object_storage/object_19 VERIFY_RECORD_ABSENT/ABSENT; evidence ∅. Root G6, evidence-supported reference-scope difference.

### case_08

Status INCOMPLETE matches; predicted/reference steps 3/4. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 3 | VERIFICATION | account_service/account_008 | VERIFY_RECORD_ABSENT / ABSENT | ∅ | G1 | C |

### case_09

Status INCOMPLETE matches; predicted/reference steps 3/5. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 3 | VERIFICATION | account_service/account_3960 | VERIFY_RECORD_ABSENT / ABSENT | ∅ | G1 | C |
| 4 | VERIFICATION | security_service/audit_record_4902 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | C |

### case_10

Status INCOMPLETE matches; predicted/reference steps 3/4. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 3 | VERIFICATION | account_service/account_010 | VERIFY_RECORD_ABSENT / ABSENT | ∅ | G1 | C |

### case_11

Status INCOMPLETE matches; predicted/reference steps 10/14. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 3 | FINDING | support_platform/support_864 | REPORT_EXPOSED_PII / PRESENT | evidence_03 | G4 | B |
| 7 | REMEDIATION | support_platform/support_864 | REDACT_RECORD / REDACTED | ∅ | G4 | B |
| 11 | VERIFICATION | security_service/audit_record_9394 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | B |
| 12 | VERIFICATION | support_platform/support_864 | VERIFY_RECORD_REDACTED / REDACTED | ∅ | G4 | B |

Pipeline diagnostics: security_service/audit_record_9394: Security retention applicability not established at audit time; support_platform/support_864: Missing or invalid boolean fact: shared_context.

### case_12

Status INCOMPLETE matches; predicted/reference steps 4/5. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 5 | VERIFICATION | security_service/audit_record_2945 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | B |

Pipeline diagnostics: security_service/audit_record_2945: Security retention applicability not established at audit time.

### case_13

Status INCOMPLETE matches; predicted/reference steps 4/8. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 2 | FINDING | support_platform/support_4218 | REPORT_REMAINING_RECORD / PRESENT | evidence_03 | G4 | B |
| 4 | REMEDIATION | support_platform/support_4218 | DELETE_RECORD / ABSENT | ∅ | G4 | B |
| 7 | VERIFICATION | support_platform/support_4218 | VERIFY_RECORD_ABSENT / ABSENT | ∅ | G4 | B |
| 8 | VERIFICATION | security_service/audit_record_4816 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | B |

Pipeline diagnostics: security_service/audit_record_4816: Security retention applicability not established at audit time; support_platform/support_4218: Missing or invalid boolean fact: belongs_only_to_subject.

### case_14

Status INCOMPLETE matches; predicted/reference steps 4/5. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 4 | VERIFICATION | security_service/audit_record_987 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | B |

Pipeline diagnostics: security_service/audit_record_987: Security retention applicability not established at audit time.

### case_15

Status INCOMPLETE matches; predicted/reference steps 4/5. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 4 | VERIFICATION | security_service/audit_record_1596 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | B |

Pipeline diagnostics: security_service/audit_record_1596: Security retention applicability not established at audit time.

### case_16

Status INCOMPLETE matches; predicted/reference steps 6/7. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 7 | VERIFICATION | security_service/audit_record_9528 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | B |

Pipeline diagnostics: security_service/audit_record_9528: Security retention applicability not established at audit time.

### case_17

Status INCOMPLETE matches; predicted/reference steps 4/5. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 4 | VERIFICATION | security_service/audit_record_1797 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | B |

Pipeline diagnostics: activity/account_6523: Post-snapshot state-changing claim requires newer readback; activity/tombstone_17: Subject-linked activity resource lacks scoped evidence; security_service/audit_record_1797: Security retention applicability not established at audit time.

### case_18

Status INCOMPLETE matches; predicted/reference steps 9/14. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 3 | FINDING | support_platform/support_5569 | REPORT_EXPOSED_PII / PRESENT | evidence_94 | G4 | B |
| 7 | REMEDIATION | support_platform/support_5569 | REDACT_RECORD / REDACTED | ∅ | G4 | B |
| 9 | VERIFICATION | account_service/account_5521 | VERIFY_RECORD_ABSENT / ABSENT | ∅ | G1 | C |
| 11 | VERIFICATION | security_service/audit_record_6645 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | C |
| 12 | VERIFICATION | support_platform/support_5569 | VERIFY_RECORD_REDACTED / REDACTED | ∅ | G4 | B |

Pipeline diagnostics: support_platform/support_5569: Missing or invalid boolean fact: shared_context.

### case_19

Status INCOMPLETE matches; predicted/reference steps 4/8. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 2 | FINDING | support_platform/support_9553 | REPORT_EXPOSED_PII / PRESENT | evidence_01 | G4 | B |
| 4 | REMEDIATION | support_platform/support_9553 | REDACT_RECORD / REDACTED | ∅ | G4 | B |
| 7 | VERIFICATION | security_service/audit_record_6793 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | B |
| 8 | VERIFICATION | support_platform/support_9553 | VERIFY_RECORD_REDACTED / REDACTED | ∅ | G4 | B |

Pipeline diagnostics: security_service/audit_record_6793: Security retention applicability not established at audit time; support_platform/support_9553: Missing or invalid boolean fact: shared_context.

### case_20

Status INCOMPLETE matches; predicted/reference steps 6/8. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 5 | VERIFICATION | account_service/account_5037 | VERIFY_RECORD_ABSENT / ABSENT | ∅ | G1 | C |
| 7 | VERIFICATION | security_service/audit_record_5569 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | C |

### case_21

Status COMPLETE matches; predicted/reference steps 1/3. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | VERIFICATION | account_service/account_6440 | VERIFY_RECORD_ABSENT / ABSENT | evidence_92 | G1 | C |
| 3 | VERIFICATION | analytics_platform/analytics_5335 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_92 | G2 | C |

### case_22

Status INCOMPLETE matches; predicted/reference steps 6/8. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 5 | VERIFICATION | account_service/account_4990 | VERIFY_RECORD_ABSENT / ABSENT | ∅ | G1 | C |
| 7 | VERIFICATION | security_service/audit_record_3482 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | B |

Pipeline diagnostics: security_service/audit_record_3482: Security retention applicability not established at audit time.

### case_23

Status INCOMPLETE matches; predicted/reference steps 6/8. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 5 | VERIFICATION | account_service/account_410 | VERIFY_RECORD_ABSENT / ABSENT | ∅ | G1 | C |
| 8 | VERIFICATION | security_service/audit_record_4128 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | C |

### case_24

Status INCOMPLETE matches; predicted/reference steps 6/7. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 7 | VERIFICATION | security_service/audit_record_7095 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | C |

### case_25

Status COMPLETE matches; predicted/reference steps 1/3. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | VERIFICATION | account_service/account_3136 | VERIFY_RECORD_ABSENT / ABSENT | evidence_92 | G1 | C |
| 3 | VERIFICATION | analytics_platform/analytics_1895 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_92 | G2 | C |

### case_26

Status COMPLETE matches; predicted/reference steps 3/6. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | VERIFICATION | account_service/account_5684 | VERIFY_RECORD_ABSENT / ABSENT | evidence_92 | G1 | C |
| 3 | VERIFICATION | support_platform/support_4715 | VERIFY_RECORD_REDACTED / REDACTED | evidence_92 | G4 | B |
| 4 | VERIFICATION | analytics_platform/analytics_4566 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_92 | G2 | C |

Pipeline diagnostics: support_platform/support_4715: Missing or invalid boolean fact: text_scan_complete.

### case_27

Status COMPLETE matches; predicted/reference steps 3/6. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | VERIFICATION | account_service/account_3866 | VERIFY_RECORD_ABSENT / ABSENT | evidence_92 | G1 | C |
| 3 | VERIFICATION | support_platform/support_4707 | VERIFY_RECORD_REDACTED / REDACTED | evidence_92 | G4 | B |
| 4 | VERIFICATION | analytics_platform/analytics_4574 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_92 | G2 | C |

Pipeline diagnostics: support_platform/support_4707: Missing or invalid boolean fact: text_scan_complete.

### case_28

Status COMPLETE matches; predicted/reference steps 3/6. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | VERIFICATION | account_service/account_5482 | VERIFY_RECORD_ABSENT / ABSENT | evidence_92 | G1 | C |
| 3 | VERIFICATION | support_platform/support_2351 | VERIFY_RECORD_REDACTED / REDACTED | evidence_92 | G4 | B |
| 4 | VERIFICATION | analytics_platform/analytics_6077 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_92 | G2 | C |

Pipeline diagnostics: support_platform/support_2351: Missing or invalid boolean fact: text_scan_complete.

### case_29

Status INCOMPLETE matches; predicted/reference steps 12/14. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 9 | VERIFICATION | account_service/account_7012 | VERIFY_RECORD_ABSENT / ABSENT | ∅ | G1 | C |
| 11 | VERIFICATION | security_service/audit_record_3954 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | C |

### case_30

Status INCOMPLETE matches; predicted/reference steps 12/14. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 9 | VERIFICATION | account_service/account_4163 | VERIFY_RECORD_ABSENT / ABSENT | ∅ | G1 | C |
| 11 | VERIFICATION | security_service/audit_record_1707 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | C |

### case_31

Status COMPLETE matches; predicted/reference steps 0/3. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | VERIFICATION | account_service/account_4857 | VERIFY_RECORD_ABSENT / ABSENT | evidence_51 | G1 | C |
| 2 | VERIFICATION | security_service/audit_record_6909 | VERIFY_RECORD_PRESENT / PRESENT | evidence_51 | G3 | B |
| 3 | VERIFICATION | identity_service/tombstone_440 | VERIFY_RECORD_REDACTED / REDACTED | evidence_51 | G5 | B |

Pipeline diagnostics: identity_service/tombstone_440: Tombstone reference has no supported retained-record relationship; security_service/audit_record_6909: Security retention applicability not established at audit time.

### case_32

Status INCOMPLETE matches; predicted/reference steps 0/5. Not exact.

| Ref no. | Phase | System/resource | Operation / state | Evidence | Root | Scope |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | FINDING | identity_service/tombstone_9178 | REPORT_EXPOSED_PII / PRESENT | evidence_51 | G5 | A |
| 2 | REMEDIATION | identity_service/tombstone_9178 | REDACT_RECORD / REDACTED | ∅ | G5 | A |
| 3 | VERIFICATION | account_service/account_8858 | VERIFY_RECORD_ABSENT / ABSENT | ∅ | G1 | C |
| 4 | VERIFICATION | security_service/audit_record_7068 | VERIFY_RECORD_PRESENT / PRESENT | ∅ | G3 | B |
| 5 | VERIFICATION | identity_service/tombstone_9178 | VERIFY_RECORD_REDACTED / REDACTED | ∅ | G5 | A |

Pipeline diagnostics: identity_service/tombstone_9178: Tombstone reference has no supported retained-record relationship; security_service/audit_record_7068: Security retention applicability not established at audit time.

## Reproduction and checks

Run from repository root (read-only inputs; outputs under /tmp):

```bash
python3 -m unittest discover -s tests -q
python3 code/main.py --all --requests dataset/sample_deletion_requests.csv --mode prediction --output /tmp/forensic-public.csv --diagnostics /tmp/forensic-public.json
cmp artifacts/prediction-benchmark/predictions.csv /tmp/forensic-public.csv
python3 code/tools/validate_candidate.py
```

Results: 128 existing tests pass; public predictions reproduce byte-for-byte. Candidate validator confirms 518 unique sorted request IDs, zero structural failures and zero citation/resource provenance failures; uncertainty remains 144 statuses and 302 incomplete/unproved plans. Candidate SHA-256 before/after is the value above. No runtime model calls were made. Only this analysis and the mandatory append-only log are committed. No code, dataset, candidate or package changes.

## Appendix: 518-request intent-only ledger

D = explicit deletion authorization; N = non-deletion. Every row was reviewed; the compact English entry applies only after confirming the entire continuation has no revocation or scope restriction. Candidate comparison is the binary NOT_APPLICABLE boundary, not an independent COMPLETE/INCOMPLETE judgment.

| Case | Language | Intent | Candidate | Boundary agrees |
| --- | --- | --- | --- | --- |
| case_33 | English | D | INCOMPLETE | Yes |
| case_34 | English | D | INCOMPLETE | Yes |
| case_35 | English | D | INCOMPLETE | Yes |
| case_36 | English | D | INCOMPLETE | Yes |
| case_37 | English | D | INCOMPLETE | Yes |
| case_38 | English | D | INCOMPLETE | Yes |
| case_39 | English | D | INCOMPLETE | Yes |
| case_40 | English | D | INCOMPLETE | Yes |
| case_41 | English | D | COMPLETE | Yes |
| case_42 | English | D | INCOMPLETE | Yes |
| case_43 | English | D | INCOMPLETE | Yes |
| case_44 | English | D | COMPLETE | Yes |
| case_45 | English | D | COMPLETE | Yes |
| case_46 | English | D | COMPLETE | Yes |
| case_47 | English | D | INCOMPLETE | Yes |
| case_48 | English | D | INCOMPLETE | Yes |
| case_49 | English | D | INCOMPLETE | Yes |
| case_50 | English | D | INCOMPLETE | Yes |
| case_51 | English | D | COMPLETE | Yes |
| case_52 | English | D | INCOMPLETE | Yes |
| case_53 | English | D | INCOMPLETE | Yes |
| case_54 | Portuguese | D | INCOMPLETE | Yes |
| case_55 | English | D | COMPLETE | Yes |
| case_56 | English | D | INCOMPLETE | Yes |
| case_57 | English | D | COMPLETE | Yes |
| case_58 | English | D | COMPLETE | Yes |
| case_59 | English | D | COMPLETE | Yes |
| case_60 | English | D | COMPLETE | Yes |
| case_61 | English | D | INCOMPLETE | Yes |
| case_62 | English | D | INCOMPLETE | Yes |
| case_63 | English | D | COMPLETE | Yes |
| case_64 | English | D | COMPLETE | Yes |
| case_65 | English | D | INCOMPLETE | Yes |
| case_66 | Korean | D | INCOMPLETE | Yes |
| case_67 | English | D | INCOMPLETE | Yes |
| case_68 | English | D | INCOMPLETE | Yes |
| case_69 | Spanish | D | COMPLETE | Yes |
| case_70 | English | D | COMPLETE | Yes |
| case_71 | English | D | INCOMPLETE | Yes |
| case_72 | English | D | INCOMPLETE | Yes |
| case_73 | English | D | COMPLETE | Yes |
| case_74 | English | D | INCOMPLETE | Yes |
| case_75 | English | D | INCOMPLETE | Yes |
| case_76 | English | D | INCOMPLETE | Yes |
| case_77 | English | D | COMPLETE | Yes |
| case_78 | Japanese | D | INCOMPLETE | Yes |
| case_79 | English | D | COMPLETE | Yes |
| case_80 | English | D | COMPLETE | Yes |
| case_81 | English | D | COMPLETE | Yes |
| case_82 | English | D | COMPLETE | Yes |
| case_83 | English | D | COMPLETE | Yes |
| case_84 | French | D | COMPLETE | Yes |
| case_85 | English | D | INCOMPLETE | Yes |
| case_86 | English | D | COMPLETE | Yes |
| case_87 | English | D | INCOMPLETE | Yes |
| case_88 | English | D | INCOMPLETE | Yes |
| case_89 | English | D | INCOMPLETE | Yes |
| case_90 | English | D | INCOMPLETE | Yes |
| case_91 | English | D | INCOMPLETE | Yes |
| case_92 | English | D | INCOMPLETE | Yes |
| case_93 | Portuguese | D | INCOMPLETE | Yes |
| case_94 | English | D | INCOMPLETE | Yes |
| case_95 | English | D | INCOMPLETE | Yes |
| case_96 | English | D | INCOMPLETE | Yes |
| case_97 | English | D | COMPLETE | Yes |
| case_98 | English | D | INCOMPLETE | Yes |
| case_99 | English | D | INCOMPLETE | Yes |
| case_100 | English | D | INCOMPLETE | Yes |
| case_101 | English | D | INCOMPLETE | Yes |
| case_102 | English | D | INCOMPLETE | Yes |
| case_103 | English | D | COMPLETE | Yes |
| case_104 | English | D | INCOMPLETE | Yes |
| case_105 | Korean | D | INCOMPLETE | Yes |
| case_106 | English | D | INCOMPLETE | Yes |
| case_107 | English | D | COMPLETE | Yes |
| case_108 | Spanish | D | COMPLETE | Yes |
| case_109 | English | D | INCOMPLETE | Yes |
| case_110 | English | D | INCOMPLETE | Yes |
| case_111 | English | D | COMPLETE | Yes |
| case_112 | English | D | COMPLETE | Yes |
| case_113 | English | D | COMPLETE | Yes |
| case_114 | English | D | INCOMPLETE | Yes |
| case_115 | English | D | INCOMPLETE | Yes |
| case_116 | English | D | INCOMPLETE | Yes |
| case_117 | Japanese | D | COMPLETE | Yes |
| case_118 | English | D | INCOMPLETE | Yes |
| case_119 | English | D | INCOMPLETE | Yes |
| case_120 | English | D | INCOMPLETE | Yes |
| case_121 | English | D | COMPLETE | Yes |
| case_122 | English | D | INCOMPLETE | Yes |
| case_123 | French | D | INCOMPLETE | Yes |
| case_124 | English | D | INCOMPLETE | Yes |
| case_125 | English | D | INCOMPLETE | Yes |
| case_126 | English | D | COMPLETE | Yes |
| case_127 | English | D | COMPLETE | Yes |
| case_128 | English | D | INCOMPLETE | Yes |
| case_129 | English | D | INCOMPLETE | Yes |
| case_130 | English | D | INCOMPLETE | Yes |
| case_131 | English | D | INCOMPLETE | Yes |
| case_132 | Portuguese | D | INCOMPLETE | Yes |
| case_133 | English | D | INCOMPLETE | Yes |
| case_134 | English | D | INCOMPLETE | Yes |
| case_135 | English | D | COMPLETE | Yes |
| case_136 | English | D | INCOMPLETE | Yes |
| case_137 | English | D | COMPLETE | Yes |
| case_138 | English | D | INCOMPLETE | Yes |
| case_139 | English | D | INCOMPLETE | Yes |
| case_140 | English | D | INCOMPLETE | Yes |
| case_141 | English | D | INCOMPLETE | Yes |
| case_142 | English | D | INCOMPLETE | Yes |
| case_143 | English | D | INCOMPLETE | Yes |
| case_144 | Korean | D | INCOMPLETE | Yes |
| case_145 | English | D | INCOMPLETE | Yes |
| case_146 | English | D | INCOMPLETE | Yes |
| case_147 | Spanish | D | INCOMPLETE | Yes |
| case_148 | English | D | INCOMPLETE | Yes |
| case_149 | English | D | INCOMPLETE | Yes |
| case_150 | English | D | COMPLETE | Yes |
| case_151 | English | D | COMPLETE | Yes |
| case_152 | English | D | COMPLETE | Yes |
| case_153 | English | D | INCOMPLETE | Yes |
| case_154 | English | D | INCOMPLETE | Yes |
| case_155 | English | D | COMPLETE | Yes |
| case_156 | Japanese | D | INCOMPLETE | Yes |
| case_157 | English | D | COMPLETE | Yes |
| case_158 | English | D | INCOMPLETE | Yes |
| case_159 | English | D | INCOMPLETE | Yes |
| case_160 | English | D | COMPLETE | Yes |
| case_161 | English | D | INCOMPLETE | Yes |
| case_162 | French | D | COMPLETE | Yes |
| case_163 | English | D | INCOMPLETE | Yes |
| case_164 | English | D | COMPLETE | Yes |
| case_165 | English | D | INCOMPLETE | Yes |
| case_166 | English | D | INCOMPLETE | Yes |
| case_167 | English | D | COMPLETE | Yes |
| case_168 | English | D | INCOMPLETE | Yes |
| case_169 | English | D | INCOMPLETE | Yes |
| case_170 | English | D | COMPLETE | Yes |
| case_171 | Portuguese | D | INCOMPLETE | Yes |
| case_172 | English | D | INCOMPLETE | Yes |
| case_173 | English | D | INCOMPLETE | Yes |
| case_174 | English | D | INCOMPLETE | Yes |
| case_175 | English | D | COMPLETE | Yes |
| case_176 | English | D | INCOMPLETE | Yes |
| case_177 | English | D | INCOMPLETE | Yes |
| case_178 | English | D | COMPLETE | Yes |
| case_179 | English | D | INCOMPLETE | Yes |
| case_180 | English | D | INCOMPLETE | Yes |
| case_181 | English | D | INCOMPLETE | Yes |
| case_182 | English | D | INCOMPLETE | Yes |
| case_183 | Korean | D | COMPLETE | Yes |
| case_184 | English | D | INCOMPLETE | Yes |
| case_185 | English | D | INCOMPLETE | Yes |
| case_186 | Spanish | D | INCOMPLETE | Yes |
| case_187 | English | D | INCOMPLETE | Yes |
| case_188 | English | D | INCOMPLETE | Yes |
| case_189 | English | D | INCOMPLETE | Yes |
| case_190 | English | D | COMPLETE | Yes |
| case_191 | English | D | COMPLETE | Yes |
| case_192 | English | D | INCOMPLETE | Yes |
| case_193 | English | D | COMPLETE | Yes |
| case_194 | English | D | INCOMPLETE | Yes |
| case_195 | Japanese | D | COMPLETE | Yes |
| case_196 | English | D | COMPLETE | Yes |
| case_197 | English | D | INCOMPLETE | Yes |
| case_198 | English | D | INCOMPLETE | Yes |
| case_199 | English | D | INCOMPLETE | Yes |
| case_200 | English | D | INCOMPLETE | Yes |
| case_201 | French | D | INCOMPLETE | Yes |
| case_202 | English | D | COMPLETE | Yes |
| case_203 | English | D | INCOMPLETE | Yes |
| case_204 | English | D | COMPLETE | Yes |
| case_205 | English | D | INCOMPLETE | Yes |
| case_206 | English | D | COMPLETE | Yes |
| case_207 | English | D | INCOMPLETE | Yes |
| case_208 | English | D | INCOMPLETE | Yes |
| case_209 | English | D | INCOMPLETE | Yes |
| case_210 | Portuguese | D | INCOMPLETE | Yes |
| case_211 | English | D | INCOMPLETE | Yes |
| case_212 | English | D | INCOMPLETE | Yes |
| case_213 | English | D | COMPLETE | Yes |
| case_214 | English | D | INCOMPLETE | Yes |
| case_215 | English | D | COMPLETE | Yes |
| case_216 | English | D | INCOMPLETE | Yes |
| case_217 | English | D | INCOMPLETE | Yes |
| case_218 | English | D | COMPLETE | Yes |
| case_219 | English | D | COMPLETE | Yes |
| case_220 | English | D | INCOMPLETE | Yes |
| case_221 | English | D | COMPLETE | Yes |
| case_222 | Korean | D | INCOMPLETE | Yes |
| case_223 | English | D | INCOMPLETE | Yes |
| case_224 | English | D | INCOMPLETE | Yes |
| case_225 | Spanish | D | COMPLETE | Yes |
| case_226 | English | D | COMPLETE | Yes |
| case_227 | English | D | INCOMPLETE | Yes |
| case_228 | English | D | INCOMPLETE | Yes |
| case_229 | English | D | INCOMPLETE | Yes |
| case_230 | English | D | INCOMPLETE | Yes |
| case_231 | English | D | COMPLETE | Yes |
| case_232 | English | D | INCOMPLETE | Yes |
| case_233 | English | D | COMPLETE | Yes |
| case_234 | Japanese | D | INCOMPLETE | Yes |
| case_235 | English | D | COMPLETE | Yes |
| case_236 | English | D | INCOMPLETE | Yes |
| case_237 | English | D | INCOMPLETE | Yes |
| case_238 | English | D | COMPLETE | Yes |
| case_239 | English | D | COMPLETE | Yes |
| case_240 | French | D | INCOMPLETE | Yes |
| case_241 | English | D | INCOMPLETE | Yes |
| case_242 | English | D | INCOMPLETE | Yes |
| case_243 | English | D | COMPLETE | Yes |
| case_244 | English | D | COMPLETE | Yes |
| case_245 | English | D | INCOMPLETE | Yes |
| case_246 | English | D | INCOMPLETE | Yes |
| case_247 | English | D | INCOMPLETE | Yes |
| case_248 | English | D | INCOMPLETE | Yes |
| case_249 | Portuguese | D | INCOMPLETE | Yes |
| case_250 | English | D | INCOMPLETE | Yes |
| case_251 | English | D | INCOMPLETE | Yes |
| case_252 | English | D | INCOMPLETE | Yes |
| case_253 | English | D | COMPLETE | Yes |
| case_254 | English | D | INCOMPLETE | Yes |
| case_255 | English | D | INCOMPLETE | Yes |
| case_256 | English | D | INCOMPLETE | Yes |
| case_257 | English | D | COMPLETE | Yes |
| case_258 | English | D | INCOMPLETE | Yes |
| case_259 | English | D | INCOMPLETE | Yes |
| case_260 | English | D | COMPLETE | Yes |
| case_261 | Korean | D | INCOMPLETE | Yes |
| case_262 | English | D | INCOMPLETE | Yes |
| case_263 | English | D | INCOMPLETE | Yes |
| case_264 | Spanish | D | COMPLETE | Yes |
| case_265 | English | D | COMPLETE | Yes |
| case_266 | English | D | INCOMPLETE | Yes |
| case_267 | English | D | COMPLETE | Yes |
| case_268 | English | D | INCOMPLETE | Yes |
| case_269 | English | D | INCOMPLETE | Yes |
| case_270 | English | D | INCOMPLETE | Yes |
| case_271 | English | D | INCOMPLETE | Yes |
| case_272 | English | D | INCOMPLETE | Yes |
| case_273 | Japanese | D | INCOMPLETE | Yes |
| case_274 | English | D | COMPLETE | Yes |
| case_275 | English | D | INCOMPLETE | Yes |
| case_276 | English | D | COMPLETE | Yes |
| case_277 | English | D | COMPLETE | Yes |
| case_278 | English | D | INCOMPLETE | Yes |
| case_279 | French | D | INCOMPLETE | Yes |
| case_280 | English | D | INCOMPLETE | Yes |
| case_281 | English | D | INCOMPLETE | Yes |
| case_282 | English | D | INCOMPLETE | Yes |
| case_283 | English | D | COMPLETE | Yes |
| case_284 | English | D | INCOMPLETE | Yes |
| case_285 | English | D | INCOMPLETE | Yes |
| case_286 | English | D | COMPLETE | Yes |
| case_287 | English | D | INCOMPLETE | Yes |
| case_288 | Portuguese | D | INCOMPLETE | Yes |
| case_289 | English | D | INCOMPLETE | Yes |
| case_290 | English | D | INCOMPLETE | Yes |
| case_291 | English | D | INCOMPLETE | Yes |
| case_292 | English | D | COMPLETE | Yes |
| case_293 | English | D | INCOMPLETE | Yes |
| case_294 | English | D | COMPLETE | Yes |
| case_295 | English | D | COMPLETE | Yes |
| case_296 | English | D | INCOMPLETE | Yes |
| case_297 | English | D | COMPLETE | Yes |
| case_298 | English | D | INCOMPLETE | Yes |
| case_299 | English | D | COMPLETE | Yes |
| case_300 | Korean | D | INCOMPLETE | Yes |
| case_301 | English | D | INCOMPLETE | Yes |
| case_302 | English | D | INCOMPLETE | Yes |
| case_303 | Spanish | D | INCOMPLETE | Yes |
| case_304 | English | D | COMPLETE | Yes |
| case_305 | English | D | INCOMPLETE | Yes |
| case_306 | English | D | INCOMPLETE | Yes |
| case_307 | English | D | INCOMPLETE | Yes |
| case_308 | English | D | COMPLETE | Yes |
| case_309 | English | D | COMPLETE | Yes |
| case_310 | English | D | INCOMPLETE | Yes |
| case_311 | English | D | INCOMPLETE | Yes |
| case_312 | Japanese | D | INCOMPLETE | Yes |
| case_313 | English | D | COMPLETE | Yes |
| case_314 | English | D | COMPLETE | Yes |
| case_315 | English | D | INCOMPLETE | Yes |
| case_316 | English | D | INCOMPLETE | Yes |
| case_317 | English | D | INCOMPLETE | Yes |
| case_318 | French | D | INCOMPLETE | Yes |
| case_319 | English | D | COMPLETE | Yes |
| case_320 | English | D | INCOMPLETE | Yes |
| case_321 | English | D | INCOMPLETE | Yes |
| case_322 | English | D | COMPLETE | Yes |
| case_323 | English | D | COMPLETE | Yes |
| case_324 | English | D | COMPLETE | Yes |
| case_325 | English | D | INCOMPLETE | Yes |
| case_326 | English | D | COMPLETE | Yes |
| case_327 | Portuguese | D | COMPLETE | Yes |
| case_328 | English | D | INCOMPLETE | Yes |
| case_329 | English | D | INCOMPLETE | Yes |
| case_330 | English | D | INCOMPLETE | Yes |
| case_331 | English | D | COMPLETE | Yes |
| case_332 | English | D | INCOMPLETE | Yes |
| case_333 | English | D | INCOMPLETE | Yes |
| case_334 | English | D | INCOMPLETE | Yes |
| case_335 | English | D | COMPLETE | Yes |
| case_336 | English | D | COMPLETE | Yes |
| case_337 | English | D | INCOMPLETE | Yes |
| case_338 | English | D | INCOMPLETE | Yes |
| case_339 | Korean | D | COMPLETE | Yes |
| case_340 | English | D | INCOMPLETE | Yes |
| case_341 | English | D | INCOMPLETE | Yes |
| case_342 | Spanish | D | INCOMPLETE | Yes |
| case_343 | English | D | COMPLETE | Yes |
| case_344 | English | D | INCOMPLETE | Yes |
| case_345 | English | D | COMPLETE | Yes |
| case_346 | English | D | COMPLETE | Yes |
| case_347 | English | D | INCOMPLETE | Yes |
| case_348 | English | D | INCOMPLETE | Yes |
| case_349 | English | D | INCOMPLETE | Yes |
| case_350 | English | D | INCOMPLETE | Yes |
| case_351 | Japanese | D | COMPLETE | Yes |
| case_352 | English | D | INCOMPLETE | Yes |
| case_353 | English | D | INCOMPLETE | Yes |
| case_354 | English | D | COMPLETE | Yes |
| case_355 | English | D | INCOMPLETE | Yes |
| case_356 | English | D | INCOMPLETE | Yes |
| case_357 | French | D | INCOMPLETE | Yes |
| case_358 | English | D | INCOMPLETE | Yes |
| case_359 | English | D | INCOMPLETE | Yes |
| case_360 | English | D | INCOMPLETE | Yes |
| case_361 | English | D | INCOMPLETE | Yes |
| case_362 | English | D | COMPLETE | Yes |
| case_363 | English | D | INCOMPLETE | Yes |
| case_364 | English | D | INCOMPLETE | Yes |
| case_365 | English | D | INCOMPLETE | Yes |
| case_366 | Portuguese | D | INCOMPLETE | Yes |
| case_367 | English | D | INCOMPLETE | Yes |
| case_368 | English | D | INCOMPLETE | Yes |
| case_369 | English | D | COMPLETE | Yes |
| case_370 | English | D | INCOMPLETE | Yes |
| case_371 | English | D | INCOMPLETE | Yes |
| case_372 | English | D | INCOMPLETE | Yes |
| case_373 | English | D | INCOMPLETE | Yes |
| case_374 | English | D | COMPLETE | Yes |
| case_375 | English | D | COMPLETE | Yes |
| case_376 | English | D | INCOMPLETE | Yes |
| case_377 | English | D | INCOMPLETE | Yes |
| case_378 | Korean | D | COMPLETE | Yes |
| case_379 | English | D | INCOMPLETE | Yes |
| case_380 | English | D | COMPLETE | Yes |
| case_381 | Spanish | D | INCOMPLETE | Yes |
| case_382 | English | D | INCOMPLETE | Yes |
| case_383 | English | D | COMPLETE | Yes |
| case_384 | English | D | INCOMPLETE | Yes |
| case_385 | English | D | INCOMPLETE | Yes |
| case_386 | English | D | INCOMPLETE | Yes |
| case_387 | English | D | INCOMPLETE | Yes |
| case_388 | English | D | INCOMPLETE | Yes |
| case_389 | English | D | INCOMPLETE | Yes |
| case_390 | Japanese | D | COMPLETE | Yes |
| case_391 | English | D | INCOMPLETE | Yes |
| case_392 | English | D | COMPLETE | Yes |
| case_393 | English | D | COMPLETE | Yes |
| case_394 | English | D | INCOMPLETE | Yes |
| case_395 | English | D | COMPLETE | Yes |
| case_396 | French | D | INCOMPLETE | Yes |
| case_397 | English | D | INCOMPLETE | Yes |
| case_398 | English | D | COMPLETE | Yes |
| case_399 | English | D | INCOMPLETE | Yes |
| case_400 | English | D | INCOMPLETE | Yes |
| case_401 | English | D | INCOMPLETE | Yes |
| case_402 | English | D | INCOMPLETE | Yes |
| case_403 | English | D | COMPLETE | Yes |
| case_404 | English | D | INCOMPLETE | Yes |
| case_405 | Portuguese | D | INCOMPLETE | Yes |
| case_406 | English | D | INCOMPLETE | Yes |
| case_407 | English | D | INCOMPLETE | Yes |
| case_408 | English | D | COMPLETE | Yes |
| case_409 | English | D | COMPLETE | Yes |
| case_410 | English | D | INCOMPLETE | Yes |
| case_411 | English | D | COMPLETE | Yes |
| case_412 | English | D | COMPLETE | Yes |
| case_413 | English | D | INCOMPLETE | Yes |
| case_414 | English | D | INCOMPLETE | Yes |
| case_415 | English | D | INCOMPLETE | Yes |
| case_416 | English | D | INCOMPLETE | Yes |
| case_417 | Korean | D | INCOMPLETE | Yes |
| case_418 | English | D | INCOMPLETE | Yes |
| case_419 | English | D | INCOMPLETE | Yes |
| case_420 | Spanish | D | INCOMPLETE | Yes |
| case_421 | English | D | INCOMPLETE | Yes |
| case_422 | English | D | INCOMPLETE | Yes |
| case_423 | English | D | COMPLETE | Yes |
| case_424 | English | D | COMPLETE | Yes |
| case_425 | English | D | INCOMPLETE | Yes |
| case_426 | English | D | INCOMPLETE | Yes |
| case_427 | English | D | COMPLETE | Yes |
| case_428 | English | D | INCOMPLETE | Yes |
| case_429 | Japanese | D | INCOMPLETE | Yes |
| case_430 | English | D | COMPLETE | Yes |
| case_431 | English | D | INCOMPLETE | Yes |
| case_432 | English | D | INCOMPLETE | Yes |
| case_433 | English | D | INCOMPLETE | Yes |
| case_434 | English | D | INCOMPLETE | Yes |
| case_435 | French | D | INCOMPLETE | Yes |
| case_436 | English | D | INCOMPLETE | Yes |
| case_437 | English | D | INCOMPLETE | Yes |
| case_438 | English | D | INCOMPLETE | Yes |
| case_439 | English | D | INCOMPLETE | Yes |
| case_440 | English | D | INCOMPLETE | Yes |
| case_441 | English | D | INCOMPLETE | Yes |
| case_442 | English | D | INCOMPLETE | Yes |
| case_443 | English | D | INCOMPLETE | Yes |
| case_444 | Portuguese | D | INCOMPLETE | Yes |
| case_445 | English | D | INCOMPLETE | Yes |
| case_446 | English | D | INCOMPLETE | Yes |
| case_447 | English | D | INCOMPLETE | Yes |
| case_448 | English | D | COMPLETE | Yes |
| case_449 | English | D | INCOMPLETE | Yes |
| case_450 | English | D | INCOMPLETE | Yes |
| case_451 | English | D | INCOMPLETE | Yes |
| case_452 | English | D | COMPLETE | Yes |
| case_453 | English | D | INCOMPLETE | Yes |
| case_454 | English | D | INCOMPLETE | Yes |
| case_455 | English | D | INCOMPLETE | Yes |
| case_456 | Korean | D | COMPLETE | Yes |
| case_457 | English | D | COMPLETE | Yes |
| case_458 | English | D | COMPLETE | Yes |
| case_459 | Spanish | D | INCOMPLETE | Yes |
| case_460 | English | D | COMPLETE | Yes |
| case_461 | English | D | INCOMPLETE | Yes |
| case_462 | English | D | COMPLETE | Yes |
| case_463 | English | D | COMPLETE | Yes |
| case_464 | English | D | COMPLETE | Yes |
| case_465 | English | D | INCOMPLETE | Yes |
| case_466 | English | D | INCOMPLETE | Yes |
| case_467 | English | D | COMPLETE | Yes |
| case_468 | Japanese | D | INCOMPLETE | Yes |
| case_469 | English | D | INCOMPLETE | Yes |
| case_470 | English | D | COMPLETE | Yes |
| case_471 | English | D | INCOMPLETE | Yes |
| case_472 | English | D | INCOMPLETE | Yes |
| case_473 | English | D | INCOMPLETE | Yes |
| case_474 | French | D | INCOMPLETE | Yes |
| case_475 | English | D | INCOMPLETE | Yes |
| case_476 | English | D | INCOMPLETE | Yes |
| case_477 | English | D | INCOMPLETE | Yes |
| case_478 | English | D | INCOMPLETE | Yes |
| case_479 | English | D | COMPLETE | Yes |
| case_480 | English | D | COMPLETE | Yes |
| case_481 | English | D | INCOMPLETE | Yes |
| case_482 | English | D | INCOMPLETE | Yes |
| case_483 | Portuguese | D | INCOMPLETE | Yes |
| case_484 | English | D | INCOMPLETE | Yes |
| case_485 | English | D | INCOMPLETE | Yes |
| case_486 | English | D | COMPLETE | Yes |
| case_487 | English | D | INCOMPLETE | Yes |
| case_488 | English | D | INCOMPLETE | Yes |
| case_489 | English | D | INCOMPLETE | Yes |
| case_490 | English | D | INCOMPLETE | Yes |
| case_491 | English | D | COMPLETE | Yes |
| case_492 | English | D | INCOMPLETE | Yes |
| case_493 | English | D | COMPLETE | Yes |
| case_494 | English | D | COMPLETE | Yes |
| case_495 | Korean | D | INCOMPLETE | Yes |
| case_496 | English | D | INCOMPLETE | Yes |
| case_497 | English | D | COMPLETE | Yes |
| case_498 | Spanish | D | INCOMPLETE | Yes |
| case_499 | English | D | INCOMPLETE | Yes |
| case_500 | English | D | INCOMPLETE | Yes |
| case_501 | English | D | INCOMPLETE | Yes |
| case_502 | English | D | COMPLETE | Yes |
| case_503 | English | D | COMPLETE | Yes |
| case_504 | English | D | INCOMPLETE | Yes |
| case_505 | English | D | INCOMPLETE | Yes |
| case_506 | English | D | COMPLETE | Yes |
| case_507 | Japanese | D | INCOMPLETE | Yes |
| case_508 | English | D | COMPLETE | Yes |
| case_509 | English | D | INCOMPLETE | Yes |
| case_510 | English | D | INCOMPLETE | Yes |
| case_511 | English | D | INCOMPLETE | Yes |
| case_512 | English | D | COMPLETE | Yes |
| case_513 | French | D | INCOMPLETE | Yes |
| case_514 | English | D | INCOMPLETE | Yes |
| case_515 | English | D | INCOMPLETE | Yes |
| case_516 | English | D | COMPLETE | Yes |
| case_517 | English | D | INCOMPLETE | Yes |
| case_518 | English | D | INCOMPLETE | Yes |
| case_519 | English | D | INCOMPLETE | Yes |
| case_520 | English | D | INCOMPLETE | Yes |
| case_521 | English | D | COMPLETE | Yes |
| case_522 | Portuguese | D | INCOMPLETE | Yes |
| case_523 | English | D | INCOMPLETE | Yes |
| case_524 | English | D | COMPLETE | Yes |
| case_525 | English | D | INCOMPLETE | Yes |
| case_526 | English | D | INCOMPLETE | Yes |
| case_527 | English | D | INCOMPLETE | Yes |
| case_528 | English | D | INCOMPLETE | Yes |
| case_529 | English | D | INCOMPLETE | Yes |
| case_530 | English | D | COMPLETE | Yes |
| case_531 | English | D | INCOMPLETE | Yes |
| case_532 | English | D | COMPLETE | Yes |
| case_533 | English | N | NOT_APPLICABLE | Yes |
| case_534 | English | N | NOT_APPLICABLE | Yes |
| case_535 | English | N | NOT_APPLICABLE | Yes |
| case_536 | English | N | NOT_APPLICABLE | Yes |
| case_537 | English | N | NOT_APPLICABLE | Yes |
| case_538 | English | N | NOT_APPLICABLE | Yes |
| case_539 | English | N | NOT_APPLICABLE | Yes |
| case_540 | English | N | NOT_APPLICABLE | Yes |
| case_541 | English | N | NOT_APPLICABLE | Yes |
| case_542 | English | N | NOT_APPLICABLE | Yes |
| case_543 | English | D | COMPLETE | Yes |
| case_544 | English | D | INCOMPLETE | Yes |
| case_545 | English | D | COMPLETE | Yes |
| case_546 | Portuguese | D | INCOMPLETE | Yes |
| case_547 | English | D | COMPLETE | Yes |
| case_548 | English | D | INCOMPLETE | Yes |
| case_549 | English | D | COMPLETE | Yes |
| case_550 | English | D | INCOMPLETE | Yes |
