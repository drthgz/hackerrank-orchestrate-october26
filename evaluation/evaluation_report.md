# Final release evaluation — 2026-10-24 America/Chicago

## Release scope and contract boundary

Starting research commit: 738a8d5. Release baseline: 099cc25 (consultation documents).
Production already contained the accepted tombstone fix from 91a8faf. This release
preserves it and adds exact stable subject_selector matching with conflicting-owner
and resource-reassignment protection. It does not activate the experimental lineage
index, alter policy/ownership heuristics or change prediction fallback behavior.

The required three-column CSV contains competition predictions. Strict auditing
requires proof; prediction fallback at four proof gates uses observed residual PII
or enabled recreation permission to predict INCOMPLETE, otherwise COMPLETE.
Absence of contradiction is not proof. The unchanged fallback is label-independent;
public labels are opened only after predictions and repeated evaluation runs.
No private truth or organizer-only files were used. No additional API calls occurred.

The statement requires 518 rows and evidence-backed complete plans. Structural
coverage does not satisfy all semantic obligations: empty/partial deletion plans
remain failures, sidecars do not alter CSV meaning, and organizer acceptance or
partial-credit weighting is unconfirmed. See [contract interpretation](../docs/submission_contract.md).

## Actual validation

- Baseline suite: 189 passed. Integrated suite: **200 passed, 0 failures/errors**.
  Python standard library only; Poppler pdftotext 26.01.0 installed.
- Fresh production generation: 518 unique sorted request IDs, exact columns and
  JSON fields, valid operation/state pairs, consecutive numbering and canonical order.
- Exactly byte-identical to artifacts/historical-lineage/candidate-full.csv.
  A second full production run also matches byte-for-byte.
- All 2,172 emitted steps pass policy-decision consistency checks. Every finding
  maps to an independently policy-assessed noncompliant observation and citation.
  This is an internal consistency check, not independent semantic certification.
- 1,580 latest physical-copy observations pass cutoff checks; citation/resource
  provenance validation has zero failures. All 192 support-fact provenance checks
  pass. No unsupported finding or unexplained added step was found.
- Fresh extracted archive replay reruns tests, full generation, candidate validation
  and public evaluation in a venv without installed Python packages or credentials.
  The external participant dataset and host Poppler are explicit dependencies.
  Final replay evidence is recorded in docs/release/final_release_report.md outside
  the archive and artifacts/package-validation.json locally.

## Public benchmark — all 32 samples

| Metric | Final result |
| --- | ---: |
| Produced / status matches | 32/32 / 32/32 (100%) |
| Exact cases / exact sequences | 2/32 / 2/32 (6.25%) |
| Matched / emitted / expected steps | 132 / 135 / 193 |
| Step precision | 132/135 (97.777778%) |
| Step recall | 132/193 (68.393782%) |
| Step F1 | 80.487805% |
| Positional field accuracy | 716/1365 (52.454212%) |
| Positional citation-field accuracy | 127/195 (65.128205%) |
| Aligned citation correctness | 50/50 (100%) |
| All emitted citations | 51 |
| Expected cited-step recall | 50/75 (66.666667%) |
| Missing finding / remediation / verification steps | 4 / 4 / 53 |
| Extra steps against public reference | 3 |
| Uncertain statuses / incomplete or unproved plans | 9 / 20 |
| Stronger audit-validator failures | 4 |
| Structural/citation provenance failures | 0 |

Exact cases remain case_05 and case_06. Public failures are case_01, case_02,
case_04 and case_31 (empty authorized-deletion plans). The three object-storage
steps extra to the public reference retain grounded support; they were not removed
to inflate exactness. Aligned citation correctness excludes omitted and extra
reference steps; the evaluator's broader cited comparison is 50/76, not 100%.
Field accuracy compares seven fields at each position, counting missing steps as
mismatches; renumbering affects it. Public results are byte-identical to the
reviewed research public candidate. No hidden-set accuracy or total score is known.

## Full dataset and exact changes

518 requests; 160 COMPLETE, 348 INCOMPLETE, 10 NOT_APPLICABLE; 2,172 steps.
All ten non-deletion rows have []. There are **140 uncertain statuses**, **302
incomplete/unproved plans**, and **45 stronger-audit failures**: 42 empty deletion
plans and three INCOMPLETE rows without all required phases. The validator is not
an exhaustive semantic audit, so 473 non-failing rows are not 473 compliance proofs.

