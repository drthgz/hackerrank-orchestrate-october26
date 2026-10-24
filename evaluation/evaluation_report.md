# Competition baseline evaluation — 2026-10-24

## Rules and scoring interpretation

The supplied official `problem_statement.md` requires complete plans for
INCOMPLETE cases and scores status, discovered records, risks, citations, policy,
completeness and sequence. It does **not** expressly promise acceptance or partial
credit for incomplete plans. Both the prescribed challenge URL and its standard
www problem-page variant were inaccessible to the web tool during this session;
no stronger live-rule claim is made. Best-effort partial plans are therefore
score candidates with known omissions, not certified complete solutions.

A best-effort INCOMPLETE row still requires at least one supported policy violation.
Every emitted finding has compatible remediation and future verification; all
schema, ordering, citation and cutoff validators remain enabled. Unknown records
or policy conditions are omitted with diagnostics. Unknown alone never becomes
INCOMPLETE. COMPLETE retains positive profile-absence, sufficient policy facts,
per-subject evidence-scope and citation proof gates. Strict mode remains available.

## Reproduce

Requires Python 3.10+ and Poppler pdftotext; no Python packages or credentials.

```bash
python3 -m unittest discover -s tests -q
python3 code/evaluation/main.py --all-samples --mode strict --output-dir artifacts/strict
python3 code/evaluation/main.py --all-samples --mode best-effort --output-dir artifacts/best-effort
python3 code/main.py --all --mode best-effort --output output.csv --diagnostics artifacts/run.json
python3 code/tools/package.py
```

The full run currently exits 2, writes only artifacts/supported.csv and diagnostics,
and leaves root output.csv absent. It refuses to silently fill unsupported cases.
Prediction runs before sample labels are opened. No organizer-only data, labels,
case-ID mappings or reported workflow statuses enter prediction logic.

## Measured public checkpoints

| Metric | e909b0d strict baseline | Initial best effort | Final best effort |
| --- | ---: | ---: | ---: |
| Valid output coverage | 10/32 | 20/32 | 22/32 |
| Correct statuses | 10/32 | 20/32 | 22/32 |
| Exact cases | 2/32 | 2/32 | 2/32 |
| Exact sequences | 2/32 | 2/32 | 2/32 |
| Emitted matching steps / emitted steps | 58/58 | 112/112 | 118/118 |
| Step precision | 100% | 100.00% | 100.00% |
| Step recall across all 193 public steps | 30.05% | 58.03% | 61.14% |
| Exact sequence yield across all 32 | 6.25% | 6.25% | 6.25% |
| Unsupported cases | 22 | 12 | 10 |

Final processed-case step recall: 118/157 (75.16%).
Positional field accuracy: 670/1099 (60.96%).
All 118 emitted step contents, including their citations, match.
Cited-step coverage among processed cases is 38/43
(88.37%); this penalizes missing citations, not incorrect ones.
Cited-step recall across all public cases is 38/75
(50.67%).
Positional citation-field accuracy (including future empty citations) is
114/157 (72.61%).

Exact-case improvement remains zero. Structurally valid plans still omit expected
verification resources. No previously exact public case regressed. All previous
58 matched step contents remain present; new admitted rows add supported work.
Successful predictions repeat identically in the evaluator. All 115 tests pass.

## Functional changes and observed benefit

1. Best-effort assessment isolates missing retention/support facts per resource
   instead of rejecting grounded findings for other resources. Initial public
   coverage/status matches double from 10 to 20, with 100% emitted precision.
2. Request-only grammar handles clear account-deletion formulations in English,
   Portuguese, Spanish, French, Japanese and Korean; explicit preservation and
   non-deletion requests return NOT_APPLICABLE. The 240 full-run intent first
   failures are eliminated on this corpus without using statuses or identity IDs.
3. All eleven screenshots were visually inspected. Hash-bound reviewed extraction
   now supplies visible account/search/connector/analytics/export/support/security/
   marketing facts. This is a transparent evidence cache, not a broad OCR engine.
   See docs/image_review.md for concrete ambiguities and excluded claims.
4. Best-effort scope is subject-specific: reviewed media with no grounded link to
   this subject no longer globally blocks COMPLETE. Relevant unresolved media and
   unknown/altered images remain open. Metadata-only catalog events do not mutate
   state; later state-changing claims invalidate that resource's old readback,
   while other supported findings can still be returned.
5. A still-present DELETION_PENDING row in an explicitly USER_PROFILE collection
   follows its unconditional DELETE rule in best-effort mode. It is not silently
   reclassified as a tombstone. Strict diagnostics remain conservative.
