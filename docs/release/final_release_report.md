# Final release report — 2026-10-24 America/Chicago

## Decision and Git release state

**GO for the reproducible competition prediction release, with disclosed semantic
limitations. NO-GO for representing it as certified deletion-audit compliance.**
There are no remaining integration, packaging or replay blockers. Organizer
acceptance of uncertain statuses and incomplete plans is unconfirmed; these are
substantive submission risks, not resolved compliance obligations.

Starting research commit: `738a8d5ef15ca001cf1d70000736cb9ad43c8b71`.
Observed baseline HEAD: `099cc25ab016160c83bcfa7c3712ff2351eb9bcb` on main.
Validated production/source commit: `5c86b3355f9561f7c2401d7793a8de685d817799` on main.
This report and the append-only transcript are recorded in the following local
release-record commit; resolve its exact ID with
`git log -1 --format=%H -- docs/release/final_release_report.md`.
The final response also records that commit. CSV/ZIP are intentionally ignored
separate-upload artifacts. Nothing was pushed or submitted.

## Baseline preservation and authentic consultation transcript

Previous artifacts remain recoverable under artifacts/final-release/:

| Preserved artifact | SHA-256 |
| --- | --- |
| previous-output.csv | `b9045f0b71ec8025cfa1b67dd3b7ee5a82f7411787173743580d0f15aa9275b6` |
| previous-code.zip | `cd014d91ffbcf470bdde1acbf96d18767de74926b425b2a45ce605b2140663b7` |

The original root CSV had 518 rows, 2,155 steps, 144 uncertain statuses, 302
incomplete/unproved plans and 49 stronger-audit failures. It passed structural and
citation/resource validation. The baseline suite passes 189 tests with Poppler
available here. The old ZIP had 38 members and stale source/reports.

The existing Copilot consultation append is explicitly **partial** and names its
native session/context source, `copilotcli:/7f36f07b-4258-459d-98c0-ff8dd3a69b32`.
Its fidelity clarification distinguishes recovered messages from an assistant-
authored activity index, notes a missing trailing reminder and missing native
tool payloads/timestamps, and does not invent a model identifier. We preserved it
verbatim rather than repairing or reconstructing history. Independent access to
the Copilot native service is unavailable in this harness; authenticity can be
confirmed to the extent of its recorded provenance and byte-preservation checks,
not as an independently re-exported complete native event log.

Verified log integrity: the research-commit log remains an exact prefix; the
179,078-byte pre-consultation prefix hashes to
`db00015422ec87c86f47bab219a800fdb424e7af3ec8d69721f540706e7b51b9`.
The first 4,029 lines reproduce the recorded 322-line partial append hash
`a9028f85ca1c651b18b261a2bc7db27e9dafb1a3f80b3e3e1cb485c4d1fc0a08`.
No existing log bytes were changed. This release appends its own session/turn
records using runtime model gpt-6.1-sol and harness Codex Desktop.

## Exact integrated improvements

The accepted tombstone remediation was already in production at baseline (91a8faf)
and is preserved: direct identifiers are redacted while the stable reference stays;
unresolved retained-record linkage remains an omission. We added subject_selector
to exact stable-reference matching and to conflicting-owner/reassignment guards in
SQL and other observation handling. Existing email selectors retain support.
The experimental temporal lineage engine remains outside the production path.
No speculative ownership, retention, anonymization or resource mapping was added;
policy and prediction fallback behavior are unchanged.

Fresh production generation is byte-identical to the reviewed
artifacts/historical-lineage/candidate-full.csv. Compared to the prior root output,
exactly nine rows change: **17 added steps, zero removals, zero status changes**.
All other rows retain their complete original CSV content. Canonical numbering
changes only where additions require it.

