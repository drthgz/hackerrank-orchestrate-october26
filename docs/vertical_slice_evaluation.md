# Vertical slice evaluation — 2026-10-24

Scope: approved first milestone only. Architecture and case_05 slice approved by the Technical Lead. No full-dataset run, submission artifact, or contest score is claimed. Supplied inputs/labels were not modified.

## Measured public-label result

Independent command:

```bash
python3 code/evaluation/main.py --prediction artifacts/case_05.csv --repeat artifacts/case_05_repeat.csv --case-id case_05
```

| Check | Result |
| --- | --- |
| Selected-request coverage | 1/1, exactly case_05 |
| Structural contract | PASS |
| Deletion-status accuracy | 1/1: INCOMPLETE |
| Exact case match | 1/1 |
| Step matches | 3/3 expected; 3 predicted |
| Step precision / recall / F1 | 100% / 100% / 100% on this one case |
| Positional step-field accuracy | 21/21 |
| Evidence-reference sequence | Exact match |
| Full ordered step array | Exact match |
| Reproducibility | Byte-identical across independent runs and different working directories |

Expected public sequence, read only by the evaluator: REPORT_REMAINING_RECORD / PRESENT citing evidence_54; DELETE_RECORD / ABSENT with empty evidence; VERIFY_RECORD_ABSENT / ABSENT with empty evidence. All target account_service / account_005, numbered 1–3.

Sample coverage is only 1/32; the other 31 were not evaluated for predictive correctness. No accuracy is available for the 518 unlabeled requests. Validation is structural and checks citations' existence/timing; semantic correctness here is separately established by label comparison and inspected SQL provenance.

Output SHA-256: `1f65d234af108b2ab48b2952cafbd75fe7225d7255b1b988ded4889e5e9e3e9d`.

Two measured fresh-process runs on Python 3.14.7 took 0.074284 and 0.072110 seconds including interpreter startup. Neither uses application caching; OS filesystem cache may be warm. These are local observations, not runtime guarantees. Runtime model calls: 0; inference input/output tokens: 0/0; inference cost: $0. Coding-assistant usage is separate. This is not the required final-full-run usage report.

## Regression suite

`python3 -m unittest discover -s tests -v`: 35 tests pass. No known failing regressions. No prior implementation baseline existed.

Coverage includes historical and case-normalized email, ambiguity and conflicting stable IDs, future identity exclusion, independent primary/failover state in both directions, cross-copy and same-copy temporal updates, inclusive cutoff, contradictory timestamps/states, policy missing/duplicate/conditional/retention refusal, tombstone refusal, misleading SUCCESS claims, unsafe SQL rejection, unsupported schemas, absence-of-evidence handling, canonical order, malformed output, incorrect citations, wrong-resource remediation, CSV/path validation, evaluator negative comparisons, reproducibility, and predictor label-access isolation.

Three representative authored fixture cases (full executable fixtures in tests/test_slice.py):

1. **Arbitrary-ID replica drift.** Request arbitrary-case, subject person-z at new@example.invalid, resource resource-q. At 2026-03-01 primary is empty and failover contains an ACTIVE profile; audit is 2026-04-01. Policy delete-profiles requires unconditional profile DELETE. Expected INCOMPLETE with exactly finding(source-a), DELETE_RECORD, VERIFY_RECORD_ABSENT; changing the workflow claim to NOT_STARTED does not change the result.
2. **Later clean primary is insufficient.** The same failover residual exists on March 1; source-b has a clean primary on April 1. Expected INCOMPLETE still citing source-a, since the primary's newer timestamp does not supersede the failover copy. In the paired case, a newer empty snapshot of the failover does supersede the earlier failover row; the slice refuses to infer global COMPLETE.
3. **Historical identity with future information excluded.** An admissible history event links old@example.invalid to then@example.invalid. The current snapshot updated after audit contains new@example.invalid. The old email resolves to person-z via history; the future snapshot email is excluded. An ambiguous second person or future-only alias causes an explicit error rather than a false match.

Additional policy fixture: changing the profile rule to RETAIN or a conditional action must fail as unsupported; it must never emit DELETE to make the sample pass. An ACTIVE-to-TOMBSTONE mutation likewise fails rather than treating a tombstone as a deletable profile.

## Failures found and improvements

- Initial SQLite capability restriction rejected ordinary PRIMARY KEY index creation and inventory indexes. Added only in-memory index creation/reindex and the supplied foreign_keys=ON pragma; filesystem attachment, extension loading, arbitrary pragmas, views and triggers remain denied and tested.
- Inventory SQL uses snapshot_scope rather than the profile adapter's header format. Kept profile header/time validation strict, while permitting other schemas to be scanned solely for unsupported subject links. They do not receive profile semantics.
- Strengthened contract validation so findings require compatible remediation and every remediation requires a compatible finding plus verification. Wrong-resource actions are regression-tested.
- Added negative evaluator tests for wrong evidence, reordered steps and wrong status, so a green comparison is not merely an unconditional success path.

## Limits and next milestone

Supported semantics: explicit English profile-deletion intent, the named account primary/failover schemas, unconditional DELETE, and residual-profile INCOMPLETE output. All non-SQL formats remain unprocessed and are reported in diagnostics. Complete-state verification, non-deletion intent and wider policies are deliberately not inferred.

Next recommendation, subject to approval: broaden structured SQL state reconstruction and add evidence-backed COMPLETE / explicit NOT_APPLICABLE paths with corresponding public/custom evaluation. Preserve the same typed boundaries and keep labels isolated. Multimodal extraction and paid inference remain separate approvals/milestones.
