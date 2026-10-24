# Requirements discovery and proposed architecture

Date: 2026-10-24. Historical phase-1 status: discovery complete; architecture proposed. The Technical Lead subsequently approved the architecture and SQL vertical slice in Prompt 2, and structured-evidence/status expansion in Prompt 3. This document records discovery findings; current capabilities and measured results are in structured_evaluation.md.

## 1. Sources and baseline

Read in full: `AGENTS.md`, `problem_statement.md`, `README.md`, `agent_trace_instructions.md`, and `CLAUDE.md` (which delegates to AGENTS). Only the root AGENTS file was found. Source references below refer to this checkout, not a live contest-page verification.

Initial branch: `main`; initial HEAD: `acb3dfc`; working tree initially clean. `code/main.py` and `code/evaluation/main.py` are both zero-byte placeholders. There is no supplied runnable reference solution, grader, test suite, dependency manifest, or generator directory in this checkout. AGENTS §7 mentions generator validators for dataset maintenance; those commands are unavailable and do not apply to this documentation-only phase. No organizer-only material was used.

The final user prompt ends at “Any limits on file size, runtime”; this analysis covers both, but additional intended constraints may be missing.

## 2. Documented task and inputs

Audit the person's request first. Access, correction, export, marketing opt-out, and other non-deletion requests authorize neither deletion nor deletion verification. For authorized deletion, reconstruct the subject's identifiers and the state of every relevant record and recreation process at `audit_at`. Apply the supplied policy, not external privacy-law assumptions. Workflow success is not proof. This is an audit and remediation-plan generator, not authorization to modify live services.

Verified inventory:

| Path under dataset/ | Rows | Exact CSV fields |
| --- | ---: | --- |
| deletion_requests.csv | 518 | case_id,email,requested_at,reported_status,reported_at,audit_at,request_text |
| sample_deletion_requests.csv | 32 | same request fields |
| sample_output.csv | 32 | case_id,deletion_status,steps_json |
| user_identities.csv | 850 | user_id,name,email,phone,email_hash,updated_at |
| user_audit_log.csv | 306 | audit_id,user_id,event_time,field_name,old_value,new_value |
| system_activity.csv | 4,011 | activity_id,event_time,event_type,source_system,target_system,resource_id,reported_result,details |
| deletion_rules.csv | 15 | rule_id,data_category,condition,required_action |
| evidence_files.csv | 94 | file_id,file_path,origin,captured_at |
| output.csv | 0 | case_id,deletion_status,steps_json |

All 94 manifest paths exist relative to `dataset/`. Evidence totals 2,934,541 bytes: 24 SQL, 28 JSON, 26 logs, 1 text, 4 PDFs, 11 PNGs. Evaluation audit cutoffs range from 2026-01-29 through 2026-10-01. Evaluation IDs are unique and disjoint from sample IDs. Input request order is not lexicographic.

Relationships:

- Request email -> current email or historical old/new email -> stable user_id -> temporal identity aliases (names, phones, emails, hashes).
- Identifiers -> artifact contents and activity details -> resource/system IDs -> related processes and downstream copies. The manifest itself is not a case-resource map.
- Audit rows join via user_id; activity requires grounded links rather than assuming every global event concerns the subject.
- Policy category and condition -> required treatment; evidence establishes both applicability and actual state.
- Manifest file_id -> relative path, origin, capture time. Preserve evidence provenance through all transformations.
- Samples and evaluation requests share context files. Sample labels belong only to the evaluator, never to predictor inputs, prompts, retrieval indexes, or cached predictions.

Inspected representative JSON snapshot bundles, trace-correlated logs, shift-handover text, primary/replica SQL, a connector screenshot, and both pages of a retention PDF. These contain business facts rather than ready-made verdicts. JSON bundles have both export timestamps and embedded snapshot timestamps. SQL includes heterogeneous schemas and `snapshot_scope`; absence requires a scoped snapshot/query, not a failed text search. Logs can separate an identifier and its query result across lines linked by trace_id. Screenshots can contain relevant rows alongside unrelated connectors. PDF content can span pages.

## 3. Exact output contract

Root `output.csv`: UTF-8 CSV, header `case_id,deletion_status,steps_json`, 518 data rows, exactly one per evaluation case, sorted ascending by case_id. The output schema is not the input reported-status schema.

