# Runtime AI experiment preflight — 2026-10-24

Experiment is blocked, not completed. No runtime inference was performed.
Continue from baseline commit 938035d. Source, source package, partial output,
and existing baseline metrics are preserved. No push or submission.

## Measured comparison

Selection uses public development results, not a held-out benchmark. Three
unsupported cases, four incomplete plans and one exact regression control were
selected. Labels are opened only after all deterministic predictions finish.
There are no runtime prompts or model predictions to evaluate.

| Metric | A deterministic | B model-only | C hybrid |
| --- | ---: | --- | --- |
| Status matches / selected | 5/8 | Not run | Not run |
| Exact cases | 1/8 | Not run | Not run |
| Step precision | 36/36 (100%) | Not run | Not run |
| Step recall including unsupported | 36/53 (67.92%) | Not run | Not run |
| Missing verification steps | 13 | Not run | Not run |
| Emitted citation correctness | 13/13 | Not run | Not run |
| Cited-step coverage, processed cases | 13/16 | Not run | Not run |
| Exact sequence matches | 1/8 | Not run | Not run |
| Newly resolved cases/steps | 0/0 | Unmeasured | Unmeasured |
| Runtime | 0.637s prediction | Not run | Not run |
| API cost | $0 | $0 (not run) | $0 (not run) |

Unsupported counts as unmatched in selected-case denominators. Emitted steps
match expected content with step_no ignored. Sequence accuracy compares complete
arrays; failure can reflect missing steps rather than unsafe relative ordering.
No model-validation failures were observed because there were no model outputs;
this does not establish validator effectiveness.

| Case | Purpose | A matched / expected steps | Missing verification |
| --- | --- | ---: | ---: |
| case_01 | Unsupported identity/evidence link | 0/1 | 1 |
| case_02 | Unsupported identity/evidence link | 0/1 | 1 |
| case_21 | Unsupported profile absence proof | 0/3 | 3 |
| case_05 | Already exact control | 3/3 | 0 |
| case_03 | Incomplete verification | 2/3 | 1 |
| case_11 | Incomplete policy/evidence plan | 10/14 | 2 |
| case_18 | Incomplete policy/evidence plan | 9/14 | 3 |
| case_29 | Incomplete verification | 12/14 | 2 |

## Rules, access and model check

The official event landing page permits development tools, but does not explicitly
establish runtime external API permission or judge network/credential availability:
https://www.hackerrank.com/hackerrank-orchestrate-october26
Its problem-statement link redirected to login. Both direct challenge URL variants
were inaccessible through the web tool. Local rules allow models subject to event
rules; that does not resolve the requested runtime-permission check. No API calls
were attempted. OPENAI_API_KEY is absent; no credential values were read or stored.

Official model documentation checked:
https://developers.openai.com/api/docs/models/gpt-5-mini
It lists gpt-5-mini-2025-08-07, structured outputs, and standard prices per million
tokens: $0.25 input, $0.025 cached input, $2 output. It also marks this model
deprecated. These are documented candidate rates, not an availability check or
final suitable-model selection. Choose an available inexpensive supported model
and recheck pricing before any future run. No model or parameters were used.

## Decision and remaining work

Provisionally retain deterministic-only (option 1) for the remaining 518 requests.
Measured baseline gaps remain; there is no evidence yet that runtime inference
improves them. This is an operational decision under unresolved prerequisites,
not a measured superiority claim. The existing partial coverage is not a valid
518-row submission. Do not scale inference.

To finish the authorized experiment requires official runtime API permission and
an environment-provided API key. Then implement/test the reusable client,
persistent conservative budget reservation (including ambiguous failed calls),
shared admissible evidence bundles, strict schema and semantic validators,
and separate B/C predictions before label evaluation. Bound to these eight cases
and strictly below $1. Hybrid must validate proposed facts against raw provenance,
policy, cutoffs and dependencies; reference answers must never enter inference.
No client is represented as validated or runnable yet. Ambiguous text category
coverage must be checked against request text before the final experiment.

## Reproduction

Run `python3 experiments/runtime_ai/baseline.py`. Outputs stay in this isolated
folder; baseline_results.json records per-case metrics and input hashes.
The baseline script has no network code. It imports the existing audit pipeline
without changes and uses identical request cutoffs. B/C evidence parity remains
unverified until those arms exist. Dollar amounts here cover runtime API usage
only; development-assistant usage is separate and not metered by this script.


## Retry — credential supplied

Confirmed a nonempty OPENAI_API_KEY entry in ignored .env without displaying
its value or executing file contents. Authentication has not been tested.
Rechecked the official repository rules and problem statement and searched the
official event pages. No explicit runtime external API permission was found;
the challenge page remains inaccessible. No authenticated browser tab is
available. Credential prerequisite is resolved; rules prerequisite is not.
No runtime API calls, input/output tokens, model latency or cost incurred.
The $1 authorization remains unused. No predictions or baseline metrics changed.


## Superseded by completed experiment

Local testing was subsequently explicitly authorized. See measured_report.md
for completed A/B/C results, actual token usage and estimated costs. Earlier
preflight notes above are historical.