The prior root output had 2,155 steps, 144 uncertain statuses and 49 stronger-audit
failures. The final release changes exactly these nine rows, adding 17 steps with
no removals or status changes; canonical renumbering follows each addition:

| Case | Resource | Finding witness / added operations |
| --- | --- | --- |
| case_544 | tombstone_8648 | evidence_52; REPORT_EXPOSED_PII, REDACT_RECORD, VERIFY_RECORD_REDACTED |
| case_546 | tombstone_8095 | evidence_52; same three tombstone operations |
| case_548 | tombstone_3745 | evidence_52; same three tombstone operations |
| case_550 | tombstone_7389 | evidence_52; same three tombstone operations |
| case_57 | data_flow_1368 | evidence_05; VERIFY_DATA_FLOW_DISABLED |
| case_112 | data_flow_3444 | evidence_10; VERIFY_DATA_FLOW_DISABLED |
| case_155 | data_flow_4305 | evidence_15; VERIFY_DATA_FLOW_DISABLED |
| case_204 | data_flow_5877 | evidence_20; VERIFY_DATA_FLOW_DISABLED |
| case_308 | data_flow_8933 | evidence_29; VERIFY_DATA_FLOW_DISABLED |

Tombstone findings cite evidence_52; their future remediation/verification citations
are empty. Connector checks cite the listed SQL file, have exact stable subject
selectors, disabled booleans, pre-cutoff capture/update times and agreement across
11 supplied physical copies (2+2+2+2+3). No newer claim contradicts the readbacks.
Relative to production immediately before selector integration, only the five
connector rows change. The tombstone behavior was already integrated in production
but absent from the old root release artifacts.

## Participant-created cases and adversarial tests

Eleven new fixtures exercise production adapters without experimental lineage or
public labels. At least three independent positive/adversarial cases are:

1. An arbitrary stable subject selector and enabled=false in two SQL copies emit
   one cited disabled-flow check, while the whole-case status remains uncertain.
2. Unknown, case-changed, padded or substring selectors assign no subject. Existing
   email-selector support remains; conflicting known/unknown references reject.
3. A nested selector conflicting with its enclosing stable owner rejects; later
   resource reassignment also rejects rather than inheriting historical ownership.
4. A late-captured selector emits no check. A measured enabled flow generates a
   finding, disable action and future verification, not a compliant-state proof.
5. Disagreeing enabled/disabled replicas produce an incomplete plan, not a cited
   claim that the flow is already disabled.

Existing counterexamples retain exposed versus clean tombstones, missing retention,
support excerpt versus full scan, ambiguous attachment ownership, temporal cutoffs,
identity-free absence, anonymous records without ownership, workflow claims,
provenance and deterministic serialization. All 200 tests pass. Historical model
experiment tests are mocked/offline; no inference experiment was rerun.

## Failures, fixes and limits

Fixed release skew: the prior root output lacked the accepted steps and the ZIP
contained stale source/reports. Fixed the narrow stable-selector adapter gap and
updated reassignment guards. Archive replay previously depended on stale external
partial-baseline files; it now compares the actual selected full/public release
outputs and checks shipped source/document parity. The consultation's missing
Poppler issue is resolved by the documented dependency already installed here.

Unresolved account absence and anonymous analytics lineage, conditional security
retention and support context/ownership still constrain completeness. The 45
stronger-validator failures are reported, not suppressed by changing fallback.
Even a cited resource check does not close unknown whole-case scope. No transcript
was fabricated, no push or submission occurred, and no deadline is configured.

## Reproduction and hashes

Use the setup, generation, validation, benchmark, packaging and clean replay
commands in README.md. Reports reflect the production output-producing run, not a
copied experimental CSV. Runtime: 24.836820 seconds, zero model calls/tokens, $0.

Final output SHA-256: `51ea84c5e2b8e66af019d321421ed6d383e5e95df16244bd41af3822eb25610d`.
Public CSV SHA-256: `868a7c3ebf14db3d04663b85cd2cce0907783d8a8b35713fbe7b665694e762c9`.
