# Independent Technical Consultation — Ghost Data Still Exists

Review date: 2026-10-24  
Repository head: `738a8d5ef15ca001cf1d70000736cb9ad43c8b71` (`main`)  
Scope: read-only review of the checked-out repository and existing release/candidate artifacts. No production code, tests, root submission artifact, branch, or commit was changed. This report is independent of the repository's prior recommendations.

## 1. Executive Summary

**Recommendation: NO-GO for the current root release pair (`output.csv` + `code.zip`).** The CSV is structurally sound and covers all 518 request IDs, but it is not the latest validated candidate, it predicts `COMPLETE` for cases whose evidence is explicitly insufficient, and it contains more stronger-audit failures than the newer candidate. The archive is older still: its production source and embedded evaluation/usage reports do not match the checked-out tree.

Verified root `output.csv` facts:

- Header, 518 unique sorted case IDs, JSON structure, allowed step vocabulary, and cited-resource provenance pass the existing candidate validator.
- Status counts are 160 `COMPLETE`, 348 `INCOMPLETE`, and 10 `NOT_APPLICABLE`; there are 2,155 steps.
- SHA-256 is `b9045f0b71ec8025cfa1b67dd3b7ee5a82f7411787173743580d0f15aa9275b6`.
- The validator reports 144 uncertain statuses, 302 incomplete/unproved plans, and **49** rows rejected by the stronger audit validator. Structural validity is not semantic audit completeness.

The separate lineage candidate, `artifacts/historical-lineage/candidate-full.csv`, has the same status counts and passes the same structural/provenance checks. It adds five evidence-backed connector verification steps in five cases, while preserving the four-case tombstone improvement already present in the separate accuracy candidate. It has 140 uncertain statuses and **45** stronger-audit failures. Its SHA-256 is `51ea84c5e2b8e66af019d321421ed6d383e5e95df16244bd41af3822eb25610d`. It is not the root output and is not included in `code.zip`.

The latest research commit is experimental, not a production integration: it adds a lineage index, tests, and a report but does not change the production adapter. The evidence is directly actionable: production identity matching omits the stable `subject_selector` field that the experiment successfully uses to recover the five disabled-connector checks.

The largest correctness risk remains the prediction fallback in `code/audit/prediction.py:89-106`: at four proof-gate failures, no observed residual identifier or enabled recreation path becomes `COMPLETE`, even though the code and report acknowledge that absence of contradiction is not proof of deletion. The fallback emits empty or partial step arrays for such rows. That is a competition heuristic, not a challenge-compliant proof of completion.

Validation executed here: `python3 -m unittest discover -s tests -q` discovered 189 tests, but did **not** pass in this environment: two tests errored and one failed because Poppler's `pdftotext` executable is unavailable. No package was installed. The README documents this external prerequisite. The root candidate and separate five-check candidate were both independently passed through the existing validator without writing diagnostic files.

## 2. Overall Assessment

The project has a thoughtful evidence-first architecture and unusually good uncertainty documentation. It correctly separates a conservative audit engine from a broader output-producing competition heuristic, and it keeps prediction labels out of the production path. The architecture has credible handling for identity history, evidence availability cutoffs, physical SQL copies, policy predicates, and provenance.

However, three different objects are being described as though they were one release:

1. The checked-out production tree at `738a8d5`.
2. The root output, which is older than the accepted tombstone candidate and the five-check lineage candidate.
3. The ignored, prebuilt `code.zip`, which predates current production-source changes and embeds older evaluation and usage reports.

This mismatch is not cosmetic. A reviewer can receive a candidate CSV whose corresponding generator and reports are absent or stale. It also explains why the user-reported 45 validator failures and five extra checks are true of a separate artifact but not of the root CSV.

The public benchmark is useful as a regression suite, not as proof of hidden-set correctness. 32/32 public status accuracy coexists with only 2/32 exact cases, a large missing-step count, and a status heuristic that matches public labels without proving the result. No public score should be presented as evidence that `COMPLETE` semantics are satisfied.

## 3. Verified Strengths

