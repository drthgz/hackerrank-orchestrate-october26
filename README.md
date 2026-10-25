# Ghost Data Still Exists — reproducible competition submission

The final output.csv contains 518 sorted unique predictions: 160 COMPLETE,
348 INCOMPLETE and 10 NOT_APPLICABLE. It includes 2,172 steps. This is a
competition prediction submission, **not a verified compliance report**:
140 statuses are uncertain, 302 plans are incomplete or unproved, and 45 rows
fail the stronger audit validator. No organizer acceptance of these limitations
is implied. No push or submission has occurred.

## Setup and run

Python 3.10+ and Poppler `pdftotext` are required. No Python packages, credentials,
network access or runtime model calls are needed. Install `poppler-utils` on
Debian/Ubuntu, `poppler` on macOS, or put Poppler's bin directory on PATH on Windows.
Verify with `pdftotext -v`. Validation used Poppler 26.01.0.
Place the supplied participant dataset/ beside this README; it is excluded from
code.zip. Paths default to the project root. --dataset and --requests also accept
absolute paths.

```bash
python3 -m unittest discover -s tests -q
python3 code/main.py --all --mode prediction --output output.csv --diagnostics artifacts/prediction-run.json
python3 code/tools/validate_candidate.py
python3 code/evaluation/main.py --all-samples --mode prediction --output-dir artifacts/prediction-benchmark
```

200 tests pass with Poppler installed. The validator checks exact CSV/JSON fields,
coverage, canonical order, operation/state vocabulary, citation cutoff and
subject-linked resource provenance. Its separate stronger-audit count remains 45;
exit 0 in prediction mode indicates structural production, not whole-case proof.
An authorized-deletion row with [] lacks required audit content even though it
parses. The uncertainty sidecar cannot repair missing proof in the required CSV.

## Architecture and uncertainty

Current identifiers and admissible audit history resolve subjects. Explicit
SQL/JSON/log/text/PDF adapters and hash-bound reviewed screenshot fields produce
observations with physical-copy and availability/observation timestamps. Policy
requires grounded retention, redaction, anonymization and ownership facts.
The planner uses official operation ordering and rejects incompatible source
dependencies. Claims of workflow success never replace measured readbacks.

The separate prediction layer preserves supported best-effort results; at four
proof-gate failures it predicts INCOMPLETE for observed residual PII or enabled
recreation permission, otherwise COMPLETE. **No observed contradiction does not
prove completion.** This fixed fallback remains unchanged. It does not use labels,
reported workflow status, case-ID rules or invented resources/citations. Invalid
inputs and identity conflicts still fail. Missing facts and plan gaps remain in
the diagnostic JSON. Confidence labels are qualitative and uncalibrated.

Strict and best-effort audit modes still refuse unsupported whole-case conclusions:

```bash
python3 code/main.py --all --mode best-effort --output artifacts/audit.csv --diagnostics artifacts/audit-run.json
python3 code/main.py --all --mode strict --output artifacts/strict.csv --diagnostics artifacts/strict-run.json
```

An unsupported batch exits 2 and writes the supported subset to
artifacts/supported.csv rather than replacing root output.csv. Partial case runs
cannot overwrite root output.csv. Input files are never modified.

The release preserves exposed-tombstone redaction while retaining stable subject
references and adds exact stable subject_selector recognition with conflict and
reassignment protection. Relative to the prior root CSV, nine rows add exactly
17 evidence-backed steps: 12 tombstone plan steps and five disabled-flow checks.
There are no status changes, removals or unrelated row changes. The experimental
lineage engine is not imported by production.

## Evaluation and replay

Public benchmark: 32/32 status accuracy, 2/32 exact cases/sequences, step precision
132/135 (97.78%), recall 132/193 (68.39%), positional field accuracy 716/1365
(52.45%), and aligned citation correctness 50/50. Nine public statuses remain
uncertain; four public rows fail stronger audit validation. Hidden-set accuracy
and total competition score are unknown. Runtime inference uses zero calls/tokens,
with $0 total and per-request inference cost.

```bash
python3 code/tools/package.py
python3 code/tools/verify_package.py
```

Run the generation and public benchmark commands above before archive verification.
The verifier checks archive integrity, member/source parity, documentation links,
fresh-venv tests, all 518 predictions, candidate validation and public predictions.
It attaches the same external dataset and strips credentials. Both CSVs must match
the root/reference bytes. Rebuilding the archive is deterministic for fixed source.

code.zip includes source, tests, README, required reports and the judge brief.
It excludes dataset, secrets, caches, experiment run artifacts, nested archives,
output.csv and log.txt. output.csv and the authentic root log.txt are separate
submission artifacts. The final release report is external to the archive because
it records the archive's hash. Recoverable previous artifacts remain locally in
artifacts/final-release/previous-output.csv and previous-code.zip.

See [evaluation](evaluation/evaluation_report.md), [usage](evaluation/usage_report.md),
[AI Judge brief](docs/release/ai_judge_brief.md),
[contract interpretation](docs/submission_contract.md),
[evidence sufficiency](docs/evidence_sufficiency.md) and [image review](docs/image_review.md).
The official October deadline is not configured in this repository.
