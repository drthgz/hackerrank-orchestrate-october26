# Interview briefing: first SQL vertical slice

## What works now

The Python CLI produces the correct public `case_05` row without reading its label. It uses actual request, identity/history, policy, activity and evidence-manifest inputs. Identity resolution supports current and historical emails, normalizes email case and phone formatting, and refuses ambiguous people or aliases only established after the audit cutoff.

It executes admissible SQL dumps in isolated in-memory SQLite, independently inspects account primary and failover tables, and retains the system/resource, physical copy, table, snapshot time, row update time, and source file ID. A surviving profile governed by unconditional DELETE produces a finding, remediation, and future verification. Serialization follows the exact official operation order and validates output coverage for the selected request.

This milestone uses deterministic rules and no runtime AI calls. It establishes the reliable foundation for the approved hybrid architecture, not the complete competition submission.

## Pipeline in one minute

1. Validate CSV headers, IDs, timestamps, manifest paths and basic policy/input enums.
2. Recognize a narrow explicit English deletion instruction; reject unsupported or restricted intent.
3. Resolve the subject through temporally available identifiers and history.
4. Read pre-cutoff SQL evidence, discover resources through identifiers, and observe each copy separately.
5. Select the latest observation within each copy lineage. Keep operational claims separate from state evidence.
6. Apply the supplied USER_PROFILE / Always / DELETE policy. Missing, conflicting or unsupported policy is an error.
7. Produce deduplicated logical resource steps while retaining copy-level diagnostics. Order and number steps, validate citations and future-work evidence rules, then write CSV.
8. A separate evaluator opens the label and compares status, steps, citations, fields, sequence and repeated-run bytes.

## Why replica independence matters

In the sample, the primary snapshot has no subject row while the failover snapshot still contains it. Combining copies too early could let a clean primary erase the evidence of surviving personal data. The intermediate model therefore keeps `(system, resource, copy)` states separate. Only after assessment are multiple violating copies consolidated into the required logical resource step. A future executor would need the diagnostics to treat all physical copies.

A successful deletion workflow says an operation ran; it does not establish that every copy is absent. Replication may fail, lag, or recreate a row. We therefore treat the sample's deletion and synchronization SUCCESS results as claims and cite the surviving row itself.

## What remains unsupported

No PDFs, screenshots, OCR, standalone JSON/log/text evidence interpretation, broad multilingual intent, runtime model adapter, full retention/redaction/anonymization, active-flow/restore planning, or full-dataset execution yet. Only recognized account primary/failover schemas receive semantic state interpretation. Subject-linked SQL outside those schemas fails explicitly. Non-SQL sources are listed as unprocessed, so this is a scoped audit rather than a guarantee that other systems are clean.

No COMPLETE or NOT_APPLICABLE prediction path is enabled yet. A clean supported snapshot cannot prove the global deletion is complete. Unresolved identity, conflicting evidence, unsupported policy or later operational activity aborts rather than fabricating an answer. The final root output.csv is protected against accidental replacement with a one-row result.

## Three likely questions

**How do you prevent sample-answer leakage?**
The predictor never imports the evaluator or opens labels. Resource discovery uses identifiers in actual SQL, not numbers in case IDs. A regression test runs the predictor with an audit hook that raises on any attempt to open sample_output. The independent evaluator reads the label only after prediction.

**How do you enforce the audit time?**
Manifest captures and observation timestamps must be at or before audit_at. Row updates cannot be later than their snapshot. Identity snapshots and history are filtered separately. A post-cutoff dump is skipped before parsing; newer primary evidence cannot overwrite a different replica's earlier state.

**What does a perfect result on this sample prove?**
It proves this narrow end-to-end path matches its public label and is reproducible. It does not establish performance on the other 31 samples or 518 evaluation cases. Synthetic regressions exercise identity ambiguity, temporal boundaries, replica drift, policy refusal, SQL isolation, and ordering; broad accuracy requires subsequent milestones.
