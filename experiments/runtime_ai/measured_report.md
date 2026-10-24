# Eight-case local runtime AI experiment — measured results

Completed after explicit Technical Lead authorization for local API calls.
Starting baseline: 938035d; isolated preflight commit: f6a4942. Runtime external
API permission was accepted for LOCAL testing on the user's instruction. No judge
network or credentials are assumed. No production inference path was enabled,
no source package or partial output regenerated, and nothing pushed or submitted.

## Design and evidence boundary

Cases: case_01, case_02, case_21 (previously unsupported); case_05 (exact control);
case_03, case_11, case_18, case_29 (incomplete verification/plans). case_21 asks to
verify a previously deleted profile and required security retention, testing
ambiguous request/policy interpretation; case_11 and case_18 test support-record
policy relationships. Selection is informed by public development results. Eight
cases do not establish independent generalization accuracy.

A runs the unmodified best-effort pipeline. B uses model reasoning over the actual
request, recovered identifiers, rules, admissible artifact excerpts, activity,
and extracted observations; it gets no deterministic plan. C gets the same
bundle plus the deterministic plan or explicit failure, proposes a plan, then
uses deterministic validation. This is a constrained proposal-and-validation
hybrid, not a new free-form evidence extractor.

Public labels are opened only by evaluate.py, after all inference calls finish.
No expected outputs enter prompts. Only participant-facing data is used.
Manifest capture times and observations use each request's audit_at. Relevant
files are found through identifiers and explicit activity/resource links. Global
exports are excerpted or filtered to records; small relevant files retain decoys.
B/C share identical bundles. Restricting A to the selected source-file set was
checked to yield the identical A result/blocker for all eight cases, and every
supplied observation's provenance is in its bundle. A and C validation were also replayed with activity restricted to the same
bundle activity list; results and blockers remained identical for all eight.
A still parses those files rather than reasoning over prose excerpts. This controls source scope and cutoff,
not identical internal representations.

## Accepted results

Unresolved or rejected cases count as unmatched, never fabricated output rows.
Step content ignores step_no; exact sequence compares the full ordered array.
Missing verification counts expected verification content absent from output,
including a wrong citation as missing proof. Citation correctness here means
emitted cited-step content matches the public label; it is not mere ID existence.

| Metric | A deterministic | B model-only + output gate | C hybrid + fallback |
| --- | ---: | ---: | ---: |
| Correct statuses | 5/8 (62.50%) | 2/8 (25.00%) | 5/8 (62.50%) |
| Exact cases | 1/8 (12.50%) | 1/8 (12.50%) | 1/8 (12.50%) |
| Exact sequences | 1/8 (12.50%) | 1/8 (12.50%) | 1/8 (12.50%) |
| Step precision | 36/36 (100.00%) | 5/5 (100.00%) | 36/36 (100.00%) |
| Step recall | 36/53 (67.92%) | 5/53 (9.43%) | 36/53 (67.92%) |
| Citation correctness | 13/13 (100.00%) | 3/3 (100.00%) | 13/13 (100.00%) |
| Positional field accuracy | 177/371 (47.71%) | 35/371 (9.43%) | 177/371 (47.71%) |
| Missing verification steps | 13 | 24 | 13 |
| Newly accepted correct cases/steps versus A | 0/0 | 0/0 | 0/0 |

C fell back to the original deterministic result for case_05, case_11, case_18;
case_03 and case_29 proposals passed independently; the three original unsupported
cases remained unsupported. The hybrid therefore adds expense with no accepted
accuracy gain on this selection.

| Case | A correct status / matched steps | B correct status / matched steps | C correct status / matched steps |
| --- | --- | --- | --- |
| case_01 | no/0 | no/0 | no/0 |
| case_02 | no/0 | no/0 | no/0 |
| case_21 | no/0 | no/0 | no/0 |
| case_05 | yes/3 | yes/3 | yes/3 |
| case_03 | yes/2 | yes/2 | yes/2 |
| case_11 | yes/10 | no/0 | yes/10 |
| case_18 | yes/9 | no/0 | yes/9 |
| case_29 | yes/12 | no/0 | yes/12 |