| Field | Required representation |
| --- | --- |
| case_id | original string identifier |
| deletion_status | COMPLETE, INCOMPLETE, or NOT_APPLICABLE |
| steps_json | CSV-escaped string containing a JSON array |
| step_no | JSON integer, consecutive from 1 |
| phase | FINDING, REMEDIATION, VERIFICATION |
| system_id, resource_id | grounded string identifiers |
| operation, state | strings from the exact pairs below |
| evidence_id | participant-visible file_id, activity_id, audit_id, or required empty string |

Each step has exactly seven fields: step_no, phase, system_id, resource_id, operation, state, evidence_id. JSON key order and whitespace are ignored; array order is significant. String/integer types are explicit in the example and are the proposed strict validator types; no complete official JSON Schema is supplied.

Canonical order from the problem statement and README: phase, then operation in the following table's order within the phase, then system_id ascending, then resource_id ascending. Number steps after sorting.

| Phase | Operation | State |
| --- | --- | --- |
| FINDING | REPORT_REMAINING_RECORD | PRESENT |
| FINDING | REPORT_EXPOSED_PII | PRESENT |
| FINDING | REPORT_ACTIVE_DATA_FLOW | ACTIVE |
| FINDING | REPORT_RESTORE_RISK | ACTIVE |
| REMEDIATION | DISABLE_DATA_FLOW | DISABLED |
| REMEDIATION | BLOCK_RESTORE | BLOCKED |
| REMEDIATION | DELETE_RECORD | ABSENT |
| REMEDIATION | REDACT_RECORD | REDACTED |
| REMEDIATION | ANONYMIZE_RECORD | ANONYMIZED |
| VERIFICATION | VERIFY_RECORD_ABSENT | ABSENT |
| VERIFICATION | VERIFY_RECORD_PRESENT | PRESENT |
| VERIFICATION | VERIFY_RECORD_REDACTED | REDACTED |
| VERIFICATION | VERIFY_RECORD_ANONYMIZED | ANONYMIZED |
| VERIFICATION | VERIFY_DATA_FLOW_DISABLED | DISABLED |
| VERIFICATION | VERIFY_RESTORE_BLOCKED | BLOCKED |

- NOT_APPLICABLE: exactly `[]`.
- COMPLETE: only verification; each check has evidence proving the compliant state by audit_at.
- INCOMPLETE: evidence-backed findings, complete ordered remediation, then future verification. Every remediation and verification evidence_id is empty, including verification of already-compliant resources.
- Verification must cover all relevant final states, not just changes. Public case_06 verifies both its already-absent account and its remaining search entry; case_11 additionally verifies retained security data and already-compliant resources.

## 4. Policy and reasoning requirements

| Categories / condition | Required treatment |
| --- | --- |
| USER_PROFILE, SECONDARY_IDENTIFIER, SEARCH_INDEX_ENTRY, CACHE_ENTRY, USER_EXPORT, MARKETING_PROFILE: Always | DELETE |
| SUPPORT_MESSAGE: shared customer, agent, or order context must remain | REDACT |
| SUPPORT_ATTACHMENT: belongs only to subject | DELETE |
| ANALYTICS_PROFILE, PRODUCT_TELEMETRY: still attributable | ANONYMIZE |
| EMAIL_DELIVERY_LOG: contains user email | REDACT |
| SECURITY_AUDIT_LOG: within supplied retention period | RETAIN |
| LEGAL_HOLD_RECORD: supplied hold active | RETAIN |
| BACKUP_ARCHIVE: restore can be blocked | RETAIN; block unsafe restoration |
| ACCOUNT_TOMBSTONE: deleted account needs internal reference for retained records | REDACT; preserve stable user_id |

A tombstone must lose name, email, phone, email hash and other prohibited direct identifiers; its stable reference alone is allowed. An analytics record linked through a hash or stable user reference is not necessarily anonymous. Retaining a backup does not make an active restoration path safe.

Every relevant copy must comply, required retained records must remain, and no active synchronization/import/restore path may recreate prohibited data. Check replicas independently: a clean primary cannot establish a clean failover replica. Resolve stale identifiers and case differences; do not assume resource numbers encode user IDs or case membership. Recreated data after a successful deletion matters if present by audit_at.

Disable flows and block restores before changing dependent records. AGENTS also requires downstream-before-source remediation when dependencies demand it. Conflicts with canonical output ordering must be exposed, not silently resolved by ignoring one requirement.

