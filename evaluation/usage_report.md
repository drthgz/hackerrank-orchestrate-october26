# Actual usage — final production-generated 518-row release

Final output-producing run: 518 requests, exit 0, 24.836820 seconds, 518 sorted
unique predictions. This run used the integrated production adapter and wrote
artifacts/final-release/production.csv, subsequently promoted to root output.csv.
It was not copied from the experimental candidate. Independent full repeat and
clean extraction regenerate the same bytes.

| Provider/model | Calls | Input tokens | Output tokens | Total tokens | Average tokens/request | Estimated total cost | Estimated cost/request |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| None — deterministic Python/SQLite/Poppler and reviewed evidence | 0 | 0 | 0 | 0 | 0 | $0 | $0 |
| Overall final-runtime totals | 0 | 0 | 0 | 0 | 0 | $0 | $0 |

No model provider or model name is used at runtime; per-model totals do not apply.
No paid OCR, network access or credentials are required. Tests, public benchmarks,
validation, the deterministic repeat and clean replay also make zero model calls.
Coding-assistant development usage is separate and unmeasured. No paid API calls
were made during release preparation.

Full coverage does not mean verified compliance: 140 statuses remain uncertain,
302 plans are incomplete or unproved, and 45 rows fail stronger audit validation.
Output SHA-256: `51ea84c5e2b8e66af019d321421ed6d383e5e95df16244bd41af3822eb25610d`.

## Historical development experiment — not rerun or adopted

Commit 00317fc records a prior OpenAI experiment with gpt-4.1-mini-2025-04-14:
16 completed calls, 141,986 input tokens (17,280 cached), 8,609 output tokens,
150,595 total and estimated $0.0653848 completed-call cost. Across eight requests
and two arms: 18,824.375 tokens/request, $0.0081731/request. Arm B: 69,794 input,
3,803 output, $0.0322744; arm C: 72,192 input, 4,806 output, $0.0331104.
One uncertain network attempt retained a maximum $0.0168484 reservation; completed
estimate plus that maximum was $0.0822332. These are historical rate-based estimates,
not invoice charges or final-run costs. The experiment yielded no accepted gain.
Clients, response caches and experimental run artifacts are excluded from code.zip.
