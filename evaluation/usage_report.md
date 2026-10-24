# Actual runtime usage — best-effort full run

The final full-dataset attempt ran all 518 requests in 23.520
seconds on the current host. It produced 367 validated rows in
artifacts/supported.csv and left 151 unsupported. It did not
produce the required complete output.csv. This is the actual partial-output run,
not a fabricated successful submission run.

| Provider/model | Calls | Input tokens | Output tokens | Total tokens | Average tokens/request | Estimated total cost | Estimated cost/request |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| None — deterministic Python/SQLite/Poppler + reviewed evidence cache | 0 | 0 | 0 | 0 | 0 | $0 | $0 |
| Overall runtime totals | 0 | 0 | 0 | 0 | 0 | $0 | $0 |

The public benchmark and reproducibility runs also use zero inference calls,
tokens and cost. Screenshot review and coding-assistant development usage are
not runtime inference; development tokens/cost were not measured and are excluded.
No credentials, paid OCR, vision endpoint or text-model API was used.

Partial output SHA-256: `a36638ca3b4acbcb093bba472f398186d4fd28570b617575aa047b8eee48cfcb`.

Before a valid submission, rerun after all unresolved cases have defensible
answers, then update this report to identify the actual 518-row output-producing
run and its artifact hash. No such run exists yet.


## Runtime AI experiment preflight — 2026-10-24

Eight public cases were measured in isolation; deterministic status matches 5/8,
exact matches 1/8, step matches 36/53 with 100% emitted precision. B/C were not
run: runtime API permission could not be verified and OPENAI_API_KEY is absent.
Runtime API calls, input/output tokens and cost are all zero; model latency and
per-model totals are not applicable. This does not replace the full-run usage
report. See experiments/runtime_ai/report.md. No evidence relationship gains
were measured; retain deterministic operation pending a completed comparison.
