# Five-minute interview briefing

## What the system does

The evidence audit resolves deletion intent and current/historical identifiers,
extracts participant evidence available by audit_at, evaluates policy, and plans
ordered remediation/verification. SQL replicas, JSON, trace logs, text handovers,
PDFs and hash-bound reviewed screenshots supply typed observations. Workflow
claims do not prove state. Missing lineage or retention facts are never invented.

The strict engine and best-effort mode are unchanged from e6cb761. Strict supports
86/518 requests; best-effort supports 374/518 and exposes partial-plan omissions.
Neither returns a verified conclusion from unknown facts.

## Why add a separate prediction mode?

The statement requires one row per request and scores predictions against hidden
canonical answers. It does not explicitly prohibit uncertainty, but it does require
evidence-backed steps and complete plans. We separated the structural submission
requirement from verified audit conclusions. The new user-authorized mode produces
all 518 rows, while keeping 144 uncertain statuses and 302 incomplete/unproved
plans explicit in a sidecar. Semantic acceptance and partial credit are unconfirmed;
there is no organizer approval. See docs/submission_contract.md.

The fixed fallback preserves all 374 best-effort rows. For the remaining evidence
proof gates it predicts INCOMPLETE from observed residual PII or enabled recreation
permission, otherwise COMPLETE. The latter is an absence-of-contradiction heuristic,
not proof that deletion is done. It uses no reported workflow statuses, public
answers, case-ID rules, invented resource IDs/citations or retention deadlines.
Only independently assessed verifications become steps. Unknown resources stay out.

## Actual results

Public statuses: strict 10/32, best-effort 22/32, prediction 32/32. Exact cases and
sequences stay 2/32. Step precision improves from 118/121 (97.52%) to 129/132
(97.73%); full-step recall from 61.14% to 66.84%. Citations match 49/50 emitted
witnesses. All previous matching steps/rows survive; eleven supported verifications
and ten correct status predictions are added. Rules were fixed before evaluation.

Ten public statuses remain unproved despite matching labels; five public rows
lack steps required by the stronger audit validator. Full candidate: 160 COMPLETE,
348 INCOMPLETE, 10 NOT_APPLICABLE; 144 unproved statuses. Forty-nine full-dataset
rows fail stronger audit validation, although all 518 pass structural/citation/
resource-provenance checks. There are 302 incomplete/unproved plans. Hidden score
and hidden accuracy are unknown. We do not present these predictions as compliance
certifications or as a solved evidence gap.

128 solution tests pass. Clean extraction/fresh venv reproduces the complete CSV,
unchanged best-effort partial audit and all public benchmarks byte-for-byte without
inherited credentials or installed pip packages. Runtime calls/tokens/cost are zero.
The earlier paid AI experiment was completed previously and not rerun.

## Questions to be ready for

**Does COMPLETE mean proved deletion for fallback rows?**
No. It is a competition prediction constrained by the three-label output format.
The sidecar marks low uncalibrated confidence, the missing proof, plan gaps and any
audit-validator error. The grader still interprets its status normally; the sidecar
does not repair a missing proof. This is an explicit submission tradeoff.

**Why can a complete CSV still be semantically incomplete?**
The schema requires identifiers, allowed statuses and an ordered JSON array. It
has no explicit array minLength, but the prose demands findings/proofs and a complete
plan. Empty/partial arrays pass structural parsing while falling short of that
content. We report both and claim no organizer acceptance or partial-credit guarantee.

**Why did exact cases stay low?**
Status prediction does not recover unknown account IDs, anonymous-record lineage,
retention periods or support conditions. We preserve genuine evidence rather than
inventing the canonical steps. Scoring considers several dimensions, but total
weights and the hidden score are unavailable.

## Artifacts and handoff

output.csv: structurally complete 518-row prediction candidate. code.zip: runnable
source/tests/reports and contract analysis, excluding dataset, credentials, caches,
experiment clients and output data. artifacts/prediction-run.json: separate confidence/
missing-proof diagnostics. log.txt: transcript. agent-trace.zip: redacted snapshot,
to refresh after closing Codex for complete active-session logs. Nothing is pushed
or submitted. The repository has no configured official deadline.
