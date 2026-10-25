# Evidence-backed accuracy improvements

Baseline source: `d79eb59`, with `docs/accuracy_gap_analysis.md` as the defect baseline. The preserved a4a358b root candidate is byte-identical to the documented hash. Public labels were opened only by evaluation, after predictions. No private truth, paid API calls, push, packaging, or submission was used.

## Accepted implementation

Best-effort policy keeps noncompliant ACCOUNT_TOMBSTONE decisions after the deleted state, stable subject reference, required identifier fields, and REDACT policy have been established. Missing retention applicability/relationships remain explicit omissions and prevent exhaustive or compliant certification. Clean tombstones remain unresolved without retention support. The plan redacts direct identifiers and preserves subject_reference; it never deletes the tombstone or invents a retained resource. Strict-mode relationship gates are unchanged.

Support predicates now carry typed booleans and witness metadata (evidence ID, adapter source/line/table, observation/availability times, and extraction basis). SQL uses the same extraction helper as JSON/log/PDF/reviewed screenshots. Actual order/delivery content or an explicit customer/agent exchange can prove shared context; a category, identifier, or bare keyword cannot. Exclusive attachment ownership is never added from subject matching alone. Positive exposure no longer marks an excerpt as a complete scan. Full message_text scans and explicit scan predicates preserve their distinct provenance. An explicit incomplete scope is not overwritten. Missing facts remain unresolved. Support metadata supplementation cannot cross physical copies or backfill a later observation into an earlier one; scan completeness is not propagated between observations.

Existing PDF personal-form and hash-bound screenshot interpretations were inspected, retained, and routed through provenance capture. No newly inspected PDF/screenshot established the missing support predicates in the public gap cases. Structured/log artifacts likewise provided no new explicit booleans for those omitted resources. Parser changes alone therefore did not recover additional support steps.

## Public evaluation (32 requests)

| Metric | Before | After |
| --- | ---: | ---: |
| Correct statuses | 32/32 (100%) | 32/32 (100%) |
| Exact cases / sequence matches | 2/32 (6.25%) | 2/32 (6.25%) |
| Matched steps | 129/193 | 132/193 |
| Emitted steps | 132 | 135 |
| Step precision | 129/132 (97.727273%) | 132/135 (97.777778%) |
| Step recall | 129/193 (66.839378%) | 132/193 (68.393782%) |
| Step F1 | 79.384615% | 80.487805% |
| Positional field matches | 699/1365 (51.208791%) | 716/1365 (52.454212%) |
| Aligned cited checks/findings with correct citation | 49/49 (100%) | 50/50 (100%) |
| Incorrect aligned citations | 0 | 0 |
| Emitted citations | 50 | 51 |
| Missing FINDING | 5 | 4 |
| Missing REMEDIATION | 5 | 4 |
| Missing VERIFICATION | 54 | 53 |
| Reference-extra steps | 3 | 3 |
| Unsupported findings established by integrity checks | 0 | 0 |

Only case_32 changes: evidence_51 directly establishes exposed fields on tombstone_9178. Recovered operations are REPORT_EXPOSED_PII, REDACT_RECORD, and VERIFY_RECORD_REDACTED. There are no newly exact cases: case_05 and case_06 remain exact. Account lineage and security retention gaps still prevent case_32 exactness. The supported object-storage extra in case_07 remains; removing it to match labels would sacrifice evidence completeness. Citation correctness is measured on semantically aligned cited steps, separately from omitted citations. Positional field accuracy includes numbering shifts and is not an independent defect count.

## Full candidate comparison

518/518 unique sorted request IDs; zero status changes. Four rows change, with 12 added steps and zero removed steps. Every changed case is listed below. Full-dataset accuracy cannot be measured without private labels, which were not accessed.

| Case | Resource | Witness | Added operations |
| --- | --- | --- | --- |
| case_544 | tombstone_8648 | evidence_52 | REPORT_EXPOSED_PII; REDACT_RECORD; VERIFY_RECORD_REDACTED |
| case_546 | tombstone_8095 | evidence_52 | REPORT_EXPOSED_PII; REDACT_RECORD; VERIFY_RECORD_REDACTED |
| case_548 | tombstone_3745 | evidence_52 | REPORT_EXPOSED_PII; REDACT_RECORD; VERIFY_RECORD_REDACTED |
| case_550 | tombstone_7389 | evidence_52 | REPORT_EXPOSED_PII; REDACT_RECORD; VERIFY_RECORD_REDACTED |

