# Final competition prediction evaluation — 2026-10-24

## Candidate and exact contract interpretation

Continued from e6cb761. The unchanged best-effort audit supports 374/518 requests;
the new, separately selected prediction mode writes **518/518** rows. Its first
implementation commit is a342529. No additional paid API calls were made.

The supplied problem_statement.md and AGENTS.md explicitly require a prediction
row for every request. Neither expressly forbids uncertain/heuristic status
predictions. They do require evidence-backed findings/verification and complete
plans. The statement lists status, records, citations, policy, completeness and
order as scoring considerations, but supplies no partial-credit formula or
acceptance guarantee for partial/empty plans. Our interpretation is that a complete
prediction CSV can meet the structural requirements while remaining semantically
incomplete. This is not organizer approval or certification of compliance. Detailed
rule-by-rule analysis: docs/submission_contract.md.

We correct the earlier conflation of an unsupported verified audit conclusion with
an impermissible competition prediction. Confidence sidecars do not change the
meaning of COMPLETE to the grader. Unproved predictions can be wrong and missing
plans can lose score or fail semantic expectations. No hidden score is claimed.

## Fixed predictor, isolated from labels

Before running the new public benchmark, the predictor was implemented with this
fixed rule: preserve each best-effort result; at the four evidence-sufficiency
proof gates, predict INCOMPLETE for observed residual direct PII or enabled
recreation permission, otherwise predict COMPLETE. Lack of contradiction is a
heuristic, not proof of absence. Existing independently assessed verification
steps survive; unknown lineage/policy produces no invented step.

The fallback reads only participant evidence at/before audit_at. It does not use
reported_status/reported_result as features, case-ID rules, public-label priors,
quotas, private truth, future evidence, fabricated resources or retention dates.
Low/high confidence labels are uncalibrated assessments, not probabilities. Invalid
input/schema/identity errors are not swallowed as uncertain predictions. The public
evaluator opens labels only after every prediction and reproducibility repeat.
No predictor rules were tuned after the measured result.

## Public benchmark — all 32 samples

| Metric | Strict audit | Best-effort baseline | Competition prediction |
| --- | ---: | ---: | ---: |
| Produced rows | 10/32 | 22/32 | 32/32 |
| Correct statuses / all cases | 10/32 (31.25%) | 22/32 (68.75%) | 32/32 (100%) |
| Exact cases / all cases | 2/32 | 2/32 | 2/32 |
| Exact sequences / all cases | 2/32 (6.25%) | 2/32 (6.25%) | 2/32 (6.25%) |
| Matching emitted steps | 58/58 | 118/121 | 129/132 |
| Step precision | 100% | 97.52% | 97.73% |
| Step recall / all 193 expected steps | 30.05% | 61.14% | 66.84% |
| Correct citations / emitted cited steps | 19/19 | 38/39 | 49/50 |
| Cited-step recall / 75 expected citations | 25.33% | 50.67% | 65.33% |
| Positional field matches / full benchmark | 360/1351 (26.65%) | 666/1365 (48.79%) | 699/1365 (51.21%) |
| First-error unsupported/no prediction | 22 | 10 | 0 |
| Structurally invalid emitted rows | 0 | 0 | 0 |
| Uncertain fallback status predictions | N/A: abstains | N/A: abstains | 10 |
| Rows rejected by stronger audit validator | 0 | 0 | 5 |

Field comparisons use max(predicted, expected) step count per case times seven,
with missing cases counted as mismatches. Three noncanonical object-storage steps
account for the precision difference; these were already in the best-effort
baseline. Positional citation fields, including empty future citations, match
124/195 (63.59%) in prediction mode. The candidate adds eleven matching supported
verification steps and ten correct status predictions; every baseline row is
preserved. There is no exact-case improvement and no baseline exact-case regression.
The prediction output repeats byte-for-byte.

The 10 fallback statuses match labels but remain unproved. Five public fallback
rows have no known steps and fail the audit validator's nonempty requirement.
Twenty public plans are flagged incomplete/unproved. Structurally valid is not
synonymous with fully supported or semantically correct.

## Full-dataset coverage and limitations

| Metric | Strict audit | Best-effort baseline | Competition prediction |
| --- | ---: | ---: | ---: |
| Produced / 518 requests | 86 | 374 | 518 |
| Unsupported with no prediction | 432 | 144 | 0 |
| Output status counts | see strict diagnostics | 25 COMPLETE / 339 INCOMPLETE / 10 NOT_APPLICABLE | 160 COMPLETE / 348 INCOMPLETE / 10 NOT_APPLICABLE |

Every one of the 374 baseline rows matches exactly. The 144 added predictions
comprise 135 COMPLETE and 9 INCOMPLETE, all low confidence and unproved. There are
302 incomplete/unproved plans (158 carried over from baseline plus 144 fallbacks).
49 rows fail stronger audit validation: 46 authorized-deletion rows have no steps;
three INCOMPLETE predictions have only supported verification and no finding/
remediation phases. Ten additional empty arrays are valid non-deletion rows.