- **Contract grounding:** the problem statement and policy table are explicit and consistently represented in most production policy code. `NOT_APPLICABLE` uses an empty array. The source validator checks required columns, canonical numbering/order, allowed operation/state pairs, citations, and remediation-to-verification pairing (`code/audit/contract.py:20-87`).
- **Conservative audit path:** `pipeline.audit` distinguishes evidence-backed audit conclusions from unsupported cases and refuses to infer a whole-case `COMPLETE` merely from a set of compliant observations (`code/audit/pipeline.py:19-32`, `121-143`).
- **Identity and time discipline:** request aliases are filtered at the audit cutoff; later identity snapshots do not backdate aliases (`code/audit/identity.py:1-46`). Evidence extraction uses manifest capture time and observed/update time separately. SQL copies remain distinct through `copy_id` and `latest_per_copy` (`code/audit/sql_evidence.py:91-213`).
- **Policy restraint:** supplied retention dates and explicit ownership/context are required for conditional `RETAIN`, `REDACT`, and `DELETE` decisions. Missing connector configuration is not treated as proof that a data flow is disabled (`code/audit/policy.py:24-90`).
- **Evidence provenance:** SQL evidence is loaded into an in-memory database with an authorizer and progress budget; the parser rejects unsupported tables and conflicting schemas (`code/audit/sql_evidence.py:43-89`). Screenshot transcriptions are content-hash-bound and identify their limited extraction scope (`code/audit/reviewed_images.py:1-20`).
- **Prediction isolation:** the production prediction path does not open public labels; the evaluator opens labels after prediction and repeatability checks (`code/evaluation/main.py:33-96`). Its diagnostics explicitly distinguish structural validity from audit-validator failures.
- **Reproducible techniques:** the five connector checks have explicit resource IDs, selector fields, capture/observation times, disabled states, and single-file witnesses for all physical copies. The lineage candidate records a direct citation check for each (`docs/historical_lineage_experiment.md:17-32`).
- **No runtime inference dependency:** the final runtime is deterministic Python/SQLite/Poppler with zero runtime model calls or token cost according to `evaluation/usage_report.md:1-21`. The historical paid experiment is clearly distinguished from the final runtime.
- **Good scope discipline in the lineage study:** it rejects workflow success as ownership/state proof and does not turn unlinked 404s, row order, numeric proximity, or cohorts into ownership edges (`code/evaluation/lineage.py:91-155`; `docs/historical_lineage_experiment.md:5-16`).

## 4. Critical Findings

### CF-1 — `COMPLETE` fallback is explicitly an absence-of-contradiction guess

**Confirmed, P0.** `predict` catches four whole-case proof failures and assigns `COMPLETE` whenever `residual_signals()` returns empty (`code/audit/prediction.py:19-27`, `89-106`). That branch can have no observations and emit `steps=[]`. The project itself says “No observed contradiction does not prove completion” in the README and output contract documentation. The supplied contract instead requires evidence-backed verification for `COMPLETE`.

This is not just a low confidence annotation: `steps_json` does not carry uncertainty, and a sidecar cannot change the grader-facing meaning of `COMPLETE`. The root diagnostics report 144 uncertain statuses; the newer separate candidate reports 140. The accurate statement is “518 structurally valid predictions,” not “518 completed deletion audits.”

### CF-2 — Root `output.csv` is not the latest validated candidate

**Confirmed, P0.** The root output hash is `b9045f0b…9275b6`. The accepted tombstone candidate is `5f30a16f…e6c25f`; the latest lineage candidate is `51ea84c5…25610d`. The root output differs from the accuracy candidate in four cases, missing 12 evidence-backed tombstone steps (three per affected case: `case_544`, `case_546`, `case_548`, `case_550`). It differs from the lineage candidate in nine cases total: those four cases plus five connector cases (`case_57`, `case_112`, `case_155`, `case_204`, `case_308`).

The latest candidate keeps the root's 160/348/10 status split, adds the 12 tombstone steps and five connector checks, and reduces stronger-audit failures from 49 to 45. No status change is reported. The separate candidate's own structural/provenance validation passed in this review; it is not represented as fully semantically compliant.

### CF-3 — `code.zip` is a stale release and does not match the working tree

