# Five-minute interview briefing

## Architecture

The agent audits deletion intent first, resolves current/historical identifiers,
and reads only participant-facing evidence available by each audit_at cutoff.
Python adapters extract SQL primary/replica snapshots, nested JSON, service logs,
text handovers, selectable-text PDFs and reviewed screenshots. Observations retain
identity/resource lineage, availability/observation time, physical copy and citation.
Policy maps facts to deletion, redaction, anonymization, retention or tombstones.
The planner stops active flows/restores before record changes, sorts canonical
operations and produces verification for supported final states.

Reported workflow success is a claim, not state. Missing identities cannot be
joined by numbered-ID patterns. Unknown retention dates cannot be inferred from
integrity seals. New screenshots cannot reuse another image's reviewed facts.

## What changed after the runtime experiment

The completed experiment did not improve accepted accuracy, so deterministic
operation was retained. No additional paid calls were made. Pipe-delimited log
headers were missing in extraction; recovering service/trace/event fields adds
six full-dataset decisions. A screenshot/catalog join adds one more: the screenshot
proves an attachment filename is present; a pre-cutoff catalog event supplies the
stable object ID, subject and sole ownership. Both witnesses remain in provenance.

All original 151 blockers now have explicit dispositions. Seven decisions were
recovered and four other formerly unlinked cases now have readbacks but unresolved
policy facts. Diagnostics preserve every independent omission instead of only the
first proof gate. Full evidence sufficiency and organizer questions are documented
in docs/evidence_sufficiency.md.

## Measurements

119 solution tests pass. The public benchmark produces 22/32 correct statuses,
2/32 exact cases/sequences, 118/121 matching emitted steps (97.52% precision),
118/193 recall (61.14%), and 38/39 correct emitted citations. The attachment triple
is supported by evidence but absent from the public canonical answer. Its inclusion
slightly reduces precision; no previous matching step or exact case is lost.

Full coverage improves from 367 to 374/518: 339 INCOMPLETE, 25 COMPLETE and 10
NOT_APPLICABLE. There are still 144 unsupported cases. The required valid output.csv
does not exist. A clean package reproduces the same partial output and exit 2.
Runtime calls, input/output tokens and cost are zero. Hidden accuracy is unmeasured.

## Questions to be ready for

**Why not fill the remaining rows with INCOMPLETE?**
That asserts a violation. Missing completion proof alone does not establish one.
The contract also requires a complete remediation plan, but defines no uncertainty
status. For an undated security record, neither applicable retention nor unlawful
persistence is established. We need missing facts or an organizer-defined fallback.

**Why are exact cases still low?**
Many expected verifications need lineage for already-absent accounts or anonymous
resources; supplied exports can omit those identifiers. Security retention and
support context can also be absent. A grounded violation supports the status while
missing verification resources prevent an exact plan. We report both measures.

**Is the package submission-ready?**
The source is runnable and clean-tested; the predictions are incomplete. No valid
518-row submission is claimed. The 374-row supported artifact is explicitly partial.
Nothing is pushed or submitted. The official deadline is not configured.

**Are the screenshot facts hardcoded answers?**
They are reviewed visible fields keyed to image SHA-256, with no case IDs, verdicts
or expected steps. Policy, identity and cutoff logic still run. Unknown or changed
images remain unresolved. This trades general OCR capability for deterministic,
reviewable evidence extraction on the supplied corpus.

## Artifacts and handoff

code.zip: source/tests/reports, excluding dataset, caches, credentials and experiments.
artifacts/supported.csv: partial predictions. artifacts/submission-run.json: full
per-case diagnostics, including unsupported-case omissions. log.txt: conversation
transcript. agent-trace.zip: redacted snapshot, to refresh after closing Codex for
complete active-session logs. No push/submission or organizer messaging occurred.
