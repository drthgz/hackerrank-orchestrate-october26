# Submission contract interpretation — competition predictions

Sources reviewed: the supplied official problem_statement.md and AGENTS.md, in full.
No organizer clarification or approval has been obtained. This document separates
explicit requirements from the interpretation used for the prediction candidate.

| Question | Explicit text | Interpretation and limit |
| --- | --- | --- |
| Is every request required? | The statement says "Produce exactly one row" for every request and requires 518 sorted rows. AGENTS §6.3 repeats it. | Yes. There is no documented abstention exception for uncertain evidence. |
| Are uncertain predictions explicitly banned? | Neither source says that a submitted status prediction must be certain, or explicitly bans probabilistic/heuristic prediction. | Absence of a ban is not organizer approval. A heuristic prediction may be incorrect or fail semantic expectations. |
| What evidence is required? | COMPLETE requires verification proving the current state. INCOMPLETE requires findings, the complete remediation plan and checks. Findings and COMPLETE checks must cite admissible evidence. Workflow results are claims. | Uncertainty does not authorize fabricated evidence, unsupported findings or an asserted compliance proof. We preserve the strict audit behavior and label fallback statuses as unverified predictions externally. |
| Is partial-plan credit documented? | Scoring considers status correctness, identity, discovered records/risks, citations, policy, completeness and sequence. | Multiple scoring dimensions are documented; a particular partial-credit formula, acceptance policy or positive score for partial plans is not. |
| Can uncertainty stay outside CSV? | The CSV has exactly case_id,deletion_status,steps_json. steps_json is an ordered JSON array. | A separate diagnostic sidecar preserves the required CSV structure. It cannot change the meaning of COMPLETE for the grader or repair a missing plan. |
| Are empty deletion arrays structurally forbidden? | No explicit minimum JSON-array length is specified; [] is expressly required for NOT_APPLICABLE. Semantic requirements still call for proofs or findings/plans for deletion requests. | [] parses and satisfies the array/column schema, but an authorized-deletion row with [] lacks the required audit content. It is counted as a stronger-audit-validation failure and never certified complete. |

The previous handoff conflated "no defensible verified audit conclusion" with
"no permitted status prediction." Those are different. The new user-authorized
competition mode emits a prediction for every request, while the unchanged audit
engine still declines unproved conclusions. The candidate is structurally complete;
semantic compliance and organizer acceptance remain unconfirmed.

## Fixed, label-independent prediction rule

The rule was implemented and documented in code before running its public benchmark:

1. Return each existing best-effort result unchanged, including its steps.
2. Only for the four known evidence-sufficiency proof gates, inspect already
   extracted subject-linked observations available by audit_at.
3. Predict INCOMPLETE if they still show direct PII in a category subject to
   deletion/de-identification, or measured enabled recreation permission. Otherwise
   predict COMPLETE. The latter is an absence-of-contradiction heuristic, not proof
   that data is absent.
4. Keep only independently policy-assessed, evidence-backed verification steps.
   Missing resource lineage, retention applicability or support-policy facts never
   become invented steps. Empty or partial arrays are retained where necessary.
5. Record low, uncalibrated confidence, the failed proof gate, missing facts,
   residual signals, audit-validator failure and plan incompleteness in a sidecar.
   Invalid inputs, schema errors and identity conflicts still raise errors.

No reported_status, reported_result, case-ID rule, label-derived prior, quota,
private data, future capture, invented resource, citation or retention date is used
to choose a fallback status. Signal dictionaries in diagnostics are not findings.
They may indicate risk while a required policy condition remains unproved.

The COMPLETE fallback is particularly uncertain: not observing a contradiction is
not evidence of completion. Even a well-formed cited verification can cover only
one known resource while the whole-case proof is missing. It must not be represented
as a verified compliance decision to a user or downstream operational system.

## Validation boundary

The existing audit validator, planner, policy and evidence parsers are unchanged.
Prediction validation checks complete case-ID coverage, exact columns/step fields,
JSON types, uniqueness, canonical numbering/order, allowed operation/state pairs,
and admissible citations. It intentionally does not certify exhaustive plans or
whole-case proof. The reports separately count 144 uncertain full-dataset statuses,
302 incomplete/unproved plans, and 49 rows rejected by the audit validator's
stronger nonempty/phase requirements.

Future organizer clarification could require a different treatment of uncertainty
or reject empty/partial deletion plans. No such approval is implied here. The
submission remains local and has not been uploaded.
