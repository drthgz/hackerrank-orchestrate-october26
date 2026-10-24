# Ghost Data Still Exists — deterministic deletion audit

Python 3.10+ and Poppler `pdftotext` are required. No Python packages, credentials,
network access or runtime model calls are needed. On Debian/Ubuntu install
`poppler-utils`; on macOS install `poppler`; on Windows add Poppler's bin directory
to PATH. Verify with `pdftotext -v`.

Place the supplied participant `dataset/` beside this README. It is excluded from
code.zip. Paths default relative to this project, regardless of terminal cwd.

```bash
python3 -m unittest discover -s tests -q
python3 code/main.py --all --mode best-effort --output output.csv --diagnostics artifacts/submission-run.json
python3 code/evaluation/main.py --all-samples --mode best-effort --output-dir artifacts/submission-benchmark
```

**Coverage is 374/518. No valid 518-row submission exists yet.** The full command
exits 2, writes `artifacts/supported.csv` and diagnostics, and leaves root
`output.csv` absent. It writes root output atomically only if every requested case
has a defensible result. It does not turn uncertainty into a guessed status.

The 374 rows comprise 339 INCOMPLETE, 25 COMPLETE and 10 NOT_APPLICABLE.
INCOMPLETE requires an observed violation; its supported plan may still omit
unresolved resources. Such partial plans do not meet the official requirement for
a complete remediation plan. Diagnostics expose omissions and exhaustive-scope
flags. COMPLETE requires policy compliance, positive profile absence, closed
relevant scope and admissible verification citations. Non-deletion intent alone
authorizes NOT_APPLICABLE. Reported workflow success never proves state.

[Evidence sufficiency](docs/evidence_sufficiency.md) documents all original 151
blockers, seven recovered decisions, the remaining 144 cases, and the organizer
clarification needed. The output contract has no uncertainty status or documented
fallback when neither completion nor a violation can be established. No resources,
retention dates, citations or blanket fallback rows are invented.

## Evidence and policy

SQL snapshots/replicas, nested JSON, trace-correlated logs, text handovers,
selectable-text PDFs and reviewed screenshot fields become typed observations.
Current and historical identifiers establish lineage. Capture timestamps constrain
availability; observation timestamps constrain state. Flows/restores are stopped
before dependent record changes; retained records and tombstones follow policy.

Eleven screenshots have content-hash-bound field transcriptions in
`code/audit/reviewed_images.py`. These are visible evidence facts, not answer labels.
Unknown/changed screenshots remain unresolved. The object-storage attachment join
requires both a visible filename and an explicit pre-cutoff catalog ownership link.
See [image review](docs/image_review.md).

Strict mode rejects whole cases with unresolved facts:

```bash
python3 code/main.py --all --mode strict --diagnostics artifacts/strict-run.json
python3 code/main.py --case-id case_61 --mode best-effort --output artifacts/case_61.csv
```

`--dataset` and `--requests` accept external absolute paths. Partial selected-case
runs cannot overwrite root output.csv. Exit 0 means all selected rows were written;
exit 2 means unsupported cases or invalid inputs. Examine diagnostics before use.

## Measurements and packaging

The 32-case public benchmark gives 22 correct statuses, 2 exact cases/sequences,
118/121 matching emitted steps (97.52% precision), and 118/193 recall (61.14%).
Citation matches are 38/39 emitted cited steps; all emitted citations pass ID and
cutoff validation. The new attachment triple is grounded but absent from the
public canonical answer. All 119 solution tests pass. No additional paid inference
was performed; the retained deterministic runtime uses zero calls/tokens and $0.
See [evaluation](evaluation/evaluation_report.md), [usage](evaluation/usage_report.md)
and [interview briefing](docs/interview_briefing.md).

```bash
python3 code/tools/package.py
python3 code/tools/verify_package.py
python3 code/tools/export_traces.py
```

code.zip contains runnable source, tests, README, required reports and evidence
review/briefing documents. It excludes dataset, virtual environments, caches,
credentials, model experiment code/caches, nested archives and traces. log.txt is
the separate conversation transcript. agent-trace.zip is a redacted session
snapshot; refresh it after closing Codex to obtain a complete active-session trace.
The package has been tested from a clean extraction with the participant dataset
supplied externally. Its full run correctly exits 2 with the same partial output.
No push or submission has been performed. The official deadline is not configured.
