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


## Completed local runtime AI comparison — 2026-10-24

Technical Lead authorized local API testing; judge network/credentials remain
unproven. Eight public cases: 01, 02, 21, 05, 03, 11, 18, 29. Labels were isolated
from inference. Accepted A/B/C status matches: 5/8, 2/8, 5/8; exact cases and
sequences: 1/8 each; step recall: 36/53, 5/53, 36/53; emitted precision: 100% each;
citation correctness: 13/13, 3/3, 13/13; missing verification: 13, 24, 13.
No newly accepted correct case or step. C uses deterministic fallback on three
rejected proposals. Raw model support-record triples match labels but do not
prove missing support-policy conditions. Recommendation: retain deterministic
operation and do not scale inference. 115 baseline + 8 experiment tests pass.

OpenAI gpt-4.1-mini-2025-04-14, temperature 0, output cap 6000, strict schema:
16 completed calls; 141,986 actual reported input tokens (17,280 cached), 8,609
output; 150,595 total, 18,824.375 tokens/tested request across both model arms.
Estimated completed-call total cost $0.0653848, per tested request $0.0081731.
B: 69,794 input / 3,803 output, $0.0322744, 27.386s summed API latency.
C: 72,192 input / 4,806 output, $0.0331104, 32.563s summed API latency.
Overall summed API latency 59.951s. One failed network attempt retains its
$0.0168484 reservation with unknown usage; estimate plus uncertain-call maximum
$0.0822332. All-attempt conservative reservations total $0.4216132, below $1.
Prices per million: input $0.40, cached $0.10, output $1.60, checked in official
OpenAI model docs. Cost is a rate-based estimate, not an invoice actual charge.
These are LOCAL EXPERIMENT numbers, not a new 518-case output-producing run;
prior full-run usage/baselines remain intact. Full details, raw diagnostics,
limitations and reproduction: experiments/runtime_ai/measured_report.md.