6. A full-request CLI validates all selected rows before writing atomically.
   It exits nonzero with explicit case blockers if full coverage fails. Packaging
   is allowlisted and deterministic; trace snapshots are separate from code.zip.

## Full-dataset coverage and unresolvable status gaps

Attempted 518 cases. Supported **367/518 (70.85%)**:
25 COMPLETE, 332 INCOMPLETE, 10 NOT_APPLICABLE.
Unsupported: **151**. Supported rows use exactly the required
three-column schema, sorted unique IDs, canonical phases/operations/states,
consecutive steps, compatible remedies and checks, and admissible citations.

No defensible 518-row output.csv exists. No guessed or empty INCOMPLETE rows were
created. The source package and partial output are reviewable but are not a valid
submission candidate. Schema validity of supported rows is distinct from full
coverage and semantic plan completeness.

| Remaining first failure | Cases |
| --- | ---: |
| Complete account deletion requires positive scoped profile-absence evidence | 69 |
| No evidence-backed resources to verify | 43 |
| Compliant observations do not close the unprocessed evidence scope | 26 |
| No supported evidence resource lineage links to subject | 13 |

Concrete examples from participant-facing evidence:

- case_103 / user_101: the SQL read replica contains audit_record_9522, but supplies
  no retention deadline. There is no linked deletion violation supporting an
  INCOMPLETE status, nor enough retention/account-absence proof for COMPLETE.
- case_112 / user_110: a blocked backup and redacted support text do not establish
  the missing account lineage/absence or security-retention applicability.
- case_513 / user_511: no supported evidence resource observation is admissible at
  its 2026-02-03 06:00 UTC cutoff. Later captures cannot repair that audit.

Closest rule-compliant resolution: obtain admissible missing evidence/ownership/
retention facts or organizer clarification. Continue deterministic extraction if
those facts exist in supplied artifacts. AI cannot create genuinely absent dates,
resource IDs or earlier snapshots. Do not substitute reported COMPLETE, blanket
INCOMPLETE, fabricated IDs or NOT_APPLICABLE for unresolved authorized requests.
Text-model spending is not justified as a solution to missing evidence; no paid
calls were made. Any new inference experiment still requires user approval.

## Additional participant-created tests

- An observed active profile plus a security record lacking a date produces a
  grounded three-step INCOMPLETE partial plan only in best-effort mode; the missing
  retention condition is recorded as an omission. Strict mode raises. Pass.
- That undated security record alone produces no guessed INCOMPLETE or COMPLETE
  row in either mode. Empty evidence also fails explicitly. Pass.
- Independent clear multilingual account-deletion requests and ancillary identity
  verification clauses classify correctly. Explicit preservation is non-deletion;
  contradictory/conditional deletion remains unsupported. Pass.
- A new image byte sequence has no cached interpretation; altered screenshots
  cannot reuse another image's reviewed evidence. Pass.
- A metadata-only resource-identity event cannot invalidate measured profile state.
  State-changing claims still require newer readback for that resource. Pass.
- Prior PDF fixtures cover retained security verification with profile absence,
  customer-owned attachment planning, exact legal subject/order joins, inactive
  holds, future capture exclusion and a real selectable-text PDF. Pass.

## Packaging and readiness

code.zip includes README.md, runnable code, tests, required evaluation reports,
problem_statement.md and the current briefing/image review. It excludes dataset,
virtual environments, caches, secrets, nested archives and trace archives.
Poppler is an external system dependency documented in README. Runtime uses no
Python dependencies. A clean extracted archive is tested against the externally
supplied participant dataset in a fresh Python virtual environment.

log.txt is the required conversation transcript. agent-trace.zip is a separate,
redacted snapshot of relevant Codex sessions only, not a nested source artifact.
Because this session is active, the complete trace must be refreshed after Codex
is closed, following agent_trace_instructions.md. No final trace completeness is
claimed while the app is running.

Nothing was pushed or submitted. Approval remains required before submission,
paid inference or a major architecture change. The user estimates approximately
16 hours to interview; no configured official submission deadline was found.

## Complete unsupported-case list

