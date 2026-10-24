# Deterministic evidence coverage milestone

Base: dd8f6a6. Only participant-facing evidence was used. Labels are opened by
`code/evaluation/main.py` after prediction attempts; a subprocess audit-hook test
checks label isolation across every public prediction and every new adapter.
No PDF, OCR, vision or inference was used. No validators were weakened;
`audit/contract.py` is unchanged.

## Implemented capabilities

- Standalone collection snapshots, nested profile/search records, snapshot bundles,
  operational record history, and nested service-response exports.
- Timestamped key-value, JSON, application-bracket, syslog and escaped cloud logs.
  Trace contexts are isolated by file, logical source, trace and instance; starts
  reset reused traces. Actual readbacks establish state; mutation success, retries
  and cache misses do not.
- Pipe-delimited handover text, resource references and historical identity aliases.
  Explicit search-to-profile references supply account verification lineage.
  Resource IDs alone do not identify a subject.
- Independent SQL and explicitly named JSON/log copies. A clean primary cannot
  overwrite a surviving replica. Subject reassignment and simultaneous conflicting
  states remain errors.
- Retention/ownership metadata correlation with source tracking; bounded support
  context/PII interpretation, including names and formatted phones. Names are
  scanned for residual PII but never used as identity join keys.
- Verification of compliant retained/absent resources alongside remediated copies.
  Already-deleted subject-only attachments get absence verification, without
  deleting shared support context. Canonical step ordering is unchanged.

Availability uses the manifest capture time as well as the record observation
time. A later export containing an earlier event is still inadmissible before the
export's capture time. Future-dated rows inside an earlier export are excluded.
Collection absence requires scoped lineage; a different bundle's missing row is
not treated as proof that a retained record disappeared.

## Checkpoints: all 32 cases attempted at every stage

| Checkpoint | Valid rows | Exact cases | Correct statuses | Step precision | Step recall, emitted cases | Positional citation accuracy | Exact sequence /32 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Base intent milestone | 3 | 1 | 3 | 100% | 75.0% | 75.0% | 1 |
| Initial JSON adapter | 5 | 1 | 5 | 100% | 73.1% | 69.2% | 1 |
| Initial log/text adapters | 7 | 1 | 7 | 100% | 76.9% | 76.9% | 1 |
| Initial lineage integration | 8 | 2 | 8 | 91.2% | 72.1% | 79.1% | 2 |
| Final policy/provenance integration | 10 | 2 | 10 | 100% | 81.7% | 81.7% | 2 |

Checkpoints describe the measured implementations at those stages, not feature
ablations of the final version. During review, assuming an excerpt was full text
was rejected, and support-replica observations were mapped to their logical
support system while retaining their physical copy identity. These changes
improved correctness rather than filling fields from labels.

## Final metrics and reproducibility

```sh
python3 -m unittest discover -s tests -v
python3 code/evaluation/main.py --all-samples --output-dir artifacts/evidence-final
```

96/96 tests pass (61 existing plus 35 new tests). New independent fixtures cover
nested ownership, anonymous-record lineage, complete retained-state checks,
primary/failover divergence, late files, trace reuse/interleaving, all log encodings,
workflow-success rejection, support PII and excerpt limits, explicit source edges,
attachment ownership, legal retention and full-corpus label isolation.

| Final metric | Result |
| --- | ---: |
| Intent recognized | 32/32 |
| Valid output coverage | 10/32 = 31.25% |
| Correct status / all requests | 10/32 = 31.25% |
| Correct status / emitted requests | 10/10 = 100% |
| Full exact case / exact sequence accuracy | 2/32 = 6.25% |
| Step precision | 58/58 = 100% |
| Step recall, emitted cases | 58/71 = 81.69% |
| Step recall, all cases | 58/193 = 30.05% |
| Non-empty citation matches, emitted cases | 19/19 = 100% |
| Non-empty citation matches, all cases | 19/75 = 25.33% |
| Positional citation-field accuracy | 58/71 = 81.69% |
| Positional field accuracy | 360/497 = 72.43% |
| Baseline regressions | 0 |

Each successful prediction is independently repeated and contract-validated.
Final prediction SHA-256:
`441f1fe01c4d0e338eb46dfaa98285312b6510a7cdc141086cebcbbd0f4030d0`.
Runtime is approximately three seconds including repeats. Inference usage is zero
calls, zero tokens and zero cost. This is a 32-case benchmark, not the final
518-case usage report or a completed submission.

## Missing verification investigation

case_06 now exactly matches: the search document explicitly names its source
profile, allowing the scoped account inventory to supply its absence verification.
case_05 remains exact. The other eight emitted cases are partial plans:
case_08, case_09, case_10, case_20, case_23, case_24, case_29 and case_30.
All emitted step contents match; missing resources/verification shift subsequent
step numbers and prevent exact whole-case/sequence matches.

The missing account and security verifications in case_09 cannot be filled from
the read inventory alone: it does not contain the expected security resource, and
the trace linking that security resource is in a file captured after audit_at.
The same principle applies to anonymous analytics/profile responses lacking an
admissible subject-to-resource link. A public label's resource ID is evaluation
information, not an identity source. Nothing infers resource IDs from user/case
numbers or groups unrelated activity by nearby timestamps.

## Remaining blockers, ranked by first failure

| Blocker | Cases | Public requests |
| --- | ---: | --- |
| Supplied retention applicability/date missing | 10 | 11, 12, 13, 14, 15, 16, 19, 22, 31, 32 |
| Full support text/context missing | 4 | 18, 26, 27, 28 |
| No supported subject-linked evidence | 4 | 01, 02, 04, 07 |
| Positive profile-absence lineage missing | 2 | 21, 25 |
| Unparsed-media scope prevents COMPLETE | 1 | 03 |
| Subject-linked activity has an unobserved resource | 1 | 17 |

These are first-failure categories, not mutually exclusive root causes. Unparsed
PDF/images still globally prevent COMPLETE even if another earlier blocker is
resolved. Missing verification resources also limit the eight partial emitted
plans; they are not included among the 22 unsupported cases.

## Next modality and expected benefit

There are four PDFs and eleven images in the participant manifest. They were not
opened, rendered, OCRed or interpreted in this milestone.

A targeted PDF pass is justified first: case_07's public finding directly cites
the delivery attachment PDF. Interpreting it can unblock its ownership/content
finding, although exact completion also needs the missing profile verification.
The security-retention PDF is a plausible source for the ten retention blockers;
its actual coverage and cutoff eligibility must be measured before claiming gains.
Those ten cases are an opportunity ceiling, not a predicted PDF improvement.

Vision may help case_17's unresolved catalog-linked tombstone and the remaining
media scope barrier (including case_03), but specific screenshot membership and
exact-match benefit cannot be established without examining the images. The
anonymous-resource linkage gaps may still remain after media extraction.
Start with deterministic PDF text extraction, then inspect the relevant images.
Paid AI is not justified yet; first measure what admissible text and pixels
actually add. No promised conversion of these blockers into exact answers.