Only evidence available by audit_at may affect a decision. Keep event time, embedded observation time, manifest capture time and snapshot update time distinct. Identity updates after the cutoff require temporal reconstruction, not unrestricted use of the latest snapshot. Claims such as SUCCESS, COMPLETE, or a command acknowledgement do not by themselves establish record state.

## 5. Public examples and scoring boundaries

32 labeled samples: 10 COMPLETE, 22 INCOMPLETE, zero NOT_APPLICABLE. They exercise all 15 allowed operations, including flows, restores, retention, and compliant/exposed tombstones. Samples case_31 and case_32 distinguish compliant stable-reference tombstones from exposed identifiers. All sample file citations checked against manifest capture dates are at or before their case audit cutoffs.

Official scoring considers deletion_status, identity resolution, discovered records/risks, cited evidence, policy decisions, step completeness and order against hidden canonical answers. No public scoring weights, partial-credit formula, evidence-equivalence rule, or runnable hidden grader is provided. Report honest sample metrics; do not label unlabeled evaluation-set coverage as accuracy or claim a predicted contest score.

## 6. Proposed smallest complete architecture — approval required

One Python CLI process, standard library dataclasses/enums, CSV/JSON, datetime, pathlib, hashlib and SQLite. No web service, vector database, autonomous tool loop, multi-agent framework, or hosted storage is needed for this corpus. Optional PDF/OCR tooling and one model-provider adapter are the only planned external dependencies. Exact provider/model, versions and budget remain unselected until approved and checked at implementation time.

Proposed boundaries (small modules, not separate services):

1. **Load and extract:** validate paths/headers; parse CSV, JSON, text/logs, and SQL into evidence observations. Load supplied SQL only into an isolated in-memory database with extensions/file attachment disabled. Extract all PDF pages; OCR screenshots, with vision fallback for uncertain interpretation. Cache extraction by file hash, parser/prompt version and model identifier.
2. **Resolve identity and retrieve:** temporal alias index and exact resource/trace joins. Preserve match reasons and ambiguity; do not merge people on a shared name alone. Maintain lineage for resources later stripped of identifiers.
3. **Interpret:** use AI for ambiguous multilingual deletion intent and unstructured evidence where deterministic extraction is insufficient. Return typed facts with source locations, never unconstrained final CSV. Treat artifact text as evidence, not instructions. No labels in model context.
4. **Reconstruct and apply policy:** select admissible observations by cutoff, track copies separately, reconcile contradictions, infer justified state and conditional policy. Preserve uncertainty internally; missing proof is not proof of absence.
5. **Plan and serialize:** build findings/actions/checks from policy and state, validate dependencies and exact canonical order, then emit and validate the CSV. Do not invent a fourth submission status for uncertain cases; unresolved cases are development errors requiring investigation before a full run is accepted.
6. **Evaluate and account:** separate evaluator can read public labels after prediction. Record elapsed time, API usage/cost and cache hits without secrets. Emit Markdown reports from reproducible measured results.

Typed intermediate records: Request; IdentityAlias(value, kind, user_id, temporal validity, provenance); Observation(resource/system, copy/table, identifiers, category, observed time, available time, state facts, source ID/location); PolicyDecision; CaseAssessment(with unresolved issues); Step; ModelUsage. Retain raw facts separately from inferred compliance and final serialization.

Trade-off: this design makes rule decisions and ordering reproducible and limits inference cost, but requires explicit adapters for heterogeneous artifacts. A model-only final-answer pipeline would reduce adapter code while making provenance, repeatability and cutoff enforcement harder. Recommendation: approve the hybrid design; defer actual API spending until provider and budget approval. “AI-powered” is the documented expectation, but no minimum number of calls, mandatory provider, or required percentage of AI decisions is specified. Development assistance alone is not assumed to satisfy the runtime AI expectation.

## 7. First implementation milestone after approval

Use sample case_05 as the minimal representative deletion slice: the failover SQL contains account_005 even though the primary is empty. The public label cites evidence_54 and expects a finding, deletion, and verification. This is a regression oracle only, not a prediction shortcut.

Proposed command: `python3 code/main.py --requests dataset/sample_deletion_requests.csv --case-id case_05 --output <temporary-output.csv>`; default `python3 code/main.py` will ultimately read evaluation requests and write root output.csv. Filters are development conveniences, never the final submission default.

Acceptance: read real request/identity/policy/manifest/activity inputs; resolve the subject without case-number assumptions; inspect scoped primary and failover data before cutoff; produce the correct three-step row with valid provenance, types and ordering; compare externally to the label; run from another working directory using repository-relative paths; repeat identically. No sample label import by the prediction path. The slice may handle clear English intent deterministically; it does not establish full AI or multimodal readiness.