**Confirmed, P0.** The 97,789-byte archive contains 38 members. It lacks the latest lineage implementation, report, and tests (`code/evaluation/lineage.py`, `code/evaluation/historical_lineage.py`, `tests/test_lineage.py`, `tests/test_policy_tracks.py`, among others). Its copies of `code/audit/competition.py`, `evidence.py`, `sql_evidence.py`, `tests/test_competition.py`, and `tests/test_prediction.py` differ from the working tree. In particular, the archive predates the accepted exposed-tombstone plan and later support-fact provenance behavior.

The embedded `evaluation/evaluation_report.md` and `evaluation/usage_report.md` are also not byte-equal to the current root reports; the archive lacks the later accuracy and combined-policy updates and all lineage findings. `README.md` is byte-equal to the working copy but reports 128 passing tests and older public metrics, while the checked-out suite discovers 189 tests. Thus the archive's README, source, reports, root output, and latest separate candidate do not describe one coherent release.

### CF-4 — Latest five connector checks are not implemented in production

**Confirmed, P1 with high confidence.** Production `identity.matches` treats `subject_selector` as an email-like alias but excludes it from the stable-reference tuple (`code/audit/identity.py:49-68`). The experimental owner resolver recognizes a `subject_selector` exactly equal to a known `user_id` as a stable subject (`code/evaluation/lineage.py:110-154`). Five SQL configurations explicitly provide that field and `enabled=false`; all are captured/observed before their case cutoffs and all physical copies agree. The experiment adds `VERIFY_DATA_FLOW_DISABLED` for each one (`docs/historical_lineage_experiment.md:17-32`).

This is a concrete missed-evidence adapter gap, not a speculative extension of historical lineage. It also disproves the broadest reading of “evidence-sufficiency ceiling”: at least five defensible verification checks were recoverable without changing policy or guessing ownership.

### CF-5 — Claimed test success is not reproducible in this environment

**Confirmed environmental validation failure, P1.** The full command discovered 189 tests. One failed and two errored because `pdftotext` was not installed; the failure also changed the expected error from an unprocessed-media-scope rejection to the explicit missing-Poppler error. `README.md:8-11` documents Poppler as a prerequisite, but the test run here cannot substantiate the documentation's “all tests pass” claims. The candidate CSV validator still passes independently.

No installation was performed because the consultation boundaries prohibit unapproved dependency installation. A clean checkout/evaluation environment must install Poppler or the PDF-adjacent tests and audit run will fail.

## 5. Architecture Review

1. **Separation of concerns — strong core, weak release boundary.** Models, identity, evidence adapters, policy, planning, output contract, and evaluation have distinct modules. The prediction layer deliberately bypasses proof gates, but sits in the same production package and writes the same three-column format. The release manifest must therefore pin code/output/report hashes together; it currently does not.
2. **Evidence extraction — broad but specialized.** SQL, JSON, logs, text, selectable-text PDFs, and reviewed images are handled. Known formats are explicit, which is safer than generic keyword matching. Reliability depends on the Poppler executable and manually hash-bound screenshot transcriptions. Unsupported media correctly keeps scope open; however, the “reviewed image” table is still a static transcription surface that needs independent visual re-review when images change.
3. **Identity/resource lineage — good conservative model, one adapter omission.** Historical aliases and conflict handling are stronger than case-ID heuristics. Production `matches` omits stable `subject_selector`, while the experimental lineage code proves that field has meaning in supplied connector SQL. Beyond that narrow gap, the report's refusal to invent account resource IDs or infer analytics ownership from anonymous state is justified.
4. **Temporal consistency — generally strong.** Evidence is gated by both observed and available/capture times, and a later state-changing activity claim blocks stale readback. The separate lineage index bounds ownership edges and filters at each request cutoff. Avoid collapsing availability time into event time; the experiment is correct to reject late-captured records even where embedded event timestamps are earlier.
5. **Privacy/retention policy — appropriately cautious.** `SECURITY_AUDIT_LOG` verification is withheld without a supplied, still-applicable retention window; legal hold requires explicit active retention; backup archives are retained but restore must be blocked. Do not relax these rules simply to raise step recall. The policy engine's fail-closed exceptions are an appropriate representation of unresolved facts.
6. **Remediation/planning — traceable but not exhaustive.** The plan sorts canonical operations and pairs findings/remedies/verifications. It rejects some dependency ordering conflicts rather than silently emitting unsafe ordering. The prediction validator is intentionally weaker than the audit validator (`code/audit/prediction.py:115-163` vs `code/audit/contract.py:32-87`); this is why 0 structural errors can coexist with 45 or 49 semantic/audit failures.
7. **Deterministic versus model-assisted — reasonable for the submitted run.** No runtime model inference is used. A prior paid model experiment is isolated and explicitly not adopted. The deterministic intent grammar is a maintainability cost and can fail closed on unseen phrasing; no evidence reviewed here supports replacing it with a model in the final hours.
8. **Error/uncertainty management — explicit in diagnostics, lost in CSV.** Errors are surfaced for unsupported input and identity conflicts. The sidecar records proof gates, but the required CSV has no uncertainty field. The fallback consequently writes success-shaped `COMPLETE` statuses and empty/partial arrays. This is the most important interface-level design tension.
9. **Reproducibility/runtime dependencies — documented, release not reproducible as a single unit.** Python has no package dependencies, but Poppler is a hard external dependency. Current package verification uses a fresh venv and strips credentials, yet the archive currently being reviewed is stale. Rebuild and clean-replay are required after selecting the final candidate.
10. **Maintainability/extensibility — solid explicit adapters, growing experiment duplication.** The lineage implementation under `code/evaluation` duplicates portions of production parsing to preserve broader observations. Keep the indexed lineage research separate until its semantics are tested, but move the verified stable-selector rule into the production identity adapter and add an end-to-end fixture. Do not promote the whole experiment index wholesale under deadline pressure.