## Raw proposals and investigation of apparent gains

Raw B: 6/8 statuses, 1/8 exact cases, 39/53 matching steps (73.58% recall),
39/53 precision, 15/27 correct cited steps. It adds seven label-matching steps
while losing four baseline matches. Raw C: 5/8 statuses, 0/8 exact cases,
41/53 matching expected steps (77.36% recall), 41/67 precision, 15/23 correct
cited steps. It adds six matching steps while losing one baseline match.
These are diagnostics of rejected proposals, not safe output performance.

Both models proposed the finding/remediation/verification triple for support_864
(case_11, evidence_03) and support_5569 (case_18, evidence_94), matching the public
labels. The artifacts directly tie the subject's email to an identifiable support
record. However these links were already present in A's extracted observations.
A omitted the treatment because the supplied observation lacked shared-context
facts required by the support REDACT policy. The model did not recover an
independently proven new ownership relationship or supply the missing retention
condition. Matching a label is insufficient evidence to bypass that gate.

B also proposed the expected retained-security verification for audit_record_3737
(case_21, evidence_92). A already extracted that record and its 2034 retention
limit; the case was blocked by missing positive scoped profile-absence evidence.
The additional check is supported locally but does not establish COMPLETE scope.
C instead invented account_21 and other unsupported resources. No new exact case
or accepted step survived the full validation boundary.

## Validation and safeguards

B applies schema, consecutive numbering, operation/state, phase and canonical
order, resource/system presence, citation/resource binding, capture cutoff and
finding/remediation/verification compatibility gates. It is an experimental
model-only reasoner, not a production semantic guarantee. A valid citation ID
alone never authorizes an unknown resource.

C additionally accepts only treatments independently grounded by existing
Observation/policy adapters, discards stale readbacks using later state-changing
claims, checks intent and COMPLETE scope, and delegates policy/dependency safety
to the existing planner. Novel free-form model facts remain untrusted and cannot
be promoted. C repairs serialization order and clears future-work citations
before semantic checks. These two label-independent repairs plus deterministic
fallback were added after inspecting initial validation failures, with no extra
API calls. Raw C results are retained to make this development adjustment visible.

B rejected six of eight responses (two UNRESOLVED, four canonical-order failures).
After serialization repair C rejected six proposals (two UNRESOLVED, invented
resource account_21, invalid/future citation, orphan finding, unproved support
policy); three of those use valid deterministic fallback. Initial raw C also
had canonical-order and nonempty future-citation errors. Early-exit validators
report the first failure, not an exhaustive defect count. Eight custom regression
tests cover conservative budget refusal, persistent uncertain failures, cache
reuse, invented resources, future citations, invalid states, incorrect resource
binding and unproved policy. All 115 existing tests also pass (123 combined).

## Model, parameters, actual usage and estimated cost

Provider: OpenAI. Exact requested and API-returned model:
`gpt-4.1-mini-2025-04-14`. Temperature 0; max_completion_tokens 6000;
strict json_schema; store=false; no tools; no automatic retries.
The snapshot is marked deprecated in official docs but was available for all 16
successful calls. Do not assume future availability. Pricing checked 2026-10-24:
$0.40/M input, $0.10/M cached input, $1.60/M output:
https://developers.openai.com/api/docs/models/gpt-4.1-mini
Structured output reference:
https://developers.openai.com/api/docs/guides/structured-outputs

Token counts below are actual API-reported usage. Costs are estimates calculated
from those counts and documented prices, not an invoice or billing reconciliation.

| Arm | Successful calls | Input tokens | Cached input (included) | Output tokens | Estimated USD | Sum API latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B | 8 | 69,794 | 5,760 | 3,803 | $0.0322744 | 27.386s |
| C | 8 | 72,192 | 11,520 | 4,806 | $0.0331104 | 32.563s |
| Overall | 16 | 141,986 | 17,280 | 8,609 | $0.0653848 | 59.951s |

