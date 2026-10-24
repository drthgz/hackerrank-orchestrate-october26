# Structured evidence evaluation — 2026-10-24

Milestone: structured SQL and all three deletion statuses. Baseline: b439c5f, 35 tests, case_05 exact. No paid inference or multimodal extraction. No final full-dataset run or submission score is claimed.

## Reproduction

```bash
python3 -m unittest discover -s tests -v
python3 code/evaluation/main.py --all-samples
python3 code/evaluation/main.py --all-samples --output-dir artifacts/structured-repeat
```

All requests are attempted before the independent evaluator opens sample_output.csv. The predictor never imports labels or evaluator code. Unsuccessful supported-scope attempts are reported as unsupported, with their exact first blocking reason. Unsupported does not mean NOT_APPLICABLE and produces no fabricated row.

## Measured public benchmark

| Metric | Result |
| --- | --- |
| Rows produced / all public requests | 2/32 (6.25%) |
| Unsupported | 30/32 (93.75%) |
| Structural validity of produced rows | 2/2 |
| Status accuracy on produced rows | 2/2 (100%) |
| Exact case accuracy on produced rows | 1/2 (50%) |
| Exact case yield across all 32 | 1/32 (3.125%) |
| Exact step content, ignoring step_no | 6 matches; 6 predicted; 8 expected |
| Step precision / recall / F1 | 100% / 75% / 85.7143% |
| Positional step-field accuracy | 38/56 (67.8571%) |
| Positional evidence_id field accuracy | 6/8 (75%) |
| Exact evidence_id sequence accuracy | 1/2 (50%) |
| Exact full step sequence accuracy | 1/2 (50%) |
| Baseline regressions | 0; case_05 remains exact |
| Reproducibility | Separate benchmark invocations emitted byte-identical prediction CSVs |

Denominators for status/case/sequence metrics exclude unsupported cases and are explicitly labelled; the 1/32 yield keeps overall coverage visible. Step content uses a multiset of all fields except step_no, so duplicates and wrong citations count. Field metrics compare positions over max(predicted, expected) step count; missing/extra steps count as mismatches for all seven fields. Evidence_id field accuracy counts empty future-work references as fields, not as factual evidence. Full-array sequence equality includes content and numbering. These are local diagnostic definitions, not an invented official scoring formula.

Public results:

- case_05: status, all three steps, all 21 fields, citation and sequence exact. Its original output SHA-256 remains `1f65d234af108b2ab48b2952cafbd75fe7225d7255b1b988ded4889e5e9e3e9d`.
- case_09: correct INCOMPLETE status and three correct step contents for the restore risk. Missing account absence and retained-security verification make the entire answer incorrect. No expected resource identifiers were added to prediction logic. The output is a scoped partial answer, not a complete challenge solution.

There are no processed public COMPLETE or NOT_APPLICABLE rows in this milestone. Both behaviors have independent synthetic coverage; the provided 32 labels contain no NOT_APPLICABLE examples at all. No accuracy is available for the 518 unlabeled evaluation requests.

## Unsupported requests

Only the first encountered reason is reported; resolving it may uncover additional unsupported evidence or policies.

| Case | Reason |
| --- | --- |
| case_01 | Request intent is outside the supported explicit English grammar |
| case_02 | Ambiguous or restricted intent is unsupported |
| case_03 | Request intent is outside the supported explicit English grammar |
| case_04 | Request intent is outside the supported explicit English grammar |
| case_06 | Ambiguous or restricted intent is unsupported |
| case_07 | Request intent is outside the supported explicit English grammar |
| case_08 | Request intent is outside the supported explicit English grammar |
| case_10 | Request intent is outside the supported explicit English grammar |
| case_11 | Ambiguous or restricted intent is unsupported |
| case_12 | Ambiguous or restricted intent is unsupported |
| case_13 | Ambiguous or restricted intent is unsupported |
| case_14 | Request intent is outside the supported explicit English grammar |
| case_15 | Ambiguous or restricted intent is unsupported |
| case_16 | Security retention applicability not established at audit time |
| case_17 | Ambiguous or restricted intent is unsupported |
| case_18 | Request intent is outside the supported explicit English grammar |
| case_19 | Request intent is outside the supported explicit English grammar |
| case_20 | No supported SQL resource lineage links to subject |
| case_21 | Ambiguous or restricted intent is unsupported |
| case_22 | Security retention applicability not established at audit time |
| case_23 | Ambiguous or restricted intent is unsupported |
| case_24 | Request intent is outside the supported explicit English grammar |
| case_25 | Request intent is outside the supported explicit English grammar |
| case_26 | Request intent is outside the supported explicit English grammar |
| case_27 | Request intent is outside the supported explicit English grammar |
| case_28 | Ambiguous or restricted intent is unsupported |
| case_29 | Request intent is outside the supported explicit English grammar |
| case_30 | Request intent is outside the supported explicit English grammar |
| case_31 | Ambiguous or restricted intent is unsupported |
| case_32 | Ambiguous or restricted intent is unsupported |

