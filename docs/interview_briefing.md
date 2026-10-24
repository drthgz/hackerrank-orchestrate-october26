# Five-minute interview briefing

## Approach and architecture (one minute)

We reconstruct deletion state from participant evidence available at audit time.
The Python pipeline separates intent, historical identity resolution, typed
observations, policy, planning and output validation. SQL copies remain separate;
JSON, text handovers, application logs and now selectable-text PDFs feed the same
Observation objects. Workflow success remains a claim, not evidence of absence.

Each observation preserves manifest evidence ID, source origin/path, page or
line/collection provenance, observation time and availability time. Current and
historical identifiers establish subject lineage; resource similarity and numbered
IDs do not. Predictors never load public labels. Evaluation opens them afterward.

## PDF capability and retention (one minute)

We inspected all four manifest PDFs before designing the adapter: every page has
selectable text, with no embedded images. Poppler extraction is sufficient; there
is no OCR or model call. Explicit journal references produce retained security
observations. The customer-uploaded address-correction document produces a linked
attachment with grounded ownership. A monthly register supplies subject/order
retention metadata, without inventing legal resource IDs. A customer statement
alone establishes no retention rule.

Retention requires both the supplied policy and facts proving its condition.
Security records need an applicable deadline. Legal retention needs a separately
linked resource and supported active hold/dispute/tax condition. Register metadata
joins only on exact subject and order, preserving its source and page references.
Explicit inactive holds are preserved. Account tombstones keep permitted stable
references while removing prohibited identifiers. Disable flows and block unsafe
restores before record changes; verify retained and already-compliant resources
as well as remediated ones.

## Time and verification (45 seconds)

Capture time controls admissibility: an old event exported after audit cannot be
used. Observation time controls state selection. For the journal, issue time
proves the extracted record exists; its older recorded event stays separate.
For an attachment, capture and submission times remain distinct. Post-capture
observations fail validation. Complete decisions require positive profile absence,
closed evidence scope and evidence-backed verification; missing resources are
never supplied from numbered case patterns or expected labels.

## Measured result (45 seconds)

108 tests pass, including twelve new PDF/provenance/correlation tests. Public
metrics remain at the baseline: 10/32 valid outputs and correct statuses, 2/32
exact cases/sequences, 58/58 emitted steps correct, 19/19 cited steps correct.
Step recall is 81.69% over processed cases and 30.05% across all public steps.
There is no measured public scoring improvement, and no regression. PDF resource
discovery improved but did not fully unblock a public case. Zero runtime model
calls, tokens or inference cost.

For case_07 the PDF identifies the attachment, but a separate subject-linked
catalog object still lacks parsed state; account-absence verification also lacks
a grounded readback. We keep that limitation visible instead of conflating IDs.

## Limitations and next work (45 seconds)

There are 22 unsupported public cases. Missing retention conditions, support
context/full-text, absence lineage and image/correlated state remain blockers.
The label-free 518-request dry run supports 86 cases and leaves 432 unsupported;
240 first failures concern intent grammar. A valid 518-row output cannot yet be
produced. Full-run evaluation and packaging still need that final prediction run.

Prioritize deterministic parsing and image inspection, then a bounded text-model
experiment for unresolved intent. OCR is unnecessary for these PDFs; screenshots
may justify OCR, with vision only if layout semantics defeat text extraction.
Neither a parser nor a model can create genuinely missing dates or resource links.

## Three likely questions (remaining minute)

**Why did PDF support fail to improve the public score?**
The security extract concerns a different subject from the blocked public security
cases. The legal register lacks matching resource/order links in parsed evidence.
The attachment improves case_07 discovery but leaves independent state and account
verification gaps. We measured the result rather than assuming extraction meant
complete plans.

**How do you avoid retaining a record just because a PDF exists?**
Match explicit resource identity, subject and policy conditions, including dates.
Order-level metadata can only supplement a separately observed matching resource.
A statement or unmatched register row supplies no record-state or retention verdict.

**Where would AI help most, and how would you control it?**
The full-run intent grammar has 240 first failures, giving text interpretation a
measurable target. Inspect screenshot/OCR failures before buying vision inference.
Any extracted facts still need provenance, subject/resource correlation and audit
cutoff checks. No paid calls were made in this milestone.

Details: [evaluation report](../evaluation/evaluation_report.md) and
[usage report](../evaluation/usage_report.md).