Total tokens: 150,595; average 9,412.19 per completed call and
18,824.38 per tested request across B+C. Estimated cost per tested request:
$0.0081731. A used zero runtime model calls/tokens/dollars;
its recorded eight-case prediction time was 0.637s.
API latencies exclude extraction, validation, evaluation and developer time;
end-to-end authoring wall time was not instrumented. Cached replays make no calls.

One initial sandbox network attempt failed with URLError before a response.
Its $0.0168484 reservation remains because usage is not available. Sixteen later
authenticated calls completed; 17 attempted network requests in total. Conservative
reservations across ALL attempts total $0.4216132.
Estimated completed-call cost plus the uncertain-attempt maximum is $0.0822332,
still below $1. No invoice-level actual charge is claimed.

The persistent ledger reserves a UTF-8-byte token ceiling plus framing allowance
and the full output cap BEFORE transmission, under an exclusive lock. It never
refunds ambiguous failures, refuses reservation sums reaching $1, and caps
completed calls at 16. No retries, tools, image uploads or unbounded token modes.
The key is parsed as data from ignored .env into process environment, never
sourced, printed, written to results or committed. Development-assistant usage
is separate and is not included in these runtime measurements.

## Recommendation and remaining submission blockers

Choose option 1: retain deterministic-only for the final 518-request run under
current time constraints. C preserves quality through fallback but adds no
accepted steps/cases, while B degrades accepted coverage. A future extraction
experiment could target grounded policy-context interpretation, but this run
does not justify scaling inference or assuming missing evidence. No further
paid calls are authorized by this experiment.

Baseline blockers remain: only 367/518 supported rows, 151 unsupported cases,
no valid full 518-row output.csv, and incomplete public verification plans.
Judge API credentials/network and future snapshot availability remain unproven;
the source package remains deterministic and offline. Existing code.zip and
partial outputs were protected, not repackaged or submitted. Any later packaging
must deliberately include the new reports if desired. The experiment is local
and isolated from code/main.py.

## Reproduction and artifacts

`python3 experiments/runtime_ai/evaluate.py` recomputes metrics from saved
predictions without credentials, network, or inference. Run regression tests with
`python3 -m unittest discover -s tests -q` and
`python3 -m unittest discover -s experiments/runtime_ai -p 'test_*.py' -q`.

`run.py` is the optional local inference entry point; it is fixed to eight public
cases and two arms, and uses successful response caches when available. The
committed ledger prevents a fresh checkout from silently repeating paid calls
once its 16 completions are recorded. Do not clear that ledger to evade the cap.
Evidence bundles and per-call response caches remain ignored local artifacts;
predictions.json, comparison.json and calls/usage.json preserve results/usage.
Prompts are source in run.py; file hashes below identify frozen local bundles.
Evaluation code alone reads labels. Labels and caches are not runtime examples.

| Local bundle | SHA256 |
| --- | --- |
| case_01_bundle.json | 2f3e02c0d1e7237c847f9e9039c5714e588981f71ca9d28103ddbd31fdcd9fab |
| case_02_bundle.json | 241b93512e87995498fd6ced603871d1e67ec977ff8e991de241f3e2fab6b23e |
| case_03_bundle.json | 522e0fb300c931abdc9715d003ea811507147fb62cfd19979f36e513a75537a0 |
| case_05_bundle.json | 22f76ca17d8ab4287bf5079f65478c7a63c90a680e5600024ab5ea2be6b457c5 |
| case_11_bundle.json | 3d51d160d9e3388e4aab07df1e7c9c5e0d213a6f089aae4c989610de5a2ee858 |
| case_18_bundle.json | 2b77a751d9e763d9d6078578e0b1d9ae36df50f8658147b1440a61c5dcd84bc5 |
| case_21_bundle.json | f28e411f63ec238efd7af7a0d57daca9bcb7d3364de01e3a1c88ea7d901bcfc1 |
| case_29_bundle.json | 9a27318ab19df004d253b7e65ad01699e3aab1c3000326608073f108edf4d4b9 |
