# PDF evidence milestone evaluation

## Reproduction and isolation

Starting commit: `3f370f0`. Runtime: Python standard library + Poppler
`pdftotext` (required); `pdfinfo`, `pdfimages` and `pdftoppm` used for inspection.
No OCR, paid inference, network calls, hidden truth, generator files or dataset
edits. Predictions are attempted before the evaluator opens public sample labels.
The independent fixtures use different identifiers and timelines.

Commands:

```bash
python3 -m unittest discover -s tests -q
python3 code/evaluation/main.py --all-samples --output-dir artifacts/pdf-final
python3 code/evaluation/readiness.py > artifacts/readiness.json
```

## Before, intermediate and after

The baseline, initial PDF adapter and final validation all processed the complete
32-case public benchmark. The initial stage retained all 96 original passing
tests; the final suite adds twelve tests (108 total). Public benchmark metrics
are unchanged across all three checkpoints. No regression among any previously
emitted case: output bytes and all per-case comparison metrics are unchanged.

| Metric | Before | After |
| --- | --- | --- |
| Valid outputs | 10/32 | 10/32 |
| Correct statuses | 10/32 | 10/32 |
| Exact matches / exact sequence | 2/32 | 2/32 |
| Step precision | 100.00% | 100.00% |
| Step recall, processed cases | 81.69% | 81.69% |
| Step recall, all public cases | 30.05% | 30.05% |
| Citation accuracy, cited steps in processed cases | 100.00% | 100.00% |
| Citation recall, all public cases | 25.33% | 25.33% |
| Positional field accuracy, processed cases | 72.43% | 72.43% |
| Unsupported | 22/32 | 22/32 |
| Runtime inference cost | $0 | $0 |

58/58 emitted step contents match, against 71 expected steps in processed cases
and 193 across all public cases. All 19 non-empty citations emitted match; there
are 75 expected non-empty citations across the full benchmark. The positional
citation-field accuracy, including empty future citations, is 58/71 (81.69%).
Exact sequence accuracy is 2/32 (6.25%), or 2/10 processed cases. Structural
validity and correct status do not prove plan completeness: eight emitted plans
still omit expected verification resources. These remain partial plans.

**Direct PDF benefit:** customer attachment and retained security resource
observations now enter the typed pipeline with real file IDs, timestamps, page
references, source origin/path and identity links. Six public subjects link to
legal retention entries. **Public cases fully unblocked by PDFs: none.**
**Other changes:** a label-free 518-case readiness runner, PDF scope recognition,
exact subject/order retention joins and independent end-to-end verification tests.
None produces a measured public score gain. No unsupported label is guessed.

## Inspection of all four PDFs

`pdftotext -layout` extracted selectable text from every page. `pdfimages -list`
reported zero images for every file. They are not scans. Representative pages
were rendered with Poppler and inspected to confirm table column boundaries,
page continuation, resource references and date extraction.

| Manifest ID | Pages | Content and grounded links | Public case/cutoff |
| --- | --- | --- | --- |
| evidence_18 | 2 | Customer statement: user_18, email, statement/order references; no retention deadline or policy resource ID | No current public request resolves to user_18; no policy observation emitted |
| evidence_27 | 2 | Six subject/order register rows; reason, invoice date, retain-until date, finance initials; no legal resource ID | case_08, 12, 17, 21, 24, 29; capture 2026-05-29 08:00 UTC precedes all six cutoffs |
| evidence_55 | 1 | Explicit audit_record_003 / user_03; event recorded 2026-08-25 04:03 UTC; issued/captured 2026-09-05 06:30 UTC; retention until 2027-08-25 04:03 UTC | No public request resolves to user_03; it cannot repair unrelated missing security deadlines |
| evidence_58 | 2 | Explicit support_001, customer email and customer-uploaded address correction; submitted 2026-06-18 10:24 UTC, captured 2026-09-12 07:30 UTC | case_07 audit 2026-09-12 08:00 UTC: admissible attachment observation |

The statement remains uninterpreted for policy scope: a customer statement alone
supplies neither a deletion category/resource identity nor retention applicability.
The register does not create legal resource IDs. It supplements a separately
identified LEGAL_HOLD_RECORD only on exact subject and order reference, without
overwriting existing retention dates or an explicitly inactive hold. Recognized
dispute/chargeback/tax reasons plus an applicable date can establish the condition;
an invoice inquiry alone cannot. Date-only deadlines are conservatively parsed
at UTC midnight; applicability at later times on that date remains unproven.

The signed journal uses issue time for the observed record state, keeps its
original event timestamp separately, and uses manifest capture for availability.
The attachment uses its explicit capture time for state, preserving submission
time separately. Observation after manifest capture fails. Future-capture files
are excluded before extraction, even if embedded dates predate the audit.

## case_07 diagnostic

The PDF now proves a subject-owned attachment at support_001. Prediction next
encounters activity_4007: a separate data-catalog entry explicitly links object_19
(delivery_confirmation_19.pdf) to the same subject. That entry establishes a
resource relationship, not current state. No supported text adapter establishes
its state. The PDF filename/resource differ: merging object_19 into support_001
would fabricate a resource link. The case remains unsupported rather than
silently dropping it. The public label's account_007 verification also has no
subject-linked profile-absence readback in the currently parsed evidence.
Workflow deletion success cannot substitute for that proof. No case-specific
prediction branch or inferred numbered account ID was added.