No accepted regression in public status, exact-case count, step content, citation integrity, evidence validity, or case coverage. An initial stricter phrase matcher omitted legitimate delivery-query/details conversations; those trial candidates were rejected, the evidence phrases were covered by counterexamples, and the final run removes no baseline steps.

Integrity checks validate every candidate finding against accepted policy decisions and the exact observed witness. Citation/resource checks cover every emitted cited step. Support provenance checks cover 7 public and 192 full-run predicates, with zero failures. These deterministic consistency checks supplement adapter counterexamples; they do not constitute independent semantic proof of every source interpretation.

## Tests and reproducibility

All 147 tests pass (128 baseline tests; 19 added counterexamples/metric tests). The former test expecting an empty plan for an exposed tombstone was updated to assert the newly authorized safe redaction plan and continuing unresolved relationship. Public evaluation repeats predictions for determinism. The separately generated public CSV is byte-identical to its benchmark CSV.

Counterexamples include: exposed versus clean tombstones with unresolved security retention; an exposed tombstone without any retained record; missing/wrong stable references and missing subject lineage; excerpts versus full message_text; explicit incomplete scan scope; invalid boolean types; sole versus unknown/shared attachment ownership; SQL/JSON/log/screenshot provenance; source-copy and time boundaries; and semantic citation/missing-phase evaluation.

```bash
python3 -m unittest discover -s tests -q
python3 code/evaluation/main.py --all-samples --mode prediction --output-dir artifacts/accuracy-improvement/after-public
python3 code/main.py --all --requests dataset/sample_deletion_requests.csv --mode prediction --output artifacts/accuracy-improvement/public-candidate.csv --diagnostics artifacts/accuracy-improvement/public-details.json
python3 code/main.py --all --mode prediction --output artifacts/accuracy-improvement/candidate-518.csv --diagnostics artifacts/accuracy-improvement/candidate-518.json
python3 code/evaluation/accuracy_changes.py --directory artifacts/accuracy-improvement
python3 code/tools/validate_candidate.py --output artifacts/accuracy-improvement/candidate-518.csv --diagnostics artifacts/accuracy-improvement/candidate-518.json
```

For an independent before-public run, use d79eb59 in a separate source checkout and the same public evaluation command with `before-public` as output directory. Copy the preserved root candidate into `artifacts/accuracy-improvement/baseline-518.csv` before comparison. Generated comparison.json contains every added/removed tuple. Candidate files and sidecars remain local under ignored artifacts/.

## Artifact preservation and usage

| File | SHA-256 |
| --- | --- |
| Preserved root output.csv | `b9045f0b71ec8025cfa1b67dd3b7ee5a82f7411787173743580d0f15aa9275b6` |
| Preserved root code.zip | `cd014d91ffbcf470bdde1acbf96d18767de74926b425b2a45ce605b2140663b7` |
| Separate full candidate | `5f30a16fb7b72a914ac7489e1a06e6967d19fefaf8c992858a7470f6a3e6c25f` |

Final separate full-dataset run: 518 requests, model providers/names: none, model calls: 0, input/output/total tokens: 0, average tokens/request: 0, estimated total/per-request cost: $0. Coding-assistant usage is not inference usage by the submitted pipeline. Root output.csv and code.zip were not overwritten.

## Remaining opportunities

1. Recover subject/resource lineage only from explicit admissible links, especially account absence and anonymized analytics. Never assign resource IDs from case numbers or record order.
2. Separate observed security-record presence from unresolved retention applicability, and locate supplied deadlines rather than infer indefinite retention.
3. Find authoritative whole-message scans, shared-context metadata, and exclusive-ownership evidence for support gaps. Excerpts and identifiers remain insufficient.
4. Add explicit tombstone-to-retained-record linkage before accepting clean tombstone verification; exposed-field redaction alone does not close the audit.
