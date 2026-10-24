# Evidence sufficiency and submission conflict

This review uses only participant-facing evidence and saved predictor diagnostics. It reads no public or private answer labels. Raw identifier/resource hits are discovery aids; they do not establish policy, ownership or current state. Later captures are listed separately and cannot repair an earlier audit.

Coverage: **374/518**; **144 unresolved**. Recovered decisions from the original 151 blockers: case_513, case_514, case_515, case_517, case_518, case_519, case_61.

## A. Recoverable facts

Pipe-delimited observability logs contain service/trace/event headers that the previous parser discarded. Parsing those headers restores subject-correlated readbacks in evidence_21 and evidence_48. Ten formerly unlinked cases now have observations: six support a grounded INCOMPLETE decision; four still lack independent policy facts. The object-storage listing in evidence_46 plus the explicit ownership/filename/resource link in activity_4007 recovers case_61. The screenshot proves presence; the catalog proves sole ownership and identity. Both are available by the cutoff.

## B. Missing facts and current limits

| First remaining blocker | Cases |
| --- | ---: |
| Complete account deletion requires positive scoped profile-absence evidence | 69 |
| Compliant observations do not close the unprocessed evidence scope | 30 |
| No evidence-backed resources to verify | 43 |
| No supported evidence resource lineage links to subject | 2 |

Independent omissions below overlap the first blockers. Counts are cases with each reason, not physical-copy counts. A missing profile proof is often not the only gap.

| Independent policy/state gap | Cases |
| --- | ---: |
| Missing identifier fields needed to prove redaction/anonymization | 3 |
| Missing or invalid boolean fact: belongs_only_to_subject | 2 |
| Missing or invalid boolean fact: legal_hold_active | 2 |
| Missing or invalid boolean fact: shared_context | 25 |
| Missing or invalid boolean fact: text_scan_complete | 13 |
| Security retention applicability not established at audit time | 65 |
| Subject-linked activity resource lacks scoped evidence | 1 |
| Tombstone reference has no supported retained-record relationship | 8 |

case_103: evidence_10 contains audit_record_9522 for user_101 in both primary and read replica at the cutoff, but no retention deadline. Rule_12 is conditional on a supplied retention period. No evidence-backed deletion violation establishes INCOMPLETE; no account-absence/retention proof establishes COMPLETE. A seal or workflow event cannot supply a missing retention date.

case_126: evidence_87 has an explicit in-period security record, but no grounded account resource lineage for an account-absence step. An identifier search returning no profile cannot supply the missing account resource ID required by the output schema. No resource ID is derived from a user/case number.

case_55: evidence_32 shows backup_9287 and its subject but no restore permission/block. case_63: evidence_60 assigns marketing_001 to a different person than activity_4008. Overwriting the measured owner with the catalog claim would create an unsupported finding.

The JSON sidecar lists admissible and later raw matches for each original blocker, including resource IDs, citation IDs, missing policy facts and profile-absence coverage. A textual match alone is not a recovered fact. The review establishes what current extraction can prove; it does not claim that all ambiguous business evidence is intrinsically uninterpretable.

## C. Permitted output and required clarification

The supplied problem_statement.md requires 518 rows, exactly three statuses, evidence-backed COMPLETE verification, and findings plus a complete plan for INCOMPLETE. AGENTS.md §6.5 defines completeness over every relevant copy. Neither document defines an uncertainty status or permits unknown to mean INCOMPLETE. NOT_APPLICABLE requires non-deletion intent. An empty authorized-deletion plan, invented resource, inferred retention date or workflow-only proof cannot resolve this conflict.

Grounded INCOMPLETE rows with policy omissions remain reviewable partial plans; the statement does not explicitly permit them as complete answers or promise partial credit. Their status can be defensible while their plan remains incomplete. They are not a valid 518-row submission. The CLI therefore retains exit 2 and writes artifacts/supported.csv, not a fabricated output.csv.

Organizer clarification needed: (1) specify how to encode an authorized request when completion and violation are both unproved; (2) supply pre-cutoff subject/resource lineage for identity-free/absent records; (3) supply applicable retention deadlines, support-context and ownership facts; (4) define whether a scoped inventory with no matching profile permits COMPLETE without a profile resource verification step; (5) confirm whether partial plans are accepted and how they score. No organizer message has been sent.