Grouped: 15 outside the explicit English grammar; 12 ambiguous/restricted intent; 2 unestablished security-retention conditions; 1 missing SQL resource lineage. These are conservative support boundaries, not claims that the actual requests are ambiguous to a person.

## Synthetic and regression validation

58 tests pass, retaining all original 35 tests unchanged. Added fixtures use arbitrary identifiers and no public expected answers:

1. **No deletion authorized:** export/correction/marketing/no-deletion instructions return NOT_APPLICABLE and exactly zero steps, even without identity/evidence. Mixed, qualified and revoked requests fail explicitly.
2. **Positive COMPLETE:** an earlier scoped SQL snapshot links profile-blue to subject-k; a later scoped empty copy proves absence. Expected COMPLETE with VERIFY_RECORD_ABSENT citing the later file. The empty snapshot without earlier linkage fails. An unprocessed text file or unknown table blocks COMPLETE.
3. **Historical alias:** an audit change links past@example.invalid to the current email. A nested search document containing the old email in uppercase is discovered without case-number assumptions.
4. **Replica drift:** a later clean primary does not erase the earlier surviving read replica. All copies cleaned in one cited snapshot can establish absence; separate uncombined witnesses remain unsupported for one-citation verification.
5. **Retention and tombstones:** a supplied retention deadline preserves a security record, with inclusive audit-time boundary coverage. A tombstone with the real stable subject reference and cleared direct identifiers is retained/redacted; exposed email or an extra full_name requires REDACT. An email used as the tombstone reference cannot masquerade as the permitted internal ID. Missing retained records or unknown/expired retention fail explicitly.
6. **Anonymization lineage:** identifiers present in an earlier analytics row can disappear later while resource lineage remains. Clean analytics plus positive profile absence supports COMPLETE; retaining any stable reference is not anonymous.
7. **Cutoff/conflict:** later clean evidence cannot change an earlier audit; same-time contradictory fields fail even if both rows are present. Nested identity matches cannot override a conflicting enclosing owner.
8. **Flow/restore ordering:** explicit enabled/restore_allowed fields yield disable-flow and block-restore before deletion. An explicit downstream/source dependency that contradicts canonical order is rejected, preserving both validation constraints.

Runtime label-access isolation remains tested for the predictor. Negative evaluator tests detect incorrect evidence, ordering and status. Validators were strengthened or retained; none were weakened to improve sample scores.

## Findings and improvements

- Added explicit relational/embedded-JSON schema adapters with scope and timestamp checks. SQL JSON remains inside the structured SQL adapter; standalone JSON files are not processed.
- Replaced profile-only policy handling with factual predicates and explicit unsupported conditions. In particular, a security event name alone is not proof of a live retention obligation.
- Added a closed-scope COMPLETE gate and positive profile-absence requirement. Preserved record presence alone is insufficient.
- Kept original identity associations through anonymization while rejecting resource reassignment and contradictory stable references.
- Added strict NOT_APPLICABLE recognition without reusing a reported workflow status as intent.
- Public case_09 exposes a remaining resource-discovery/verification-coverage failure. Missing checks are not synthesized from labels. This is a new evaluated failure, not a regression of a previously correct case.

## Runtime, usage and limitations

One measured benchmark including repeated predictions took 0.203527 seconds locally. Combined prediction CSV SHA-256: `93359a7d067ef0e8d3177874378c9a8c486843609789ec3fe8013f4320d1cdee`. No application cache is used; OS filesystem cache may be warm. Python 3.14.7 was used.

Runtime inference calls: 0; input/output inference tokens: 0/0; estimated inference cost: $0. Coding-assistant usage is separate. This document is a milestone record, not the required final-full-run usage report.

COMPLETE currently requires all admissible evidence to be supported SQL, so real mixed-format cases are intentionally excluded. INCOMPLETE may still identify a genuine violation without discovering the full required plan, as case_09 demonstrates. Exact evidence tie-breaking for equivalent witnesses and dependency-vs-canonical ordering precedence remain externally unspecified; unsupported conflicts are not silently decided.

Recommended next milestone, pending approval: deterministic text/log and standalone structured-record extraction with resource lineage and policy evidence correlation, plus focused explicit intent expansion. These would address missing verification scope and retention evidence before OCR or paid inference. No multimodal work is started here.