## 6. Challenge Compliance

| Requirement | Assessment | Evidence |
|---|---|---|
| Exactly 518 sorted rows and exact CSV header | **Satisfied by root file** | Root validator: 518 rows, exact IDs, sorted/unique, header verified. |
| Valid JSON step arrays, exact step fields, numbering and operation vocabulary | **Structurally satisfied** | Root validator reports zero structural errors. |
| `NOT_APPLICABLE` with `[]` | **Satisfied in candidate validator** | Contract writer and validator accept only empty steps for this status; 10 root rows classify as N/A. |
| Deletion intent including non-deletion requests | **Partially satisfied / limited grammar** | Deterministic supported language grammar plus competition extension; unsupported language/phrasing can fail to produce a prediction. Public 32/32 is not hidden-set proof. |
| Current and historical identifiers | **Mostly satisfied where evidence links exist** | Identity snapshots and audit history are cutoff-aware; reused/conflicting identifiers fail closed. |
| State at `audit_at`, not reported status | **Mostly satisfied** | Production reads admissible evidence and treats activity results as claims; stale/post-cutoff evidence is rejected. |
| `COMPLETE` only with evidence-backed verification proving current state | **Potentially violated by design** | Four-gate fallback emits `COMPLETE` on no residual signal, including zero observations. Root has 144 uncertain statuses. |
| `INCOMPLETE` has findings, complete ordered remediation, and future verification | **Not satisfied for all rows** | Root stronger validator failures: 49; latest separate candidate: 45. Root/experiments document 302 incomplete or unproved plans. |
| Findings cite admissible evidence; future steps have empty citation | **Satisfied for emitted steps under validator** | Zero citation/time/resource provenance failures; this validates emitted steps, not omitted steps. |
| Every relevant record/copy and recreation risk is covered | **Partially satisfied** | Five directly grounded connector checks exist only in the research candidate; unresolved account/analytics lineage remains. |
| Policy-specific retention/redaction/tombstone semantics | **Generally conservative; incomplete coverage** | Explicit retention/ownership predicates are required. Separate accuracy candidate restores exposed tombstone redaction in four rows; root output omits those steps. |
| Evaluation/usage reports in package | **Files exist, current package stale** | Required files are present in root and archive, but archive versions differ and omit latest 5-check/189-test research. |
| Clean checkout execution | **Conditional / currently unverified** | Requires external Poppler. Test run failed here due missing executable; archive/root/candidate mismatch creates reproducibility risk. |
| Organizer acceptance of heuristic prediction | **Ambiguous, not established** | Contract docs correctly state no approval or partial-credit guarantee. |

