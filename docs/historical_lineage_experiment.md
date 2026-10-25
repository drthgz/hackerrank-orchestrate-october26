# Historical evidence lineage experiment

Starting commit: `054aca8`. Prediction baseline: `91a8faf`. **No additional account-absence or anonymized-analytics verification was recoverable.** A separate candidate recovers five disabled-connector checks through explicit stable subject selectors in SQL records. Production adapters, root `output.csv`, root `code.zip`, and the submission evaluation reports remain unchanged.

## Method and temporal index

The label-free experiment reads only participant-facing inputs. It scans all 94 manifest-listed artifacts, yielding 2,901 observations. At the maximum request cutoff, 2026-10-01T12:00:00Z, the global index contains 2,628 ownership-edge witnesses: 1,225 stable-reference observations, 1,390 unique historical-identifier observations, 12 explicit catalog links, and one documented source-resource reference. These are witness counts, including physical copies and repeated observations, **not additional recovered resources**. Each request queries the index again at its own `audit_at`; the global maximum-cutoff index is never substituted for a case-specific query.

`code/evaluation/lineage.py` keeps subject, system, resource, physical copy, observation time, evidence availability, provenance, source location and validity bounds. Audit changes supply old/new identifier intervals; unknown beginnings remain null. Snapshots cannot backfill earlier identifier ownership. Historical aliases can identify stale records only when unambiguous; shared or reused values require an explicit stable reference. Names, cohorts, row order, case IDs and numeric similarity never join records. Edge availability includes the latest availability of its identifier witnesses.

Resource intervals begin at a positive ownership observation and end at an admissible conflicting ownership observation. A null end means no supplied termination, not a guarantee of permanent ownership. Conflicting simultaneous links block continuity. Later capture cannot alter an earlier query. Catalog events establish a named association only; `SUCCESS` and other workflow results establish no record state. Forward trace lookup keys require an unambiguous resource namespace and owner. The documented `search_documents_primary.source_resource_id` supplies a typed account reference. SQL primary, regional and failover copies remain separate.

The index also preserves 300 raw readbacks that literally name `profile_service`. They stay in that namespace, with no inferred alias to `account_service` or invented policy category. They provide no incremental target links for the evaluated request subjects/cutoffs. Query starts, thumbnail errors and deletion-marker messages do not prove ownership or completed mutation. The supplied commercial statement PDF identifies its customer and statement; it does not prove export-job availability. Existing hash-bound screenshot transcriptions remain scoped to their visible fields. Six SQL observations with unknown stable subject references are rejected rather than assigned to a known subject.

Each resource diagnostic reports ownership, measured current state, and authoritative scope separately, and checks that the lineage actually joins the state observation at that time. A catalog-only resource can have proven lineage while lacking any state witness. An identity-free 404 can prove a resource readback returned absent while proving nothing about the request subject. No compliant check is emitted from either fact alone. All supplied copies must agree on compliance; a newer state-changing activity requires a newer readback. These checks do not certify that all unknown physical copies or the whole case have been exhausted.

## Incremental links and recoverable checks

Compared with baseline per-case observation ledgers, the index adds one public association and nine full-dataset associations (15 edge witnesses). Four full associations are already supplied catalog links; they are newly explicit in this ledger, not newly discovered evidence. Five are additional direct subject/resource associations from SQL connector configurations, covering 11 physical copies. There is **no newly recovered historical path to an account or anonymous analytics resource**.

| Full request | Subject | Resource | Citation | Copies | Result |
| --- | --- | --- | --- | ---: | --- |
| case_57 | user_55 | data_flow_1368 | evidence_05 | 2 | Add VERIFY_DATA_FLOW_DISABLED |
| case_112 | user_110 | data_flow_3444 | evidence_10 | 2 | Add VERIFY_DATA_FLOW_DISABLED |
| case_155 | user_153 | data_flow_4305 | evidence_15 | 2 | Add VERIFY_DATA_FLOW_DISABLED |
| case_204 | user_202 | data_flow_5877 | evidence_20 | 2 | Add VERIFY_DATA_FLOW_DISABLED |
| case_308 | user_306 | data_flow_8933 | evidence_29 | 3 | Add VERIFY_DATA_FLOW_DISABLED |

