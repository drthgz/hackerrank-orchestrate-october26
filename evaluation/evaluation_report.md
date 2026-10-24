# Submission completion evaluation — 2026-10-24

## Result and contract

Continued from commit 00317fc and retained the deterministic pipeline. No additional
paid inference calls were made. The full run produces **374/518 (72.20%)** supported
rows, up from 367/518. **144 cases remain unsupported**, so root output.csv is absent.
This is a runnable review package, not a valid complete competition submission.
339 INCOMPLETE, 25 COMPLETE and 10 NOT_APPLICABLE statuses are emitted.
Of the emitted deletion rows, 158 have explicit policy/state omissions and 206
are flagged exhaustive by the current extractor; the latter flag is diagnostic,
not measured hidden-answer completeness. Ten non-deletion rows need no plan.

The supplied official problem_statement.md requires 518 rows and complete plans.
AGENTS.md §6.3–6.6 requires evidence-backed states at audit_at and prohibits
fabricated evidence. Neither supplied document defines UNKNOWN or an uncertainty
fallback. Unknown cannot become INCOMPLETE without a violation, COMPLETE without
proof, or NOT_APPLICABLE for an authorized deletion. Partial plans may have grounded
statuses but are not certified complete plans; partial-credit scoring is unspecified.
See docs/evidence_sufficiency.md for exact conflicts and organizer questions.
No organizer-only data or labels enter prediction. No live organizer clarification
has been obtained and no message has been sent. Deadline is not configured.

## Public benchmark: all 32 cases

Predictions are completed before the evaluator opens sample_output.csv. Every
successful prediction is repeated and compared for determinism.

| Metric | Commit 00317fc baseline | Current |
| --- | ---: | ---: |
| Produced / all public cases | 22/32 | 22/32 |
| Correct statuses / all public cases | 22/32 (68.75%) | 22/32 (68.75%) |
| Correct statuses / produced | 22/22 | 22/22 |
| Exact cases and exact sequences / all cases | 2/32 (6.25%) | 2/32 (6.25%) |
| Matching emitted step contents | 118/118 | 118/121 |
| Step precision | 100% | 97.52% |
| Step recall / all 193 public steps | 118/193 (61.14%) | 61.14% |
| Step recall / 157 steps in produced cases | 75.16% | 75.16% |
| Positional field accuracy | 670/1099 (60.96%) | 666/1113 (59.84%) |
| Positional citation-field accuracy | 114/157 (72.61%) | 113/159 (71.07%) |
| Citation match / emitted cited steps | 38/38 | 38/39 (97.44%) |
| Cited-step recall / all cited public steps | 38/75 (50.67%) | 38/75 (50.67%) |
| Full-dataset supported coverage | 367/518 | 374/518 |

All 118 previously matching step contents remain. The catalog-backed object_19
finding/remedy/check triple adds three noncanonical public steps; the same join
recovers full-dataset case_61 with a supported violation. This small precision
tradeoff is retained because both presence and sole ownership have admissible
witnesses. It creates no new status/sequence regression, and does not replace
measured facts with missing canonical lineage. No exact-case gain is claimed.

Citation correctness above compares against canonical answers; structural citation
validity checks only that IDs exist, cutoffs are respected and future-work citations
are empty. Neither metric alone establishes full semantic correctness. Full-dataset
status/exact-case accuracy is unmeasured because hidden answers are not accessed.

## Evidence investigation and limitations

Pipe-delimited logs previously lost their service/trace/event headers. Recovering
those headers establishes observations for ten originally unlinked cases: six now
support INCOMPLETE, four move to unresolved policy/scope gaps. The attachment join
recovers one further decision using evidence_46 plus activity_4007. It uses the
screenshot for presence and catalog metadata for ownership/resource lineage.

All original 151 unsupported cases were reviewed with raw identifier/resource
searches across the 94 participant evidence files, current/historical identifiers,
parsed observations and policy omissions. Later captures are listed separately
and excluded from proof. Raw hits do not automatically prove state or ownership.
Machine detail: artifacts/evidence-sufficiency.json. Portable case dispositions:
docs/evidence_sufficiency.md, included in code.zip.

Remaining first blockers: 69 missing positive profile-absence proofs; 43 no
policy-assessable verification resource; 30 unresolved scope; 2 missing/conflicting
lineage. Independent gaps overlap these counts: missing supplied retention periods,
shared support context, full text scans, attachment ownership and tombstone/retained
record relationships. First failures do not describe all missing facts.

For example, case_103 has an undated security record in evidence_10 and no supported
violation. Neither an integrity seal nor a reported success supplies a retention
deadline. case_55 has a backup without restore authorization; case_63 has conflicting
screenshot/catalog ownership. No safe fallback covers these authorized requests.
The CLI preserves exit 2 and explicitly refuses to fabricate a 518-row file.

## Participant-created evaluation cases

All 119 solution tests pass, including these independent fixtures with arbitrary
identifiers (no public labels):

1. Interleaved pipe-format traces read two subjects; only the matching subject's
   scoped 404 becomes profile absence. Trace/service/instance isolation is retained.
2. A visible attachment filename plus exact catalog resource/sole-owner metadata
   creates a grounded attachment observation with both witnesses in provenance.
3. The same ownership event after audit_at yields no attachment observation.
4. A catalog filename absent from the screenshot yields no presence observation.
5. An active profile plus an undated security record produces only a grounded
   partial INCOMPLETE plan in best-effort mode; strict rejects missing policy facts.
6. An undated security record alone yields no guessed COMPLETE/INCOMPLETE result.

Existing tests also cover replica drift, future capture exclusion, historical
identifiers, redaction/anonymization fields, tombstones, retention joins, mutation
claims versus readbacks, canonical order, and label isolation.

## Reproduction and package validation

```bash
python3 -m unittest discover -s tests -q
python3 code/main.py --all --mode best-effort --diagnostics artifacts/submission-run.json
python3 code/evaluation/main.py --all-samples --mode best-effort --output-dir artifacts/submission-benchmark
python3 code/evaluation/investigate.py --run artifacts/submission-run.json
python3 code/tools/package.py
python3 code/tools/verify_package.py
```

Optional --baseline artifacts/competition-run.json reconstructs the original 151-case
recovery comparison in the development checkout. That baseline is not a predictor
input or a package dependency. Standalone investigation reports current blockers.

The clean extracted package runs in a fresh Python virtual environment without
pip packages, using external participant data and system Poppler. All 119 tests
pass, benchmark predictions reproduce byte-for-byte, and the full run exits 2 with
374 supported rows and the same SHA-256 below. No dataset, caches, credentials,
experiment clients or nested archives are in code.zip. No push or submission.

Partial-output SHA-256: `a6b39fd24b7d31cb70578975720a33875179561206c3262d6877b112164182a6`.
Public-prediction SHA-256: `4a40ddc20c7286a01cda1047241f3c8e324191aed21f1569306d2daf802b8f81`.
Runtime details: evaluation/usage_report.md. The previous completed AI experiment
is historical development evidence only and is not imported or rerun.