The key distinction is between structural CSV validity and semantic audit validity. The project correctly measures both, but the root release presents the structurally valid file as the candidate while the stronger semantic validator rejects 49 rows. `COMPLETE`'s proof requirement is stronger than “a cited verification exists somewhere in the partial observations.”

## 7. Accuracy and Evaluation Assessment

- **Status accuracy is overinterpreted when quoted alone.** The 32/32 status result is over 32 public cases. Ten public statuses are documented as uncertain fallbacks matching the labels, and the full root run has 144 uncertain statuses. A correct public label does not prove that the status-generation rule is valid.
- **2/32 exact cases is the most revealing headline.** It says end-to-end plan completeness is poor even where statuses match. Root's documented public baseline has 129/193 matched steps (66.84% recall); the separate accepted accuracy candidate has 132/193 (68.39%). Exact cases did not improve: still 2/32.
- **Precision is less informative than it looks.** 97.78% precision means few emitted steps are unmatched in the small public reference. It does not quantify the many omitted steps, prove whole-case `COMPLETE`, or guarantee a positive hidden score. Report recall, exact sequences, empty-plan count, stronger-validator failures, and uncertainty next to it.
- **Verification omissions share multiple causes, not one universal parser defect.** The prior analysis identifies account/analytics lineage, security-retention applicability and availability, support context/full-text scope, and tombstone dependency behavior. The latest experiment adds a fifth, concrete cause: SQL `subject_selector` omitted in production matching. Generic planner changes cannot recover records that never become observations.
- **Evaluation methodology has good label separation but limited semantic independence.** Prediction is repeated before labels are read; public labels are opened only afterward. The validator proves schema, ordering, citation timing, and resource linkage for emitted steps, not exhaustiveness. The stricter validator catches some omissions but likewise cannot establish hidden truth.
- **The claimed evidence-sufficiency ceiling is too broad.** The lineage report's conclusion that no account/analytics checks can be recovered remains supported. But five connector checks were recovered because a field in available SQL was not integrated into production matching. The new opportunity is bounded and falsifiable, not a basis for guessing other links.
- **Metric drift is release evidence.** The root README says 129/132 precision and 129/193 recall; the accuracy candidate and historical report say 132/135 and 132/193. The user-reported 97.78% / 68.39% matches the separate accuracy candidate, not a verified claim about the root CSV's accompanying release artifacts.

## 8. Submission Readiness

### Root `output.csv`

Exists (431,756 bytes); exact header, 518 rows, correct sorted unique IDs, valid JSON, allowed operations/states, and no invalid cited-resource provenance. Root stronger-validator failures are 49, not 45. It is not the latest validated candidate and is not ready as the selected final answer without an explicit candidate decision.

### `code.zip`

Exists (97,789 bytes; 38 members; SHA-256 `cd014d91ffbcf470bdde1acbf96d18767de74926b425b2a45ce605b2140663b7`). ZIP integrity/member listing is valid. It is not current:

- It omits latest experiment source, tests, report, and other later tests.
- Three production modules and two tests differ byte-for-byte from the checked-out tree.
- Embedded evaluation and usage reports are older than the root reports.
- It does not contain the five-check lineage candidate or its report.
- It is not possible to infer from the ZIP alone which external `output.csv` was actually paired with it.

### Evaluation, usage, and execution

The required reports exist in the root. The root usage report documents zero model calls for the original output and the separate accuracy candidate but omits the latest lineage experiment. The root evaluation report includes earlier improvements but not the latest five-check result. The archive's reports are older still. The README advertises Poppler and an all-tests-passing state; in this environment Poppler is absent and 3 of 189 tests fail/error for that reason. No dependency was installed.

### Transcript and Git state

`log.txt` is present and contains the earlier development/experiment transcript. The checked-out branch was clean before report creation; `output.csv` and `code.zip` are present but ignored/untracked release artifacts. That is consistent with their separate-upload role, but a fresh Git checkout alone will not contain either artifact or the supplied `dataset/`; packaging instructions must be followed with the dataset mounted.

### Reproducibility conclusion