Every cited SQL payload explicitly contains its resource ID, `subject_selector` equal to the stable subject reference, and boolean `enabled=false`. Every supplied copy agrees, its capture and observation precede the request cutoff, and no newer activity contradicts the readback. Each logical check has a single evidence file covering all its copies. The baseline SQL matcher recognizes `user_id`/`customer_reference` but omits stable `subject_selector`; the experiment recognizes that typed field. This is a current-record adapter gap, not a historical-ownership extrapolation. The candidate adds one verification step per row and renumbers canonically. It preserves the existing COMPLETE predictions and their uncertainty diagnostics; it makes no whole-case certification.

The other four full associations are export_service/export_1842 (case_33), identity_service/tombstone_17 (case_46), backup_service/backup_9287 (case_55), and marketing_platform/marketing_001 (case_63). Catalog lineage supplies no new compliant-state proof for them. Two were already present in baseline activity-omission diagnostics; two fall into baseline cases whose fallback sidecars lack such observations. The public association is tombstone_17 in case_17, already mentioned in its baseline omissions. No CSV step follows from those catalog links.

## Unresolved account and analytics checks

After both candidate CSVs were written, public references were opened strictly for evaluation. They identify 27 missing target checks: 20 account-absence checks and seven analytics-anonymization checks. Fourteen target resource IDs have no located token in the manifest-listed artifacts; one occurs only in late evidence; twelve have an admissible raw artifact but no proven subject/resource lineage. All 27 remain unasserted. Token matches locate evidence; they never assign ownership.

| Public cases | Missing resources | Located evidence and limitation |
| --- | --- | --- |
| case_01, case_02, case_04 | account_001; account_002; account_004 | No located resource witness |
| case_03 | analytics_9406 | evidence_94: cleared identifiers, null lookup key, no prior owner |
| case_04 | analytics_901 | evidence_56: anonymous report with no prior subject/resource link |
| case_07, case_08, case_10 | account_007; account_008; account_010 | No located resource witness |
| case_09 | account_3960 | evidence_06 is captured after audit_at |
| case_18, case_20 | account_5521; account_5037 | No located resource witness |
| case_21 | account_6440; analytics_5335 | evidence_92 supplies identity-free state; evidence_02 is late |
| case_22, case_23 | account_4990; account_410 | No located resource witness |
| case_25 | account_3136; analytics_1895 | evidence_92 supplies identity-free state; evidence_02 is late |
| case_26 | account_5684; analytics_4566 | evidence_92 supplies identity-free state; evidence_02 is late |
| case_27 | account_3866; analytics_4574 | evidence_92 supplies identity-free state; evidence_02 is late |
| case_28 | account_5482; analytics_6077 | evidence_92 supplies identity-free state; analytics also occurs in late evidence_02 |
| case_29, case_30, case_31, case_32 | account_7012; account_4163; account_4857; account_8858 | No located resource witness |

In particular, account_6440 appears only as an identity-free 404. Analytics_9406 appears only with null customer/direct identifiers and the general shopper cohort. Neither the twelve catalog events nor the historical identifier-bearing records supplies the missing owner. The experiment does not interpret absence from the subject's matched observations as positive account absence, reconstruct a resource ID from a case number, or transfer ownership between records that share a cohort.

## Measurements against 91a8faf

Fresh public and full baseline runs reproduce the preserved 91a8faf candidates byte for byte. The production audit code has no changes between 91a8faf and 054aca8. Public labels never enter the index or candidate generation.

| Metric | Baseline | Lineage candidate |
| --- | ---: | ---: |
| Public status accuracy | 32/32 (100%) | 32/32 (100%) |
| Exact public cases | 2/32 (6.25%) | 2/32 (6.25%) |
| Step precision | 132/135 (97.777778%) | 132/135 (97.777778%) |
| Step recall | 132/193 (68.393782%) | 132/193 (68.393782%) |
| Aligned citation correctness | 50/50 (100%) | 50/50 (100%) |
| New full checks with direct citation proof | — | 5/5, covering 11 copies |
| Newly recoverable account/analytics checks | — | 0 |
| Newly recoverable connector checks | — | 5 |
| Public changed rows | — | 0/32 |
| Full changed rows | — | 5/518 |
| New audit-validator failures | — | 0 public; 0 full |
| Existing stronger-validator failures | 4 public; 45 full | 4 public; 45 full |