| Case | Blocker |
| --- | --- |
| case_103 | No evidence-backed resources to verify |
| case_107 | No evidence-backed resources to verify |
| case_108 | No evidence-backed resources to verify |
| case_111 | No evidence-backed resources to verify |
| case_112 | Complete account deletion requires positive scoped profile-absence evidence |
| case_126 | Complete account deletion requires positive scoped profile-absence evidence |
| case_127 | Complete account deletion requires positive scoped profile-absence evidence |
| case_135 | Compliant observations do not close the unprocessed evidence scope |
| case_137 | Compliant observations do not close the unprocessed evidence scope |
| case_150 | Complete account deletion requires positive scoped profile-absence evidence |
| case_151 | Complete account deletion requires positive scoped profile-absence evidence |
| case_152 | Complete account deletion requires positive scoped profile-absence evidence |
| case_155 | Complete account deletion requires positive scoped profile-absence evidence |
| case_157 | No evidence-backed resources to verify |
| case_160 | No evidence-backed resources to verify |
| case_162 | No evidence-backed resources to verify |
| case_175 | Complete account deletion requires positive scoped profile-absence evidence |
| case_178 | Complete account deletion requires positive scoped profile-absence evidence |
| case_183 | Complete account deletion requires positive scoped profile-absence evidence |
| case_190 | Complete account deletion requires positive scoped profile-absence evidence |
| case_191 | Complete account deletion requires positive scoped profile-absence evidence |
| case_204 | Complete account deletion requires positive scoped profile-absence evidence |
| case_206 | No evidence-backed resources to verify |
| case_213 | Complete account deletion requires positive scoped profile-absence evidence |
| case_215 | Complete account deletion requires positive scoped profile-absence evidence |
| case_218 | Complete account deletion requires positive scoped profile-absence evidence |
| case_219 | Complete account deletion requires positive scoped profile-absence evidence |
| case_221 | Complete account deletion requires positive scoped profile-absence evidence |
| case_225 | Complete account deletion requires positive scoped profile-absence evidence |
| case_226 | Complete account deletion requires positive scoped profile-absence evidence |
| case_231 | Complete account deletion requires positive scoped profile-absence evidence |
| case_233 | Compliant observations do not close the unprocessed evidence scope |
| case_235 | Compliant observations do not close the unprocessed evidence scope |
| case_243 | Complete account deletion requires positive scoped profile-absence evidence |
| case_244 | Complete account deletion requires positive scoped profile-absence evidence |
| case_253 | No evidence-backed resources to verify |
| case_257 | No evidence-backed resources to verify |
| case_260 | No evidence-backed resources to verify |
| case_264 | Compliant observations do not close the unprocessed evidence scope |
| case_265 | Compliant observations do not close the unprocessed evidence scope |
| case_267 | Compliant observations do not close the unprocessed evidence scope |
| case_274 | Complete account deletion requires positive scoped profile-absence evidence |
| case_276 | Complete account deletion requires positive scoped profile-absence evidence |
| case_277 | Complete account deletion requires positive scoped profile-absence evidence |
| case_292 | Compliant observations do not close the unprocessed evidence scope |
| case_294 | Complete account deletion requires positive scoped profile-absence evidence |
| case_295 | Complete account deletion requires positive scoped profile-absence evidence |
| case_297 | Complete account deletion requires positive scoped profile-absence evidence |
| case_299 | Complete account deletion requires positive scoped profile-absence evidence |
| case_304 | No evidence-backed resources to verify |
| case_308 | Complete account deletion requires positive scoped profile-absence evidence |
| case_309 | No evidence-backed resources to verify |
| case_313 | Complete account deletion requires positive scoped profile-absence evidence |
| case_314 | Complete account deletion requires positive scoped profile-absence evidence |
| case_319 | Complete account deletion requires positive scoped profile-absence evidence |
| case_322 | Complete account deletion requires positive scoped profile-absence evidence |
| case_324 | Compliant observations do not close the unprocessed evidence scope |
| case_326 | Compliant observations do not close the unprocessed evidence scope |
| case_331 | Compliant observations do not close the unprocessed evidence scope |
| case_335 | Complete account deletion requires positive scoped profile-absence evidence |
| case_336 | Complete account deletion requires positive scoped profile-absence evidence |
| case_339 | Complete account deletion requires positive scoped profile-absence evidence |
| case_343 | Complete account deletion requires positive scoped profile-absence evidence |
| case_345 | Complete account deletion requires positive scoped profile-absence evidence |
| case_346 | Complete account deletion requires positive scoped profile-absence evidence |
| case_351 | Complete account deletion requires positive scoped profile-absence evidence |
| case_354 | No evidence-backed resources to verify |
| case_362 | No evidence-backed resources to verify |
| case_369 | Compliant observations do not close the unprocessed evidence scope |
| case_383 | Compliant observations do not close the unprocessed evidence scope |
| case_390 | Compliant observations do not close the unprocessed evidence scope |
| case_392 | Compliant observations do not close the unprocessed evidence scope |
| case_393 | Complete account deletion requires positive scoped profile-absence evidence |
| case_395 | Complete account deletion requires positive scoped profile-absence evidence |
| case_398 | Complete account deletion requires positive scoped profile-absence evidence |
| case_403 | No evidence-backed resources to verify |
| case_408 | No evidence-backed resources to verify |
| case_409 | No evidence-backed resources to verify |
| case_41 | Compliant observations do not close the unprocessed evidence scope |
| case_411 | No evidence-backed resources to verify |
| case_412 | No evidence-backed resources to verify |
| case_423 | Complete account deletion requires positive scoped profile-absence evidence |
| case_424 | Complete account deletion requires positive scoped profile-absence evidence |
| case_427 | Complete account deletion requires positive scoped profile-absence evidence |
| case_430 | Complete account deletion requires positive scoped profile-absence evidence |
| case_44 | Compliant observations do not close the unprocessed evidence scope |
| case_448 | Complete account deletion requires positive scoped profile-absence evidence |
| case_45 | Complete account deletion requires positive scoped profile-absence evidence |
| case_452 | Complete account deletion requires positive scoped profile-absence evidence |
| case_456 | No evidence-backed resources to verify |
| case_457 | No evidence-backed resources to verify |
| case_458 | No evidence-backed resources to verify |
| case_46 | Compliant observations do not close the unprocessed evidence scope |
| case_460 | No evidence-backed resources to verify |
| case_462 | No evidence-backed resources to verify |
| case_463 | Complete account deletion requires positive scoped profile-absence evidence |
| case_464 | Complete account deletion requires positive scoped profile-absence evidence |
| case_467 | Complete account deletion requires positive scoped profile-absence evidence |
| case_470 | Complete account deletion requires positive scoped profile-absence evidence |
| case_479 | No evidence-backed resources to verify |
| case_480 | Complete account deletion requires positive scoped profile-absence evidence |
| case_484 | No evidence-backed resources to verify |
| case_493 | Complete account deletion requires positive scoped profile-absence evidence |
| case_494 | Complete account deletion requires positive scoped profile-absence evidence |
| case_497 | Complete account deletion requires positive scoped profile-absence evidence |
| case_502 | Complete account deletion requires positive scoped profile-absence evidence |
| case_503 | No evidence-backed resources to verify |
| case_506 | No evidence-backed resources to verify |
| case_508 | No evidence-backed resources to verify |
| case_51 | Compliant observations do not close the unprocessed evidence scope |
| case_512 | No evidence-backed resources to verify |
| case_513 | No supported evidence resource lineage links to subject |
| case_514 | No supported evidence resource lineage links to subject |
| case_515 | No supported evidence resource lineage links to subject |
| case_516 | No supported evidence resource lineage links to subject |
| case_517 | No supported evidence resource lineage links to subject |
| case_518 | No supported evidence resource lineage links to subject |
| case_519 | No supported evidence resource lineage links to subject |
| case_520 | No supported evidence resource lineage links to subject |
| case_521 | No supported evidence resource lineage links to subject |
| case_522 | No supported evidence resource lineage links to subject |
| case_524 | Complete account deletion requires positive scoped profile-absence evidence |
| case_530 | Complete account deletion requires positive scoped profile-absence evidence |
| case_532 | Complete account deletion requires positive scoped profile-absence evidence |
| case_543 | No evidence-backed resources to verify |
| case_544 | No evidence-backed resources to verify |
| case_545 | No evidence-backed resources to verify |
| case_546 | No evidence-backed resources to verify |
| case_547 | No evidence-backed resources to verify |
| case_548 | No evidence-backed resources to verify |
| case_549 | No evidence-backed resources to verify |
| case_55 | No supported evidence resource lineage links to subject |
| case_550 | No evidence-backed resources to verify |
| case_57 | Complete account deletion requires positive scoped profile-absence evidence |
| case_58 | No evidence-backed resources to verify |
| case_59 | No evidence-backed resources to verify |
| case_60 | No evidence-backed resources to verify |
| case_61 | No supported evidence resource lineage links to subject |
| case_63 | No supported evidence resource lineage links to subject |
| case_64 | Complete account deletion requires positive scoped profile-absence evidence |
| case_69 | Complete account deletion requires positive scoped profile-absence evidence |
| case_70 | Complete account deletion requires positive scoped profile-absence evidence |
| case_76 | No evidence-backed resources to verify |
| case_77 | Compliant observations do not close the unprocessed evidence scope |
| case_81 | Compliant observations do not close the unprocessed evidence scope |
| case_82 | Compliant observations do not close the unprocessed evidence scope |
| case_83 | Compliant observations do not close the unprocessed evidence scope |
| case_84 | Compliant observations do not close the unprocessed evidence scope |
| case_86 | Compliant observations do not close the unprocessed evidence scope |
| case_88 | Compliant observations do not close the unprocessed evidence scope |
| case_97 | Complete account deletion requires positive scoped profile-absence evidence |
