# Interview briefing: deterministic evidence coverage

## Supported features

The existing Python pipeline now consumes relational/embedded-JSON SQL, standalone
JSON snapshots and nested service responses, application/readback logs in five
encodings, and structured text handovers. Intent recognizes direct deletion,
residual copies, earlier-deletion audits and bounded multilingual forms.
NOT_APPLICABLE requires explicit recognized non-deletion and returns no steps.

Identity resolution uses current and historical identifiers available by audit_at.
Nested identifiers, isolated trace contexts and explicit source-resource references
establish lineage. Names are used for PII scans, never identity merges. Independent
replicas retain separate state and provenance. Readback state differs from a
workflow claiming success.

Policy supports deletion, redaction, anonymization, connectors, restore controls,
retention and tombstones. Every assessed compliant resource receives verification,
including retained records that need no remediation. Disable/block actions precede
record changes; official canonical ordering and validation remain enforced.

## Architectural decisions

Adapters produce the existing Observation objects; policy, planning and output
validation remain separate. Observations keep file/line/collection provenance,
observation time and availability time. A later export cannot introduce facts into
an earlier audit, even when its embedded event timestamp is earlier.

Anonymity or absence without resource lineage is insufficient. A partial support
excerpt can expose PII, but cannot prove full redaction. Policy dates/ownership
must be supplied; metadata joined across sources retains its supporting citation.
COMPLETE also requires closed evidence scope and sufficient cited witnesses.
Unparsed PDFs/images continue to prevent scope closure. No contract validator was
relaxed, and no resource IDs or public steps were inserted into prediction logic.

## Actual benchmark

96 tests pass, up from 61. All 32 public cases pass intent. Valid output coverage
rose from 3/32 to 10/32; status matches from 3/32 to 10/32; exact case/sequence
matches from 1/32 to 2/32. Both exact cases are preserved across repeated runs.
All 58 emitted step contents and all 19 non-empty citations match public labels.
Recall is 81.7% among emitted cases, 30.1% across all public steps. Eight emitted
plans still omit required verification resources. Structural validity is not a
claim that these plans are complete.

The benchmark repeats successful predictions, validates outputs, and opens labels
only after prediction. There are zero runtime model calls, tokens or inference
cost. This is not the full 518-case submission run. Details and checkpoint results:
[Evidence evaluation](evidence_evaluation.md).

## Remaining limitations and next priority

Of 22 unsupported cases, first failures are retention facts (10), support
context/full text (4), missing subject-linked evidence (4), profile-absence lineage
(2), unparsed-media scope (1) and unresolved activity resources (1). Binary scope
and missing lineage can remain after an earlier failure is fixed.

Next: deterministic PDF text extraction for the delivery attachment and retention
extract, followed by targeted image inspection. Only case_07 is directly known
from its evaluated finding to require a PDF; the ten retention blockers are a
potential opportunity, not a promised gain. No PDF/OCR/vision or paid inference
was used in this milestone. Never invent a retention period or identifier to
satisfy a public label.

## Three likely interview questions

**How do you correlate an anonymous or deleted resource to a person?**
Through an admissible earlier record with current/historical identifiers, an
explicit source reference, or an isolated lookup trace. That grounded resource
lineage survives later removal of identifiers. A null payload or similarly named
resource alone is not enough.

**Why did coverage increase much more than exact accuracy?**
The new adapters find real surviving records and recreation paths, yielding ten
valid partial outputs with correct statuses. Exact answers also require every
retained/absent resource and its ordered verification. Missing retention dates,
full text and subject-resource links still prevent many complete plans. The
search-to-profile edge fixed one such verification gap without hardcoding IDs.

**When would you use AI, and how would you avoid overfitting?**
First measure deterministic PDF extraction and inspect relevant images. Use AI
only for demonstrated interpretation gaps, preserving timestamp/provenance checks.
The predictor never reads public labels; independent fixtures vary identities,
trace boundaries, replicas and timelines. The evaluator reports exact accuracy,
recall and unsupported cases separately rather than treating emitted rows as wins.
