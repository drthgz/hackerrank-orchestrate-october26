# Actual runtime usage — final 518-row prediction run

The final output-producing run processed all 518 requests in
24.608 seconds, exited 0, and wrote output.csv with exactly
518 sorted unique rows. Of these, 144 statuses are uncertain predictions and 302
plans are incomplete/unproved. Structural completion is not verified compliance.

| Provider/model | Calls | Input tokens | Output tokens | Total tokens | Average tokens/request | Estimated total cost | Estimated cost/request |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| None — deterministic Python/SQLite/Poppler and reviewed evidence | 0 | 0 | 0 | 0 | 0 | $0 | $0 |
| Overall final-runtime totals | 0 | 0 | 0 | 0 | 0 | $0 | $0 |

No model provider/name is used by the final pipeline. No paid OCR, model endpoint,
credentials or network access is required. Benchmark, tests, validation and clean
replay also use zero paid inference. Coding-assistant development usage is separate
and unmeasured. No additional paid API calls were made during this work.

output.csv SHA-256: `b9045f0b71ec8025cfa1b67dd3b7ee5a82f7411787173743580d0f15aa9275b6`.
The candidate is reproduced byte-for-byte from the clean extracted package.
The prior best-effort run remains a separate 374-row partial audit; its engine and
rows are unchanged. Its uncertainty is not hidden or counted as model usage.

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

## Separate accuracy-improvement candidate run

This later full run wrote `artifacts/accuracy-improvement/candidate-518.csv`; it did not replace root `output.csv` or `code.zip`. Requests: 518. Providers/models: none. Model calls: 0. Input tokens: 0; output tokens: 0; total tokens: 0; average tokens/request: 0. Estimated total cost: $0; per-request cost: $0. No per-model totals apply. SHA-256: `5f30a16fb7b72a914ac7489e1a06e6967d19fefaf8c992858a7470f6a3e6c25f`. The coding assistant is not a runtime model dependency.