**Not ready as a coherent clean-checkout release.** The package script can rebuild an archive, and the candidate generator is documented, but the actual prebuilt ZIP and root output have not been refreshed together. A clean replay must be run after selecting a candidate, with Poppler present, and must compare the regenerated CSV hash with the intended output hash. This consultation did not run a mutating package/release command.

## 9. Previously Overlooked Opportunities

### A. Integrate stable `subject_selector` in production matching

**Specific code location:** `code/audit/identity.py:49-68`, especially the `stable` tuple at line 51.  
**Available evidence:** five connector SQL evidence files `evidence_05`, `evidence_10`, `evidence_15`, `evidence_20`, and `evidence_29`; each has one or more `DATA_FLOW` records whose `subject_selector` is the stable subject ID and whose `enabled` value is false. The full-file manifest maps these to `customer_data_read_replica_20260921.sql`, `customer_data_read_replica_20260827.sql`, `customer_data_read_replica_20260802.sql`, `customer_data_read_replica_20260708.sql`, and `customer_data_regional_replicas_20260519.sql`. The lineage experiment confirms all 11 physical copies and the five logical `VERIFY_DATA_FLOW_DISABLED` citations (`docs/historical_lineage_experiment.md:17-32`).
**Falsifiable test:** add a production-adapter fixture with a known `subject_selector=user_id`, explicit resource ID, `enabled=false`, and two physical copies; assert the audit emits the correct disabled-flow verification with admissible evidence. Add negative fixtures for an unknown selector and a conflicting stable ID; both must remain unresolved/rejected. Run the five real cases through production prediction and compare all deltas to the isolated candidate.
**Expected effect:** five supported verification steps, no status changes, no new audit-validator failures. The isolated experiment already observed this result; integration must reproduce it before promotion.

### B. Keep policy facts independent from unrelated failures

The separate tombstone improvement preserves an observed exposed-identifier violation even when an unrelated retained-record relationship is unresolved. This adds 12 steps over four full cases without deleting the stable tombstone reference. The root output lacks these improvements. Preserve this behavior and its “do not delete the tombstone” tests when rebuilding the package.

### C. Use an artifact lock/release check, not more inference

Before upload, hash the chosen `output.csv`, `code.zip`, README, evaluation report, and usage report; validate that the archive source/report files match the working tree; then run a fresh extraction and byte-compare regenerated output. This simple release manifest would have exposed the current mismatch more reliably than another benchmark iteration.

### D. Avoid low-yield speculative lineage search

The index report is persuasive that account-absence and anonymous-analytics records often lack the ownership edge needed to safely assert verification. Continue only if a new explicit selector/catalog/lineage witness is located. Do not use the public reference resource IDs as production features.

## 10. Risk Register (P0–P3)

