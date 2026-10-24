# Five-minute interview briefing

## What the agent does

It audits deletion requests against participant evidence at each audit cutoff.
Python adapters convert SQL replicas, JSON, readback logs, handover text, PDFs and
reviewed screenshot fields into typed observations. Historical identifiers recover
older copies. Policy decides DELETE, REDACT, ANONYMIZE or RETAIN, with flow/restore
controls ordered before record changes. Every finding has remediation and a future
check; retained and already-compliant resources also need verification.

Workflow success is only a claim. Capture time controls availability; observation
time controls state selection. Later exports cannot be used for an earlier audit.
Identity-free records need grounded lineage. Names and numbered IDs never become
invented subject/resource joins. PDF page references and screenshot source regions
remain in internal provenance.

## Competition versus strict mode

Strict mode rejects a whole case when a required fact remains unresolved.
Best-effort mode isolates unresolved resource decisions, keeps supported violations
and records omissions in diagnostics. It preserves the exact schema, ordering,
operations, states, citation cutoffs and finding/remedy/check relationships.
Unknown is never silently translated to INCOMPLETE: that needs an observed policy
violation. COMPLETE still needs sufficient proof, positive profile absence and
closed relevant scope. An unrelated reviewed image does not block everyone.

The official supplied statement requires full plans and scores completeness; it
does not expressly promise partial credit. Best-effort output is a score candidate
with known gaps, not a claim that partial plans satisfy every semantic requirement.

## Actual measurements

115 tests pass. Public valid outputs and correct statuses improved from 10/32 to
22/32. Exact cases/sequences remain 2/32. All 118 emitted step contents match;
full-public step recall improved from 30.05% to 61.14%. Missing verification steps
still prevent exact matches. Citation accuracy and citation coverage are reported
separately in evaluation/evaluation_report.md. Runtime calls, tokens and cost are zero.

The 518-request run yields 367 supported rows: 332 INCOMPLETE, 25 COMPLETE and
10 NOT_APPLICABLE. It leaves 151 unsupported. This is not a valid 518-row submission.
The CLI writes a clearly partial artifact and exits nonzero instead of fabricating
rows. Runnable source packaging is ready; final prediction coverage is not.

## Major improvements and limitations

Request-only rules now recognize clear deletion forms in six languages and explicit
preservation/non-deletion. This removes the earlier 240 full-run intent failures.
Best-effort policy isolation recovers grounded violations from cases that also lack
retention or support facts. Reviewed screenshot fields add concrete identities and
resource states. Still-present DELETION_PENDING profiles follow the unconditional
profile-deletion rule; they are not guessed to be tombstones.

The four PDFs contain selectable text, so no OCR is needed. The journal gives an
explicit security resource and deadline; the attachment gives customer ownership.
Register retention joins require exact subject/order/resource grounding. A PDF's
existence alone proves no legal retention condition.

Remaining problems are insufficient account-absence lineage, security retention
applicability, unresolved relevant media/state, and cases without admissible linked
resource observations. For example, a current security record with no supplied
deadline cannot prove legal retention or an unlawful residual record. A model
cannot manufacture that missing fact. Paid inference was not used.

## Three difficult questions

**Why not fill every unresolved case with INCOMPLETE to meet 518 rows?**
The schema has no UNKNOWN status. INCOMPLETE asserts an actual policy violation;
missing proof of completion does not establish one. Blanket filling would invent
claims. We deliver supported rows and exact blockers, and require missing evidence
or organizer clarification before calling the output valid.

**How can the output be structurally valid but not exact?**
It can correctly cite a surviving record and prescribe its remedy while missing
an account-absence, retained-resource or anonymous-record verification. Validators
check schema and internal consistency, not omniscience. We report 22 valid public
rows separately from only two exact cases and 61.14% full-step recall.

**Are screenshot transcriptions hardcoded answers?**
They store only reviewed visible fields, keyed by the source image's SHA-256.
They contain no case IDs, statuses or expected steps. Identity, policy and cutoff
logic still run normally. Unknown/changed images have no cached interpretation.
The tradeoff is corpus-specific evidence extraction rather than a general OCR
system; ambiguous ownership, access controls and future fields remain unresolved.


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