Exact public cases remain case_05 and case_06. All 32 public rows are unchanged, including their sequence and citations. Missing public phases remain four FINDING, four REMEDIATION and 53 VERIFICATION steps. The three supported object_storage/object_19 steps remain extra against the reference. The 50/50 citation measure concerns aligned reference steps; the extra public citation has independent provenance, and all 51 emitted public citations meet the existing cutoff/structural checks. Full reference accuracy is unavailable; the five new full citations are source audits, not benchmark-label accuracy claims.

Full changes are exactly case_57, case_112, case_155, case_204 and case_308, all retaining COMPLETE. Each adds the one tabled step and removes no step. Existing stronger-validator failures are retained in the JSON report; public failures remain case_01, case_02, case_04 and case_31 with empty authorized-deletion plans. The CSV validator passes all 518 candidate rows with sorted, unique and complete request coverage. Finding support and support-fact provenance checks introduce no failure. The stronger validator is not an exhaustive semantic certification.

## Adversarial validation

All **189 tests pass**, including 26 new lineage tests. Counterexamples cover shared identifiers across people, historical identifier rotation, reused identifiers, future identity snapshots, resource reassignment, stable/alias conflicts, simultaneous ownership conflicts, primary/replica disagreement, identity-free 404 responses, anonymous records without prior ownership, incomplete analytics payloads, late capture, later historical-alias availability, newer workflow claims, ambiguous cross-system resource tokens, row-order/cohort similarity, and workflow successes. Positive controls recover a scoped absence check and an anonymized-record check when valid prior ownership exists. A fixture with arbitrary subject/resource/request strings verifies that a cited disabled-selector check is emitted without loading any reference labels.

The experiment remains isolated from production. No models are called at runtime: providers/models none, calls 0, input/output/total tokens 0, average tokens/request 0, total and per-request inference cost $0. This excludes coding-assistant usage. No push, packaging or submission occurred.

## Files and reproduction

Separate generated files live under ignored `artifacts/historical-lineage/`: baseline-public/full.csv and JSON, candidate-public/full.csv and JSON, index.json, lineage-public/full.json, report.json, and preserved-hashes.json. The full index contains alias intervals and provenance; per-case ledgers contain admissible edges, rejected associations and unlinked target observations. The report includes the complete 27-target evidence inventory, new edge/copy proofs, exact added steps and all existing validator failures.

| Artifact | SHA-256 |
| --- | --- |
| Baseline and candidate public CSV | `868a7c3ebf14db3d04663b85cd2cce0907783d8a8b35713fbe7b665694e762c9` |
| Baseline full CSV | `5f30a16fb7b72a914ac7489e1a06e6967d19fefaf8c992858a7470f6a3e6c25f` |
| Candidate full CSV | `51ea84c5e2b8e66af019d321421ed6d383e5e95df16244bd41af3822eb25610d` |
| Preserved root output.csv | `b9045f0b71ec8025cfa1b67dd3b7ee5a82f7411787173743580d0f15aa9275b6` |
| Preserved root code.zip | `cd014d91ffbcf470bdde1acbf96d18767de74926b425b2a45ce605b2140663b7` |

Run from the repository root:

```bash
python3 -m unittest discover -s tests -q
python3 code/main.py --all --requests dataset/sample_deletion_requests.csv --mode prediction --output artifacts/historical-lineage/baseline-public.csv --diagnostics artifacts/historical-lineage/baseline-public.json
python3 code/main.py --all --mode prediction --output artifacts/historical-lineage/baseline-full.csv --diagnostics artifacts/historical-lineage/baseline-full.json
python3 code/evaluation/historical_lineage.py --directory artifacts/historical-lineage
```

**Stop decision:** explicit links and historical identifier-bearing evidence yield no admissible new lineage for the unresolved account/analytics checks. Stop this search without speculative heuristics. Recommend release preparation, keeping the five-check candidate separate for review and documenting the unresolved ownership/state/scope limits. Root submission artifacts still contain the preserved older release, so candidate selection and any future packaging must be explicit follow-up work.