Next increments: generalized SQL and complete/non-deletion paths; full evidence adapters and model interpretation; all 32 sample comparisons plus custom regressions; complete 518-case run and usage accounting; clean-install and packaging rehearsal. Validate and commit meaningful milestones locally, never push or submit.

## 8. Evaluation-first plan (local diagnostic definitions, not official formula)

Freeze public inputs/labels by hashes and record commit, parser/prompt/model versions, configuration, cache state and commands. Predict all 32 sample cases independently, then let the evaluator load labels. Label-informed engineering is a development benchmark, not an independent generalization estimate. Preserve a fixed baseline and add generalized regressions rather than per-case patches.

| Measure | Proposed reproducible definition |
| --- | --- |
| Coverage | unique required IDs with rows / required IDs; separately count missing, duplicate and extra IDs |
| Validity | count/rate passing exact schema, enums, order, citation existence/time and status-specific rules |
| Status accuracy | exact deletion_status matches / 32; confusion matrix and class counts |
| Exact case accuracy | status and complete parsed ordered step array both match / 32 |
| Step accuracy | multiset exact-step precision/recall/F1 excluding step_no to diagnose content independently of sequence; include evidence_id; duplicates remain significant |
| Field accuracy | positional per-field agreement across max(predicted, expected) array length; missing/extra steps count as mismatches for all seven fields; aggregate and per-field denominators shown |
| Sequence accuracy | exact ordered step-array matches / 32, independent of status; also diagnose canonical-sort and dependency violations |
| Unsupported/invalid | explicit counts and reasons; do not silently skip or remove from denominators |
| Regression count | previously exact-correct sample/custom cases now incorrect; maintain per-category deltas |
| Runtime | wall time for extraction, prediction, validation and total; distinguish cold and cached runs |
| Inference usage/cost | actual calls, provider/model, input/output tokens, total and mean per request; per-model and overall totals; documented rates, currency/date and estimate method |

For step precision/recall, define an all-empty matched benchmark as 1; zero predictions with nonempty expected steps has recall/F1 0. Report counts alongside ratios. Semantic citation-equivalence diagnostics may supplement exact comparisons, never replace them silently. Hidden identity-resolution accuracy is unavailable: use synthetic known identities and downstream public-label errors as diagnostics, not an invented official metric.

Custom evaluation cases to author with full fictional fixtures and explicit expected output:

1. Multilingual export/access or marketing-opt-out request with workflow COMPLETE and residual PII: NOT_APPLICABLE with []; unauthorized deletion is a failure.
2. Historical email points to subject, primary absent, failover contains old identifier before cutoff; remediation evidence after cutoff must not affect state: INCOMPLETE and delete residual copy.
3. Tombstone with stable user_id only plus retained security record: COMPLETE; paired mutation adding email/hash must yield REDACT, never DELETE of tombstone or security record.
4. Active connector plus restorable retained backup and downstream record: stop flow, block restoration, then delete dependent data, with full verification.
5. Identical identifiers/resource observed compliant and noncompliant on opposite sides of audit_at; later export bundle tests admissibility boundaries without changing past state.

Error taxonomy: intent; identity false merge/missed alias; retrieval omission/decoy; extraction/OCR; temporal leakage; claim mistaken for proof; replica aggregation; policy/retention/tombstone; flow/restore dependency; evidence selection; missing verification; serialization/order. No measured solution accuracy or runtime exists yet.

## 9. Submission and operational requirements

| Deliverable | Required location/content |
| --- | --- |
| output.csv | repository root, generated from final 518-case run |
| code.zip | runnable source, prompts, non-secret configuration, README, evaluation reports |
| README.md | setup, dependencies, exact terminal command, paths, model configuration and reproducibility instructions |
| evaluation_report.md | status, step, field and sequence metrics; at least 3 authored cases; failures and improvements directly in Markdown |
| usage_report.md | final full-run providers/models, call counts, tokens, per-request/total costs and per-model totals directly in Markdown |
| chat_transcript | root log.txt, uploaded directly per AGENTS/README |
| agent-trace.zip | separate original structured traces per agent_trace_instructions.md; do not nest in code.zip |
| AI interview | architecture, investigation, remediation, evaluation explanation |

