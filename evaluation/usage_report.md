# Runtime model usage — PDF milestone

This milestone used deterministic Python/SQLite and local Poppler PDF extraction.
The 32-case baseline, intermediate PDF checkpoint and final benchmark all incurred
zero runtime inference usage. The final benchmark repeats successful predictions
for reproducibility. Development-assistant usage is outside these runtime totals
and has not been measured here.

| Run | Requests attempted | Supported | Providers/models | Calls | Input tokens | Output tokens | Total tokens | Average tokens/request | Estimated total cost | Estimated cost/request |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Public baseline | 32 | 10 | None | 0 | 0 | 0 | 0 | 0 | $0 | $0 |
| Initial PDF checkpoint | 32 | 10 | None | 0 | 0 | 0 | 0 | 0 | $0 | $0 |
| Final public benchmark | 32 | 10 | None | 0 | 0 | 0 | 0 | 0 | $0 | $0 |
| Full-dataset readiness audit | 518 | 86 | None | 0 | 0 | 0 | 0 | 0 | $0 | $0 |
| Overall | 614 attempts, excluding reproducibility repeats | — | None | 0 | 0 | 0 | 0 | 0 | $0 | $0 |

There are no per-model entries because no inference provider/model was invoked.
Local CPU, development time and host electricity are not inference charges.

**Submission limitation:** the 518-request readiness audit left 432 cases
unsupported and did not produce output.csv. There is no final full-dataset
prediction run to attribute to a submission artifact. Replace/extend this report
with the measured final output-producing run before submission; do not represent
this dry run as a finished 518-row prediction. No API credentials were used.