## Additional participant-created evaluation cases

1. **Security ledger + absent account:** independent subject-k / ledger-azure PDF,
   known prior profile and empty scoped SQL snapshot. Expected COMPLETE with
   profile absence and retained-ledger verification in canonical order, each
   citing its actual witness. Pass.
2. **Customer attachment + absent account:** upload-violet PDF plus independently
   linked profile-peach NOT_FOUND readback. Expected INCOMPLETE, cited attachment
   finding, deletion, account absence verification, attachment absence verification.
   Pass; proves recovery of the otherwise-easy-to-omit compliant resource check.
3. **Legal register join:** ORD-EXAMPLE / subject-k row with explicit deadline and
   card-dispute reason supplements hold-amber. Changing order or subject prevents
   enrichment; an explicitly false legal hold remains false. Pass.
4. **Time and ownership adversaries:** a future manifest capture with an old
   embedded event is never read; observation after capture, ambiguous customer
   emails, absent attachment ID and noncustomer upload are rejected. Pass.
5. **Actual PDF transport:** a minimal independently generated selectable-text
   PDF is extracted with the real Poppler executable, not a mocked subprocess.
   Pass. The fixture text tests separately cover semantic parsing and page joins.

## Remaining public blockers and scoring recommendations

First-failure counts (later blockers may remain hidden): missing security
retention applicability 10; support context/full-text 4; no linked state evidence
3; unresolved activity resources 2; profile-absence lineage 2; media scope 1.
Unsupported cases: 01, 02, 03, 04, 07, 11, 12, 13, 14, 15, 16, 17, 18, 19,
21, 22, 25, 26, 27, 28, 31, 32.

Ranked by observed reach, with benefits as opportunities rather than promises:

1. **Additional deterministic parsing/correlation:** inventory supplied image
   content and resource/retention links before any model integration. Public
   retention failures affect ten cases; image and identity-free readbacks may
   resolve earlier provenance gaps. Audit explicit date/ownership availability;
   no parser or AI can recover facts genuinely absent from supplied evidence.
2. **Text-based interpretation for intent:** the full run exposes 240 first
   failures in intent grammar (237 outside grammar, two unresolved negations,
   one hypothetical/informational). Extend deterministic rules for clear cases,
   then measure a small bounded text-model experiment for unresolved language.
   This has greater potential coverage than more PDF work. No model or price
   chosen; paid inference remains unapproved and unused.
3. **OCR for screenshots, followed by deterministic parsing:** all four PDFs
   require no OCR. OCR is potentially useful for remaining supplied images;
   inspect representative screenshots and measure OCR field recovery first.
   It cannot prove resource ownership merely from a visually similar identifier.
4. **Vision interpretation:** justified only if observed screenshots contain
   layout/semantic facts that OCR and exact parsing cannot recover. A bounded
   pilot is reasonable to investigate, but measured score benefit is currently
   unknown. No vision or OCR deployment in this milestone.

There is no evidence-based reason for paid interpretation of these four PDFs.
Text inference for unresolved multilingual intent has a measured coverage target;
its actual accuracy, cost and provenance integration remain unmeasured.

## Submission readiness

Label-free full run attempted **518 requests**, supporting **86**,
with **432 unsupported**. All supported statuses were INCOMPLETE.

No root output.csv or fabricated rows were written. This cannot yet generate a
valid, evidence-backed 518-row submission. The selected-case CLI also deliberately
requires --case-id and prevents overwriting the final output path.

Full-run first failures:

| Reason | Cases |
| --- | --- |
| Request intent is outside the supported deterministic grammar | 237 |
| Security retention applicability not established at audit time | 106 |
| Complete account deletion requires positive scoped profile-absence evidence | 23 |
| Missing or invalid boolean fact: shared_context | 18 |
| Compliant observations do not close the unprocessed evidence scope | 14 |
| No supported evidence resource lineage links to subject | 13 |
| Missing or invalid boolean fact: text_scan_complete | 9 |
| Non-active profile requires a dedicated tombstone schema | 6 |
| Missing or invalid boolean fact: legal_hold_active | 2 |
| Unresolved negation of deletion intent | 2 |
| Informational or hypothetical wording is unsupported | 1 |
| Post-snapshot activity requires state reconstruction beyond this slice | 1 |

Required next work: expand intent coverage; resolve admissible retention and media
facts; handle tombstones and full support text; establish absence/anonymous lineage;
close scope per grounded evidence; add an all-request CLI with transactional final
output and coverage validation. Then rerun the full corpus, finish the usage report
for the actual run producing output.csv, and package from an explicit allowlist.

The required evaluation/evaluation_report.md and evaluation/usage_report.md now
exist at the AGENTS.md contract paths. README packaging includes these reports;
dataset, caches, virtual environments, secrets, and nested archives are excluded.
No code.zip was created and nothing was submitted or pushed. The usage report is
honest about the missing final prediction run; it is not submission-complete.

Estimate: 1–2 focused days for deterministic intent expansion and evidence/image
inventory, 2–4 more for scoped interpretation/correlation and full-output support,
then roughly half a day for final evaluation/packaging. This is a planning estimate,
not a guarantee: if supplied evidence lacks required links/dates, additional model
spending will not make a valid evidence-backed answer possible. A first valid
518-row candidate depends on resolving that sufficiency question.