Report-path conflict: AGENTS §6.8 and problem statement specify `evaluation/...`; README strongly requests `code/evaluation/...`, while its packaging section also permits top-level evaluation. Proposed conservative packaging: canonical top-level evaluation reports plus byte-identical copies under code/evaluation, validated for consistency. This avoids silently choosing one contradictory instruction; confirm organizer expectations if possible.

Trace conflict/addition: AGENTS requires log.txt while agent_trace_instructions requests original traces as a ZIP. Preserve both separately; final upload slot for the extra ZIP is not documented. Raw traces should be staged only after relevant sessions finish, reviewed/redacted, and must exclude auth/config/credentials and unrelated sessions. Do not quit the active session or package traces now.

Automated code evaluation ignores raw `.csv`, `.tsv`, `.json`, `.jsonl`, `.sql`, `.log` content according to README. Keep metrics, authored fixture descriptions/expected results and usage details directly in Markdown; executable custom fixtures can live in Python. Prompts must be source or Markdown. Runtime caches are not substitutes for readable reports or source.

Exclude dataset, virtual environments, dependency/build caches, nested archives, secrets, real personal data and sensitive configuration from code.zip. Final packaging should use an explicit allowlist and inspect archive members; do not blindly rely on starter zip commands to exclude everything. Secrets come from environment variables; any local .env stays uncommitted. Add appropriate ignore rules with implementation, before generating caches or credentials.

Logging: append-only root log.txt; session start and every user turn with verbatim prompt (secret-redacted), summary, actions and context; exact harness and model verified from runtime metadata. This session uses Codex / gpt-6-astra. No configured deadline. No documented maximum upload size, runtime, token budget, internet permission during judging, dependency allowlist, required model/provider, or minimum inference-call count was found in the local documents. Any language/model/framework is permitted subject to official event rules; no specific pre-existing-code restriction or external-API prohibition is stated here. This is absence of documentation, not an exemption from broader event rules. Significant API spending requires project-manager approval.

Challenge/submission URL, preserved exactly as mandated:
https://wwww.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists

## 10. Assumptions and unresolved questions

Reasonable proposals, not documented requirements:

- Lexicographic string sorting for case_id/system_id/resource_id; identifiers are strings and evaluation IDs have variable numeric widths. Do not assume numeric “natural” sorting without confirmation.
- Use a conservative evidence-availability gate requiring manifest capture and relevant observation times at/before audit_at. Embedded earlier observations in a later bundle are not automatically admissible. No late file citations were found in public labels.
- Cache immutable extraction independently of case reasoning and apply cutoff at selection time. Cache reuse must retain provenance and usage attribution; report warm/cold behavior separately.
- Strict validation stops a full run when evidence cannot support a legal answer; there is no official UNKNOWN status. Investigate unresolved cases rather than emit fabricated findings.

Questions requiring clarification before affected implementation/final packaging:

1. Which report paths and transcript upload slots does the judge actually require? Proposed dual report locations and separate trace artifacts above.
2. If dependency-safe remediation contradicts operation/system/resource ordering, which takes priority? Do not silently weaken either rule.
3. Are alternative equally valid evidence IDs accepted, and how are ties chosen? Hidden canonical scoring may require a particular citation; no selection rule is supplied.
4. Does a later-exported bundle containing an earlier observation count as information available by audit_at? Literal AGENTS language excludes later capture; preserve that default unless clarified.
5. What happens when a conditional retention rule is not satisfied, a required retained record is missing, or evidence is insufficient/conflicting? Allowed operations contain no restoration action and status enum contains no uncertainty state. Do not invent either.
6. Are runtime, archive size, network/model-access, pre-existing-code licensing, or deadline limits specified only on the live event page? Local checkout does not answer these. No live event verification was performed in this phase.
7. Which inference provider/model and maximum budget should be approved? This does not block the no-cost vertical slice but is required before substantial inference runs.

Approve the proposed Python hybrid architecture and the case_05 vertical slice before implementation. Requirements documentation and its local commit do not imply architectural approval.

## 11. Discovery validation

All 32 public label rows passed independent read-only checks of exact step fields/types, consecutive numbering, operation/state compatibility, phase/operation/system/resource ordering, citation existence and cutoff, and status-specific citation requirements. Inventory checks confirmed all 94 evidence paths, 518 unique evaluation IDs and disjoint sample IDs. `git diff --check` passed. These are contract/inventory checks, not solution accuracy measurements. Source entrypoints remain empty and participant data unchanged.
