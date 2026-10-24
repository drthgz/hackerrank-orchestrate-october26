# Actual runtime usage — final deterministic full-dataset attempt

The final attempt processed all 518 requests in 24.076 seconds.
It produced 374 rows in artifacts/supported.csv, leaving 144 unsupported, and
correctly exited 2. It did not produce a complete output.csv; no successful
518-row output-producing run is claimed.

| Provider/model | Calls | Input tokens | Output tokens | Total tokens | Average tokens/request | Estimated total cost | Estimated cost/request |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| None — deterministic Python/SQLite/Poppler and reviewed evidence | 0 | 0 | 0 | 0 | 0 | $0 | $0 |
| Overall runtime totals | 0 | 0 | 0 | 0 | 0 | $0 | $0 |

There are no model providers/names in the final pipeline. No paid OCR, model API,
network access or credentials are required. Benchmark, tests, investigation and
clean-package replay also make no paid inference calls. Coding-assistant development
usage is separate and unmeasured, and is not represented as runtime usage.

Partial output SHA-256: `a6b39fd24b7d31cb70578975720a33875179561206c3262d6877b112164182a6`.
The same partial predictions are reproduced by the clean extracted package.

## Historical completed development experiment (not rerun)

Commit 00317fc records a prior local OpenAI experiment using
gpt-4.1-mini-2025-04-14: 16 completed calls, 141,986 input tokens (17,280 cached),
8,609 output tokens, 150,595 total, estimated $0.0653848 completed-call cost.
Across eight tested requests and two model arms: 18,824.375 tokens/request and
$0.0081731/request. Arm B: 69,794 input, 3,803 output, $0.0322744. Arm C: 72,192
input, 4,806 output, $0.0331104. One uncertain network attempt retained a maximum
reservation of $0.0168484; completed estimate plus that maximum is $0.0822332.
These are prior rate-based estimates, not invoice charges or final-runtime costs.
The archived experiment improved no accepted case or step; the Technical Lead
retained deterministic operation. No further paid calls were made in this work.
The experiment client, prompts, API caches and usage ledger are excluded from code.zip.
