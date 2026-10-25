# AI Judge brief — final competition release

## 60-second architecture explanation

We resolve each deletion request against current identities and cutoff-admissible
identity history, then extract subject-linked facts from the participant evidence.
Adapters handle SQL replicas, JSON, correlated logs, text, selectable-text PDFs
through Poppler, and content-hash-bound reviewed screenshots. We preserve physical
copies and distinguish observation time from when evidence became available.
A policy engine evaluates deletion, redaction, anonymization, retention, tombstone,
connector and restore requirements. A deterministic planner orders findings,
remediation and verification under the official operation order and checks
source dependencies. Strict auditing refuses unsupported conclusions. A separate
competition predictor preserves supported results and fills evidence gaps with
explicitly uncertain status predictions. It emits no invented proof. The final
518-row CSV is reproducible from the packaged code, but 140 statuses remain
uncertain and 302 plans remain incomplete or unproved.

## Engineering decisions

- Exact typed identifiers and historical aliases establish associations. Names,
  case numbers, cohorts and row position do not assign resource ownership.
- Both capture/availability and observation must precede audit_at. Later workflow
  claims require newer readbacks; reported success alone proves no current state.
- Each replica remains separate. A disabled-flow check requires all observed
  copies to agree and one admissible citation to cover the logical verification.
- Policy predicates remain explicit. Missing retention deadlines, shared support
  context or exclusive attachment ownership remain unknown.
- Tombstones preserve stable references. Proven direct-identifier exposure can be
  redacted even when a separate retained-record relationship remains unresolved.
- The release adds exact stable subject_selector matching with conflicting-owner
  and reassignment guards. It does not activate the experimental lineage index.
- Runtime is deterministic Python/SQLite/Poppler, with no model calls, credentials
  or inference cost. AI assisted development and prior research are separate.
- Prediction fallback remains unchanged: observed residual PII or enabled recreation
  predicts INCOMPLETE; otherwise it predicts COMPLETE. That absence-of-contradiction
  rule is a competition heuristic, not proof of deletion.

## Testing and reproducibility

200 tests pass with Poppler installed, including 11 new production selector
fixtures. Fresh generation exactly matches the reviewed research candidate and a
second full run. The archive verifier checks member/source parity, integrity,
local documentation links, fresh-venv tests, all 518 predictions, structural and
citation validation, and public predictions. Credentials are stripped from replay.
Public status accuracy is 32/32, but exact cases/sequences are only 2/32. Precision
is 132/135; recall is 132/193. These figures do not establish hidden-set accuracy.

## Known limitations

45 full rows fail the stronger audit validator. Missing account absence/anonymous
analytics ownership, retention and support facts still prevent exhaustive plans.
A sidecar explains uncertainty but cannot change the grader-facing CSV meaning.
Even stronger-validator success is not exhaustive semantic certification. The
screenshot interpretations are scoped reviewed fields, not general-purpose OCR.
Unseen intent phrasing or evidence formats can fail closed. No organizer approval
of partial plans or heuristic completion is claimed.

## Ten likely questions

1. **Why is this AI-powered without runtime LLM calls?** AI assisted architecture,
   extraction review and implementation; the submitted inference path is deterministic.
   We claim no runtime LLM reasoning. A prior model experiment delivered no accepted gain.
2. **How do you know deletion is complete?** Strict auditing requires scoped account
   absence, compliant observed copies and closed evidence scope. Prediction COMPLETE
   can bypass proof gates; we explicitly do not certify those results.
3. **Why submit uncertain predictions?** The competition requires 518 status rows.
   We preserve fixed predictions and report gaps rather than fabricate evidence.
   Acceptance and scoring of partial plans remain unconfirmed.
4. **How do you use historical email addresses?** Snapshot and audit-event aliases
   are cutoff-filtered; exact stable references and conflict guards constrain linkage.
5. **How do you prevent future leakage?** Capture availability and observation/update
   times are checked against audit_at. Post-cutoff snapshots cannot backdate aliases.
6. **Why keep multiple SQL copies?** Primary and replicas can disagree. One compliant
   primary cannot prove a stale replica is clean; checks consider every supplied copy.
7. **What did the final integration change?** It preserved 12 tombstone plan steps
   and recovered five disabled-flow checks through exact stable selectors. Nine rows
   changed, 17 steps were added, no steps removed and no statuses changed.
8. **Why not recover anonymous analytics by similarity?** Anonymous state without
   prior subject/resource lineage proves no ownership. Cohorts and numeric IDs are
   insufficient, so those checks remain omitted.
9. **Why can 100% status accuracy coexist with weak exactness?** Public statuses are
   a coarse target; missing proof and plan steps reduce exact sequence accuracy and
   recall. Public samples are small and do not expose hidden-set correctness.
10. **What would you improve next?** Seek explicit ownership/state witnesses and
    policy metadata for unresolved resources, then test independently. We would not
    relax retention, infer ownership, or suppress validation failures to raise scores.