| ID | Priority / confidence | Finding and evidence | Why it matters / expected impact | Effort | Recommended remediation and validation |
|---|---|---|---|---|---|
| R1 | **P0 / 10** | Release pair is stale. Root output hash is `b9045f0b…`; latest candidate is `51ea84c5…`. ZIP is 38 members and differs from the working tree in production files and reports. | The uploaded code, CSV, and reports do not describe the same build; 17 evidence-backed steps in the newer candidate are absent from root output. | 30–60 min | Select the intended candidate; promote output only after review; rebuild `code.zip`; refresh reports; run clean extraction and compare generated/output hashes and test counts. |
| R2 | **P0 / 10** | Prediction fallback maps no residual signal to `COMPLETE` (`prediction.py:89-106`) and can emit `[]`. Root has 144 uncertain statuses; contract demands proof for `COMPLETE`. | A status can be false while appearing to certify deletion. Sidecar uncertainty is invisible to the grader. | High / evidence-limited | Do not describe fallback rows as verified. Reassess status policy against official scoring/clarification; where evidence cannot support a status, avoid fabricating proof. Validate every `COMPLETE` against whole-case scoped verification, not just row schema. |
| R3 | **P0 / 10** | Incomplete plans remain incomplete: 49 root rows fail stronger audit validation; even separate latest candidate has 45. 302 plans are marked incomplete/unproved. | Explicit requirement for findings + complete remediation + future checks is unmet in those rows; score loss is likely. | High / evidence-limited | Fix only resolvable cases; preserve omitted facts as unknown. Re-run `validate_result` for all rows and separately report unresolved cases. No invented resource IDs or policy conclusions. |
| R4 | **P1 / 9** | Production matcher misses stable `subject_selector` (`identity.py:49-68`); isolated experiment recovers 5 connector checks from 11 copies. | Missed compliant-state verification, reduced exactness/recall, and unnecessary “evidence ceiling.” | 15–30 min + tests | Integrate typed stable selector recognition with conflict checks; use positive/negative fixtures and compare exact five case deltas. |
| R5 | **P1 / 9** | Root docs/reports are version-skewed: README says 128 tests; current suite discovers 189; root docs and isolated candidates have different metrics; ZIP contains older reports. | Judges/interviewers may be told stale counts; usage report omits latest candidate; candidate traceability suffers. | 20–40 min | Update README/evaluation/usage reports from the chosen output and actual run; ensure archive contains the current reports and any referenced documentation. |
| R6 | **P1 / 9** | The 189-test suite has 2 errors and 1 failure here because `pdftotext` is missing (`pdf_evidence.py:31-40`); README identifies it as required. | Clean setup/test run is not self-contained; evidence-sensitive paths may not execute. | 5–20 min if package available | Ensure documented Poppler installation in the evaluation environment; rerun all 189 tests and the full clean-package replay. Do not claim pass until observed. |
| R7 | **P2 / 8** | Public status metric is saturated while exact sequence is 2/32; 53 verification steps are missing from the latest public candidate according to the lineage report. | Optimizing status accuracy or precision alone hides plan incompleteness. | 10 min reporting | Lead with exact-case, step recall, empty plans, audit-validator failures, and uncertainty; separate public labels from hidden-set claims. |
| R8 | **P2 / 8** | `code/tools/package.py` has a fixed documentation allowlist and latest lineage docs are not in the current archive; current evaluation report links to later docs not packaged. | Rebuilt package can still contain broken report references and omit relevant evidence. | 10–20 min | Include all referenced/required docs or remove links; verify archive references after extraction. |
| R9 | **P3 / 7** | Lineage research maintains parallel evidence parsing/ownership logic under evaluation. | Drift can emerge between experimental and production semantics; current selector finding demonstrates the risk. | 1–3 hours | Extract shared typed selector/ownership primitives after deadline; keep experiment-only broad index separate until parity tests exist. |
| R10 | **P3 / 6** | Per-request extraction reparses shared artifacts and datasets, though measured runtime is ~24.6 s. | Modest performance and maintainability cost, not a current submission blocker. | 1–2 hours | Cache immutable parsed evidence keyed by file/hash after correctness release; preserve per-cutoff filtering and test determinism. |

Priority interpretation: P0 items block a defensible release; P1 items should be addressed before submission if feasible. R2/R3 are evidence-limited and may not be fully resolvable before deadline; that is not a reason to fabricate data.

## 11. Recommended Actions Before Submission

1. **Choose a release candidate explicitly.** The best available evidence-backed output is `artifacts/historical-lineage/candidate-full.csv`, not root `output.csv`. Review its exact row delta: 12 tombstone steps across four rows plus five connector checks across five rows; statuses unchanged.
2. **Integrate the production selector adapter narrowly.** Add only the typed `subject_selector == known user_id` case and conflict protections, then verify the five known connector resources and negative cases.
3. **Run the full suite with Poppler installed.** Current local test results are not green. Do not install packages without user approval in this consultation; make that environment step explicit in release prep.
4. **Regenerate and validate output in a temporary location first.** Compare the production run to the reviewed candidate; reject unrelated row changes and inspect all status/step deltas. Run both structural/citation validation and the stronger audit validator.
5. **Rebuild `code.zip` from the same source and reports.** Verify ZIP integrity, included test count, current source/report parity, and that internal documentation links resolve. Do not include dataset, output CSV, credentials, caches, or experiment sidecars unless separately required.
6. **Refresh all reports from that exact run.** State the final hashes, 518-row coverage, status/exact/step metrics, 140/144 uncertainty as applicable, 45/49 stronger-validator failures as applicable, actual test result, and zero runtime model calls. Do not mix candidate metrics.
7. **Perform one clean replay and release freeze.** Fresh extraction, no credentials, documented Poppler, full tests, full output generation to a temporary path, candidate validation, SHA-256 comparison, and only then upload the chosen separate artifacts.