Zero schema, ordering, duplicate-ID, citation-cutoff or resource/citation-provenance
failures were found. All step resources and cited witnesses map to subject-linked
observations in diagnostics. This checks emitted-step grounding, not completeness.
Full-dataset status/exact-case accuracy and total competition score are unmeasured
because hidden answers and scoring weights are unavailable and never accessed.

The known evidence gaps remain: missing profile lineage/absence, retention periods,
support context/full scans, attachment ownership and conflicting catalog/media
ownership. The new prediction layer does not solve these gaps or promote them into
facts. docs/evidence_sufficiency.md preserves the original blocker investigation.

## Additional participant-created evaluation cases and tests

All **128 solution tests** pass. New independent fixtures include:

1. Empty evidence yields low-confidence COMPLETE with [], while both unchanged
   audit modes still raise. No fictitious resource/check is emitted.
2. A subject-linked exposed tombstone without a proved retained-record relationship
   predicts INCOMPLETE, but no unsupported finding/remedy is created.
3. An explicitly in-period security record retains its grounded verification while
   missing profile proof keeps the whole-case status uncertain.
4. An undated security record creates no retention deadline or verification step.
5. Changing the case identifier and reported workflow status does not change the
   fallback decision. Malformed SQL/input errors still raise.
6. Fabricated/future citations and duplicate prediction rows are rejected; the CSV
   has only the official columns, with confidence confined to the sidecar.
7. Existing best-effort steps are identical after wrapping them as predictions.

Existing tests continue covering identity history, independent replicas, future
capture exclusion, trace isolation, PDF extraction, policy, canonical order,
resource lineage, claims versus readbacks and label isolation. The eight historical
experiment tests are offline/mocked and no experiment inference was rerun.

## Reproduction and clean package

```bash
python3 -m unittest discover -s tests -q
python3 code/main.py --all --mode prediction --diagnostics artifacts/prediction-run.json
python3 code/tools/validate_candidate.py
python3 code/evaluation/main.py --all-samples --mode prediction --output-dir artifacts/prediction-benchmark
python3 code/evaluation/main.py --all-samples --mode strict --output-dir artifacts/final-strict-benchmark
python3 code/tools/package.py
python3 code/tools/verify_package.py
```

The clean extraction uses a fresh venv with no pip packages and no inherited
credentials. It reruns tests, the unchanged best-effort partial audit, the 518-row
prediction run, candidate validation and all three public benchmarks. Predictions
reproduce byte-for-byte. The code archive excludes dataset, output/diagnostic data,
credentials, caches, experiment clients and nested archives. output.csv and log.txt
are separate deliverables; the uncertainty sidecar remains local. No push,
submission or organizer messaging occurred. Deadline is not configured.

Candidate output SHA-256: `b9045f0b71ec8025cfa1b67dd3b7ee5a82f7411787173743580d0f15aa9275b6`.
Public prediction SHA-256: `a671432781c8379f6400a5051bd8fe939fe8aa04264171393630dd798a5b98b9`.
Final output-producing run: 24.608s, zero model calls/tokens, $0.
See evaluation/usage_report.md for runtime and separate historical experiment usage.

## Evidence-backed improvement candidate (after d79eb59)

Separate candidate; root release artifacts remain preserved. Public statuses: 32/32 before and after. Exact cases/sequence: 2/32 before and after. Step precision: 129/132 (97.727273%) → 132/135 (97.777778%); recall: 129/193 (66.839378%) → 132/193 (68.393782%). Positional field accuracy: 699/1365 (51.208791%) → 716/1365 (52.454212%). Aligned citation correctness: 49/49 → 50/50, both 100%. Missing finding/remediation/verification steps: 5/5/54 → 4/4/53.

Recovered three case_32 tombstone steps; no newly exact public cases. Full dataset: all 518 rows, four changed cases (case_544, case_546, case_548, case_550), 12 additions, zero removals or status changes. Zero unsupported findings or provenance failures in the final integrity checks. All 147 tests pass. Added participant counterexamples include exposed versus clean tombstones with unresolved retention, missing stable subject lineage, partial versus complete support scans, and unknown versus exclusive attachment ownership. An overly narrow delivery-context matcher was caught by comparison, corrected, and covered by counterexamples before acceptance. Detailed changes, limits, all changed cases, and reproduction commands: [accuracy improvements](../docs/accuracy_improvements.md).

## Combined policy completeness experiment (91a8faf baseline)

Security-only, support-only and combined diagnostic variants each preserve public status accuracy 32/32, exact cases/sequence 2/32, precision 132/135 (97.777778%), recall 132/193 (68.393782%), positional field accuracy 716/1365 (52.454212%), and aligned citation correctness 50/50. Each preserves all 518 rows with zero changed full-dataset rows. Stronger audit-validator failures remain 4 public / 45 full; no unsupported or temporally invalid finding was introduced. No CSV policy relaxation was accepted: VERIFY_RECORD_PRESENT requires established retention, and support violation findings cannot substitute for neutral exposure facts with unresolved treatment. Evaluation-only ledgers retain these facts separately. All 163 tests pass, including 16 new counterexamples for retention, evidence cutoffs, support ownership/context and partial scans. Detailed evidence inventory and independent results: [combined policy experiment](../docs/combined_policy_experiment.md).