| Case | Resource | Witness | Added operations |
| --- | --- | --- | --- |
| case_544 | tombstone_8648 | evidence_52 | REPORT_EXPOSED_PII; REDACT_RECORD; VERIFY_RECORD_REDACTED |
| case_546 | tombstone_8095 | evidence_52 | same three tombstone operations |
| case_548 | tombstone_3745 | evidence_52 | same three tombstone operations |
| case_550 | tombstone_7389 | evidence_52 | same three tombstone operations |
| case_57 | data_flow_1368 | evidence_05 | VERIFY_DATA_FLOW_DISABLED |
| case_112 | data_flow_3444 | evidence_10 | VERIFY_DATA_FLOW_DISABLED |
| case_155 | data_flow_4305 | evidence_15 | VERIFY_DATA_FLOW_DISABLED |
| case_204 | data_flow_5877 | evidence_20 | VERIFY_DATA_FLOW_DISABLED |
| case_308 | data_flow_8933 | evidence_29 | VERIFY_DATA_FLOW_DISABLED |

The tombstone witness applies to FINDING; future steps use empty evidence_id.
All five connector checks have enabled=false, exact known stable selectors,
admissible capture/update times, no newer contradictory activity, and agreement
across 11 physical copies (2+2+2+2+3). Compared with the immediate production
baseline, only these five connector rows change; the previous root output also
lacked the already-accepted 12 tombstone steps. There is no unexplained discrepancy.

## Validation and public metrics

Environment: Python 3.14.7, SQLite from the standard library, Poppler pdftotext
26.01.0. Baseline: 189 tests passed. Integrated and clean-extracted suites:
**200 passed, 0 failures, 0 errors**, including 11 new production-selector fixtures.
Fixtures cover exact/two-copy matches, unknown/padded/case-changed selectors,
email compatibility, conflicting/nested owners, reassignment, late capture,
enabled flows and replica disagreement. Existing tombstone/adversarial tests pass.

| Public metric | Actual final result |
| --- | ---: |
| Status accuracy | 32/32 (100%) |
| Exact cases / exact sequences | 2/32 (6.25%) / 2/32 (6.25%) |
| Step precision | 132/135 (97.777778%) |
| Step recall | 132/193 (68.393782%) |
| Step F1 | 80.487805% |
| Positional field accuracy | 716/1365 (52.454212%) |
| Aligned citation correctness | 50/50 (100%) |
| Emitted citations / expected cited-step recall | 51 / 50 of 75 (66.666667%) |
| Missing finding / remediation / verification | 4 / 4 / 53 |
| Extra reference steps | 3 |
| Uncertain statuses / incomplete or unproved plans | 9 / 20 |
| Stronger audit-validator failures | 4 |

All 32 public predictions are unchanged from the accepted research public CSV.
Labels enter only evaluation after predictions and repeats. The extra object-
storage steps remain supported by source evidence and were not removed to match
labels. Hidden status/step accuracy and total competition score remain unknown.

## Full-dataset coverage and stronger-validator failures

518 unique sorted IDs, exact schema/JSON fields, canonical operations/order and
consecutive numbering. Status counts: 160 COMPLETE, 348 INCOMPLETE,
10 NOT_APPLICABLE; all ten N/A arrays are empty. Total steps: 2,172.
Structural errors: 0. Citation/resource-provenance failures: 0.
Unsupported findings: 0 under policy/evidence consistency checks.
All 2,172 emitted steps were checked against policy decisions; 1,580 latest-copy
observations pass cutoff checks and all 192 support-fact provenance checks pass.
These are deterministic consistency checks, not independent source-semantic proof.

**140 statuses remain uncertain; 302 plans remain incomplete or unproved.**
The stronger validator rejects **45 rows**: 42 empty authorized-deletion plans
and three INCOMPLETE rows missing required phases. The 473 rows not rejected
are not 473 proven whole-case compliance decisions. Full failure inventory:

- Authorized deletion requires evidence-backed steps (42): case_103, case_107, case_108, case_111, case_157, case_160, case_162, case_206, case_253, case_257, case_260, case_304, case_309, case_354, case_362, case_403, case_408, case_409, case_411, case_412, case_45, case_456, case_457, case_458, case_460, case_462, case_479, case_484, case_503, case_506, case_508, case_512, case_543, case_545, case_547, case_549, case_55, case_58, case_59, case_60, case_63, case_76.
- Incomplete case requires all three phases (3): case_520, case_522, case_88.

