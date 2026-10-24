# Ghost Data Still Exists — competition audit agent

Python 3.10+ with standard-library SQLite/JSON support and Poppler `pdftotext`.
There are no Python package dependencies, runtime model calls or credentials.

Install Poppler on Debian/Ubuntu with `sudo apt install poppler-utils`, or on
macOS with `brew install poppler`. On Windows, install Poppler and add its bin
directory to PATH. `pdftotext -v` must work from the terminal.

Place the supplied participant `dataset/` beside this README. The dataset is
intentionally excluded from code.zip. All paths default relative to this project
root; `--dataset` and `--requests` also accept absolute external paths.

## Run

```bash
python3 -m unittest discover -s tests -q
python3 code/main.py --all --mode best-effort --output output.csv --diagnostics artifacts/run.json
```

**Current coverage: 367/518. This is not yet a valid submission candidate.**
The full command currently exits **2**, lists 151 unresolved cases, and writes
only `artifacts/supported.csv` plus `artifacts/run.json`. It does not write a
misleading partial root output.csv or fill unsupported rows. Once every request
has a defensible answer, it atomically creates output.csv with exactly one row per
input case. Do not upload the current partial CSV as the required final output.

`best-effort` returns the maximum currently supported policy decisions while
recording missing policy/resource facts in diagnostics. Every emitted INCOMPLETE
requires a grounded violation, compatible remediation and verification. It never
uses unknown alone as a status. COMPLETE requires sufficient evidence, positive
profile absence, no unresolved relevant scope and valid verification citations.
Reported workflow success is never accepted as proof.

`strict` preserves conservative whole-case diagnostics:

```bash
python3 code/main.py --all --mode strict --output output.csv --diagnostics artifacts/strict-run.json
python3 code/main.py --requests dataset/sample_deletion_requests.csv --case-id case_06 --mode strict --output artifacts/case_06.csv
```

Partial selected-case runs cannot overwrite final root output.csv. For full runs,
exit 0 means all selected requests were written; exit 2 means explicit unsupported
cases or input failure. Inspect diagnostics before using any artifact.

## Evidence and policy

SQL snapshots and replicas, nested JSON, service/readback logs, text handovers and
selectable-text PDFs feed typed observations. Current/historical identifiers and
explicit resource lineage correlate the subject. Observations retain capture and
observation times, evidence IDs, source provenance and page/line origins. Future
captures and post-snapshot state uncertainty cannot silently become proof.

The eleven supplied screenshots have reviewed, content-hash-bound field
transcriptions in `code/audit/reviewed_images.py`. These are evidence artifacts,
not output labels or case-ID rules. Unknown or changed images remain unresolved.
Read [image review](docs/image_review.md) for excluded ambiguous/future fields.

Policy requires evidence of retention dates, ownership, shared support context
and other conditions. Tombstones preserve permitted stable references. Flows and
restore risks are stopped before record changes. In best-effort mode an unresolved
resource does not discard a different supported violation; omissions remain
explicit. Complete-plan accuracy is lower than structurally valid output coverage.

## Evaluate

```bash
python3 code/evaluation/main.py --all-samples --mode strict --output-dir artifacts/strict
python3 code/evaluation/main.py --all-samples --mode best-effort --output-dir artifacts/best-effort
```

The predictor never reads public labels. The evaluator opens them only after all
predictions are attempted and repeats successful predictions for reproducibility.

Current public results: **22/32** valid rows and correct statuses; **2/32** exact
cases/sequences; **118/118** emitted step contents correct; **61.14%** recall over
all public steps. All **115 tests** pass. Runtime inference costs are **$0**.
See [evaluation](evaluation/evaluation_report.md), [actual usage](evaluation/usage_report.md)
and [interview briefing](docs/interview_briefing.md) for denominators and limitations.

## Package and traces

```bash
python3 code/tools/package.py
python3 code/tools/export_traces.py
```

`code.zip` contains runnable source, tests, README, required reports, the supplied
problem statement and current briefing/review. It excludes dataset, caches,
virtual environments, credentials, nested archives and traces. Its file list and
ZIP integrity are validated by the packaging command.

`log.txt` is the required chat transcript and is provided separately.
`agent-trace.zip` contains relevant, redacted local Codex session snapshots only.
The active session snapshot is incomplete: after closing Codex, rerun the trace
export command from a terminal before uploading, as required by the supplied
agent trace instructions. No authentication/configuration stores are included.

The source archive is runnable, but submission remains blocked on 151 cases and
the missing valid 518-row output.csv. No push or submission is performed.