## Original blocker disposition

| Case | Disposition | Remaining first blocker | Resources observed |
| --- | --- | --- | --- |
| case_103 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_9522 |
| case_107 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_7572 |
| case_108 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_1469 |
| case_111 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_8933 |
| case_112 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_4082, backup_4863, support_2859 |
| case_126 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_6884 |
| case_127 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_9649 |
| case_135 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_1417, audit_record_5140 |
| case_137 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_3734, audit_record_6779 |
| case_150 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_1584 |
| case_151 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_8905, backup_9557, data_flow_2437, support_5400 |
| case_152 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_3579 |
| case_155 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_4199, backup_161, support_7867 |
| case_157 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_8821 |
| case_160 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_9882, support_4148 |
| case_162 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_6362 |
| case_175 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_7166, backup_549, data_flow_4319, support_8164 |
| case_178 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_8521 |
| case_183 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_3262 |
| case_190 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_4417 |
| case_191 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_7493, backup_3010, data_flow_1611, support_5049 |
| case_204 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_2736, backup_9519, support_9505 |
| case_206 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_9878 |
| case_213 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_4413, backup_5626, data_flow_5279, support_1360 |
| case_215 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_1718 |
| case_218 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_8792 |
| case_219 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_3382 |
| case_221 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_3880 |
| case_225 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_9389 |
| case_226 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_9964 |
| case_231 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_4425, backup_6564, data_flow_2576, support_3964 |
| case_233 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_5264, audit_record_8350, backup_8162, data_flow_6754, support_9670 |
| case_235 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_886, audit_record_7103, backup_2775, data_flow_593, support_9391 |
| case_243 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_7202 |
| case_244 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_9314 |
| case_253 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_2927 |
| case_257 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_7193 |
| case_260 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_1876 |
| case_264 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_8316, audit_record_6711, backup_3250, data_flow_4885, support_9996 |
| case_265 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_5015, audit_record_6378 |
| case_267 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_8384, audit_record_6621 |
| case_274 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_6398 |
| case_276 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_8323 |
| case_277 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_8228, backup_9728, data_flow_2439, support_2036 |
| case_292 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_1125, audit_record_3432, backup_1825, data_flow_5598, support_1526 |
| case_294 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_4387 |
| case_295 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_1269 |
| case_297 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_7878, backup_7308, data_flow_3391, support_1983 |
| case_299 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_5194 |
| case_304 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_4759 |
| case_308 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_3221, backup_4917, support_6046 |
| case_309 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_1945 |
| case_313 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_7020 |
| case_314 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_7893 |
| case_319 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_7337 |
| case_322 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_3201 |
| case_324 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_1242, audit_record_4466, backup_6458, data_flow_4769, support_7249 |
| case_326 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_3785, audit_record_1219, backup_2894, data_flow_2468, support_305 |
| case_331 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_6814, audit_record_6731, backup_9376, data_flow_8534, support_1403 |
| case_335 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_711, backup_3136, data_flow_7452, support_4712 |
| case_336 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_5022 |
| case_339 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_2922 |
| case_343 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_9233 |
| case_345 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_454 |
| case_346 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_1700 |
| case_351 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_8787, backup_024, data_flow_4323, support_7137 |
| case_354 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_9286 |
| case_362 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_8638 |
| case_369 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_8590, audit_record_337 |
| case_383 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_5043, audit_record_989 |
| case_390 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_7618, audit_record_101, backup_5165, data_flow_5737, legal_hold_8049, support_5720 |
| case_392 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_1718, audit_record_7510 |
| case_393 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_7330 |
| case_395 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_2839 |
| case_398 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_7361 |
| case_403 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_4733 |
| case_408 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_4216 |
| case_409 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_2559 |
| case_41 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_4051, audit_record_7814, backup_706, data_flow_2901, support_2667 |
| case_411 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_4330 |
| case_412 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_5637 |
| case_423 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_8082 |
| case_424 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_1474 |
| case_427 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_999 |
| case_430 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_5292 |
| case_44 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_2064, audit_record_1105, backup_6266, data_flow_223, support_1066 |
| case_448 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_753 |
| case_45 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_003 |
| case_452 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_8608 |
| case_456 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_8176 |
| case_457 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_1171 |
| case_458 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_6750 |
| case_46 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_6523 |
| case_460 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_1369, legal_hold_5622, support_4146 |
| case_462 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_641 |
| case_463 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_8444, backup_2005, data_flow_8024, support_2659 |
| case_464 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_5183, backup_7400, data_flow_1344, support_5586 |
| case_467 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_8992 |
| case_470 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_2706 |
| case_479 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_5745, support_4665 |
| case_480 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_7742, backup_7706, data_flow_2893, support_5854 |
| case_484 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | support_7973 |
| case_493 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_730 |
| case_494 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_1112 |
| case_497 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_9796 |
| case_502 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_5238 |
| case_503 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_5454, support_2295 |
| case_506 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_1361 |
| case_508 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_8154, support_2691 |
| case_51 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_3610, audit_record_3308, backup_7809, data_flow_4713, support_1097 |
| case_512 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_4219 |
| case_513 | A_RECOVERED_DECISION | Recovered | account_1334, audit_record_2044, search_4739 |
| case_514 | A_RECOVERED_DECISION | Recovered | account_6473, analytics_9920, audit_record_1967, data_flow_9556, search_2715, support_3982 |
| case_515 | A_RECOVERED_DECISION | Recovered | account_3411, audit_record_7062, search_1928, support_4533 |
| case_516 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_141, audit_record_3777 |
| case_517 | A_RECOVERED_DECISION | Recovered | account_3407, audit_record_946, data_flow_8165, search_2818 |
| case_518 | A_RECOVERED_DECISION | Recovered | account_9641, audit_record_5572, data_flow_3518, search_6401 |
| case_519 | A_RECOVERED_DECISION | Recovered | account_1506, audit_record_4027, backup_8264 |
| case_520 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_4979, audit_record_9504, support_9251 |
| case_521 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_1482, audit_record_3567 |
| case_522 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_1096, audit_record_5513, support_8538 |
| case_524 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_5429 |
| case_530 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_2152 |
| case_532 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_4828, backup_6344, data_flow_6987, support_7724 |
| case_543 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_6244, tombstone_205 |
| case_544 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_1037, tombstone_8648 |
| case_545 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_5041, tombstone_946 |
| case_546 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_518, tombstone_8095 |
| case_547 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_7352, tombstone_8774 |
| case_548 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_6970, tombstone_3745 |
| case_549 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_1491, tombstone_3963 |
| case_55 | B_UNRESOLVED_EVIDENCE | No supported evidence resource lineage links to subject | None |
| case_550 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_3831, tombstone_7389 |
| case_57 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_7219, backup_7711, support_7479 |
| case_58 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_8465 |
| case_59 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_962 |
| case_60 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | audit_record_629 |
| case_61 | A_RECOVERED_DECISION | Recovered | object_19 |
| case_63 | B_UNRESOLVED_EVIDENCE | No supported evidence resource lineage links to subject | None |
| case_64 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_1892, backup_3933, data_flow_6846, support_6334 |
| case_69 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_9011 |
| case_70 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_1738 |
| case_76 | B_UNRESOLVED_EVIDENCE | No evidence-backed resources to verify | support_9746 |
| case_77 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_9334, audit_record_5425, backup_7303, data_flow_7773, support_008 |
| case_81 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_9832, audit_record_9645, backup_3332, data_flow_3255, support_5953 |
| case_82 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_4156, audit_record_3747, backup_317, data_flow_9666, support_9166 |
| case_83 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_2449, audit_record_2636 |
| case_84 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_2387, audit_record_3787 |
| case_86 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_8473, audit_record_5580 |
| case_88 | B_UNRESOLVED_EVIDENCE | Compliant observations do not close the unprocessed evidence scope | account_868, audit_record_3825, support_2967 |
| case_97 | B_UNRESOLVED_EVIDENCE | Complete account deletion requires positive scoped profile-absence evidence | audit_record_8778 |