Remaining evidence gaps include account absence, ownership of anonymous analytics,
security retention applicability, support context/full scans and exclusive
attachment ownership. The unchanged fallback may predict COMPLETE merely from
lack of a residual contradiction. That is not proof. Diagnostics are qualitative,
uncalibrated and external to the grader-facing CSV; they cannot cure missing
semantic content or guarantee organizer acceptance. No unsupported new step was
added to suppress validator failures.

## Clean replay and artifact contents

The source-only ZIP has 50 members. Integrity and every member's byte equality to
the source tree pass; local Markdown links resolve. A fresh extraction and venv
with no pip packages and no inherited credentials rerun all 200 tests, generate
518 predictions, validate them, and repeat public evaluation. Both full and public
CSVs match their root/reference bytes. A second independent full run also matches.
Rebuilding the ZIP produces the identical hash.

The same external participant dataset is attached for replay; host Poppler is a
documented external dependency. All runtime/evaluation calls use deterministic
local code: providers/models none, calls 0, input/output/total tokens 0, average
per request 0, total/per-request inference cost $0. Production generation took
24.836820 seconds. Coding-assistant development usage is separate and unmeasured.

Archive contents include code, all tests and their supporting evaluation modules,
README, required evaluation/usage reports and the final AI Judge brief. Research
evaluation source remains only to support reproducible tests; generated experiments,
API clients/caches, dataset, secrets, virtual environments, nested archives,
output.csv and log.txt are excluded. This final report and checksum manifest stay
outside the ZIP to avoid a self-referential archive hash. Current source/report
bytes match the package, including the validated production commit.

Local machine-readable records: artifacts/final-release/baseline-hashes.json,
baseline-validation.json, release-checks.json, validation.json, production.json,
repeat.json, public/benchmark.json and artifacts/package-validation.json.
Replay commands are documented in README.md. The external checksum manifest also
pins this report and the briefing.

## Submission readiness checklist

- [x] Prior output/ZIP preserved until new validation and replay passed.
- [x] Accepted production improvements only; positive/adversarial tests pass.
- [x] Fresh production output equals reviewed candidate; 17 additions explained.
- [x] All 518 request IDs, exact schema, JSON, ordering, citations and cutoffs checked.
- [x] Public metrics and unresolved stronger-validator counts reported honestly.
- [x] README/evaluation/usage correspond to the actual final output-producing run.
- [x] ZIP integrity, source parity, exclusions and documentation links checked.
- [x] Deterministic repeat/rebuild and fresh-extraction byte-for-byte replay pass.
- [x] Authentic transcript history preserved; partial Copilot limitations disclosed.
- [x] Production and release documentation committed locally; no push/submission.
- [ ] Whole-case compliance proof for all requests — unresolved and not claimed.
- [ ] Organizer acceptance of heuristic statuses/partial plans — not established.

## Final artifact hashes

| Artifact | SHA-256 |
| --- | --- |
| output.csv | `51ea84c5e2b8e66af019d321421ed6d383e5e95df16244bd41af3822eb25610d` |
| code.zip | `b3e91133f851a1060aa3dea10390c365db35175a4bc75cacdc9256fa447bf023` |
| log.txt | `10843fdec34d57eab4c43bb54537a5ee4cdb9e34ddcd403a86330eee9c350e11` |
| README.md | `e38c9f88cb5b5d440d77ca8460cf1e7a20889a53cc732306d93de555ccbfcb1c` |
| evaluation/evaluation_report.md | `580d80252145c41ee94eb19545219d2907d4ab61bec72f1bb65f638b97fa8c50` |
| evaluation/usage_report.md | `275412840e40d39b268858ac8923ca7376f972299d973a98931d397647b57404` |
| docs/release/ai_judge_brief.md | `cfc3876aab480595ffd7dd79ad93419d6155179eda81964f87b760dc31ba7dd4` |

The root log hash is the final append-only transcript snapshot for this release.