The repository does not configure an official October deadline. Treat these as relative T-minus actions; no absolute time remaining is asserted.

## 12. What NOT to Change

- Do not map account IDs from case IDs, sequence numbers, row position, neighboring users, cohorts, or numeric similarity.
- Do not infer ownership of anonymous analytics or identity-free 404s without an admissible prior owner/resource link.
- Do not accept `reported_status`, `reported_result`, or a mutation acknowledgement as a current-state readback.
- Do not let event time override later evidence capture/availability time.
- Do not turn a security-log presence or integrity seal into an unstated retention deadline.
- Do not assume shared support context or subject-exclusive attachment ownership from category or subject matching alone.
- Do not delete an account tombstone when policy requires preserving the stable subject reference.
- Do not remove the independently supported object-storage finding merely to improve exact public matching.
- Do not present the fallback `COMPLETE` as verified compliance, or use a sidecar to claim that the grader sees uncertainty.
- Do not optimize status accuracy/precision while ignoring exact sequence, missing phases, or audit-validator failures.
- Do not overwrite the root output or archive until an explicit release candidate is selected and validated.

## 13. Final Go/No-Go Recommendation

**NO-GO for submission of the current root `output.csv` and `code.zip` as a matched release.** The CSV meets structural coverage but is stale relative to the better candidate and contains 49 stronger-audit failures; the ZIP contains older code/reports. In addition, the current `COMPLETE` fallback does not establish the required proof for 144 root cases.

**Conditional GO only after** selecting/promoting one output candidate, integrating or explicitly retaining the five-check experiment as a documented candidate, rebuilding the archive from the same source, refreshing reports, and passing a clean replay with Poppler available. This can make the release reproducible and improve known step coverage; it cannot manufacture missing account/analytics lineage or turn uncertain completion into proof.

## 14. Evidence Appendix

### Commands and read-only checks performed

- Inspected `problem_statement.md`, `AGENTS.md`, `dataset/deletion_rules.csv`, production modules, evaluation modules, tests, README, required reports, cited experiment docs, commit history, package manifest, root output, and transcript tail.
- `git show --stat 738a8d5` confirms the commit adds only evaluation lineage code, tests, a report, and the transcript; it does not alter production adapters or root submission files.
- `python3 -m unittest discover -s tests -q`: 189 discovered; two errors and one failure due missing `pdftotext`.
- Called the existing `validate_candidate.validate()` function without its write-producing CLI wrapper for root output and latest separate candidate.
- Compared ZIP member bytes with the current working tree and compared root/candidate CSV rows and hashes.
- Checked `git status` before creating these consultation reports; no production/test/root submission changes were present.

### Artifact facts

| Artifact | SHA-256 / measured result |
|---|---|
| Root `output.csv` | `b9045f0b71ec8025cfa1b67dd3b7ee5a82f7411787173743580d0f15aa9275b6` |
| Accuracy candidate CSV | `5f30a16fb7b72a914ac7489e1a06e6967d19fefaf8c992858a7470f6a3e6c25f` |
| Latest lineage candidate CSV | `51ea84c5e2b8e66af019d321421ed6d383e5e95df16244bd41af3822eb25610d` |
| Root `code.zip` | `cd014d91ffbcf470bdde1acbf96d18767de74926b425b2a45ce605b2140663b7`; 38 members |
| Root output validator | 518 rows; 0 structural/provenance errors; 144 uncertain; 302 incomplete/unproved; 49 stronger-audit failures |
| Latest candidate validator | 518 rows; 0 structural/provenance errors; 140 uncertain; 302 incomplete/unproved; 45 stronger-audit failures |
| Full tests in this environment | 189 discovered; 186 passed, 2 errors, 1 failure, all three tied to missing Poppler executable |

All data examined is participant-facing challenge material or previously generated local artifacts. No organizer-only truth, labels as prediction inputs, paid APIs, network inference, or branch/commit modifications were used.
