# Ghost Data Still Exists — competition prediction candidate

**output.csv now contains all 518 requested rows.** This is a structurally complete
competition prediction candidate, with 144 explicitly uncertain statuses and 302
incomplete/unproved plans. It is not a verified compliance report or an
organizer-approved solution. No push or submission has occurred.

Python 3.10+ and Poppler `pdftotext` are required; no Python packages, credentials,
network access or runtime model calls are needed. Install `poppler-utils` on Debian/
Ubuntu, `poppler` on macOS, or add Poppler's bin directory to PATH on Windows.
Verify with `pdftotext -v`. Place the supplied participant dataset/ beside this
README. Dataset and credentials are excluded from code.zip.

## Generate the candidate

```bash
python3 -m unittest discover -s tests -q
python3 code/main.py --all --mode prediction --output output.csv --diagnostics artifacts/prediction-run.json
python3 code/tools/validate_candidate.py
python3 code/evaluation/main.py --all-samples --mode prediction --output-dir artifacts/prediction-benchmark
```

Prediction mode preserves all 374 existing best-effort rows and fills the 144
previously unsupported requests using a fixed, label-independent heuristic.
Observed subject-linked residual PII or enabled recreation permission predicts
INCOMPLETE; otherwise it predicts COMPLETE. **No observed contradiction does not
prove completion.** The fallback does not use reported workflow status, public
answers, case-ID rules, invented resources, citations or retention dates.
Invalid inputs and identity/schema errors still fail rather than silently guess.

All steps still come from grounded policy assessments. Where no valid step is
known, the prediction can have an empty array. Such an authorized-deletion row
lacks the semantic audit content required by the statement; it is recorded as an
audit-validator failure. A status prediction is not an evidence-backed finding.
Only the required three columns go into CSV. Confidence, missing facts, residual
signals, proof-gate errors and plan gaps stay in artifacts/prediction-run.json.
Confidence is qualitative and uncalibrated, never a measured probability.

[Contract interpretation](docs/submission_contract.md) distinguishes the explicit
518-row requirement and evidence rules from our interpretation: uncertain
predictions are not explicitly banned, but partial-plan credit and organizer
acceptance are unconfirmed. The sidecar does not repair semantic shortcomings.

## Existing audit modes are preserved

```bash
python3 code/main.py --all --mode best-effort --output artifacts/audit.csv --diagnostics artifacts/audit-run.json
python3 code/main.py --all --mode strict --output artifacts/strict.csv --diagnostics artifacts/strict-run.json
```

The audit engine, policy, proof gates, validators and evidence adapters are
unchanged from e6cb761. Best-effort still supports 374/518 and exits 2 with an
explicit partial artifact. Strict supports 86/518 and also exits 2. Neither mode
turns uncertain evidence into a verified conclusion. Exit 0 in prediction mode
means every selected row passes structural/citation checks, not that every case
is proved. Partial case runs cannot overwrite root output.csv. Paths default
relative to this project; --dataset and --requests accept external absolute paths.

SQL replicas, JSON, trace-correlated logs, handover text, PDFs and hash-bound
reviewed screenshot fields supply observations. Current/historical identifiers
establish lineage and timestamps limit admissible evidence. See
[evidence sufficiency](docs/evidence_sufficiency.md) and [image review](docs/image_review.md).

## Measurements and artifacts

Public samples: **32/32 correct statuses**, **2/32 exact cases/sequences**,
**129/132 step precision (97.73%)**, **129/193 recall (66.84%)**, and **49/50
correct emitted citations (98%)**. Ten public statuses remain epistemically
uncertain despite matching labels. Five public rows fail the stronger audit
validator. No hidden total score is known. All 128 solution tests pass.

Full candidate: 160 COMPLETE, 348 INCOMPLETE, 10 NOT_APPLICABLE; 144 uncertain
statuses; 49 audit-validator failures; zero structural/citation/provenance failures.
All 374 prior best-effort rows are preserved exactly. Runtime inference: zero
calls/tokens, $0. See [evaluation](evaluation/evaluation_report.md),
[usage](evaluation/usage_report.md) and [interview briefing](docs/interview_briefing.md).

```bash
python3 code/tools/package.py
python3 code/tools/verify_package.py
python3 code/tools/export_traces.py
```

code.zip includes runnable source, tests, README, required reports and briefing/
evidence/contract documents. It excludes dataset, caches, credentials, experiments,
nested archives, output CSV and traces. output.csv is supplied separately;
artifacts/prediction-run.json is the separate local uncertainty sidecar.
The clean extracted package reproduces candidate and all three public benchmark
outputs byte-for-byte in a fresh venv without installed packages or inherited
credentials. log.txt is the transcript. agent-trace.zip is a redacted snapshot;
refresh it after closing Codex for a complete active-session trace. The official
challenge deadline is not configured in the repository.
