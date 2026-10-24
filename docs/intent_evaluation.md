# Intent milestone

Continues e136500. Scope is deterministic request-text interpretation only;
no evidence adapters, policy decisions, remediation planning or paid inference changed.
Rules reviewed: AGENTS.md §6.2, §6.3, §6.5 and the participant problem statement.
Only participant request text informed grammar; public outputs are read by the
evaluator after predictions, never by the classifier.

## Capabilities and safety

The independent `audit.intent` module recognizes explicit deletion commands,
residual-copy cleanup and verification of earlier deletion. It supports retention
qualifications without treating them as conditional deletion authorization, and
explicit Spanish, French and Japanese authorization patterns. Unicode and curly
apostrophes are normalized. It uses no case IDs, identity values or workflow status.

Explicit access/export, correction, opt-out and no-deletion forms return
NON_DELETION. Existing pipeline tests prove they need no identity or evidence and
produce NOT_APPLICABLE with an empty step array. Unknown, hypothetical, revoked,
conflicting, mixed-action and unsupported restricted requests raise AuditError.
Language coverage is a bounded grammar, not general multilingual understanding.

Independent examples cover an account erasure command, verification of a prior
deletion, retention with backups, conditional deletion, an export request and
conflicting preservation. New parameterized tests exercise 43 synthetic wordings;
no public answers are embedded in these tests.

## Validation

Commands:

```sh
python3 -m unittest discover -s tests -v
python3 code/evaluation/main.py --all-samples --output-dir artifacts/intent-benchmark
```

61 tests pass, including all 58 existing tests. All 32 public samples were
attempted, and successful outputs were repeated and contract-validated. Evaluator
now reports intent classification separately from downstream processing.

| Metric | Before | After |
| --- | ---: | ---: |
| Intent classified | 5/32 | 32/32 |
| Intent blocked | 27/32 | 0/32 |
| Valid output rows | 2/32 | 3/32 |
| Public status matches | 2/32 | 3/32 |
| Full exact matches | 1/32 | 1/32 |

All classified public requests are deletion/audit requests. This corpus therefore
does not measure real-world non-deletion precision; synthetic safety tests cover
that boundary. Passing intent classification means recognition, not an independent
labeled intent score. Structural validity does not mean a complete evidence plan.
The three valid rows are case_05, case_06 and case_09. Only case_05 matches all
public fields and step sequence; case_06 lacks one verification and case_09 lacks
two. No baseline regressions; repeated predictions agree.

## Next priority

Of 29 downstream failures, 27 report no supported SQL resource lineage and 2 lack
security-retention applicability facts. Broader participant evidence interpretation
is the largest next scoring opportunity, followed by policy facts and whole-case
verification coverage. This milestone deliberately adds no JSON/log extraction,
OCR, PDF, vision or inference. There were zero model calls, tokens and inference
cost in the benchmark. This is a public 32-case run, not a final 518-case usage report.
