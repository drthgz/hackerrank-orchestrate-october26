# Combined policy completeness experiment

Baseline: `91a8faf`. Defect baseline: `docs/accuracy_gap_analysis.md`. Outcome: **no additional CSV steps accepted**. The supplied operation meanings do not support either proposed relaxation. Production prediction, policy, adapters, planner and validators remain unchanged. Accepted work is evaluation-only fact/policy separation, independent diagnostic tracks, counterexamples, and reproducible reports.

## Official contract and experimental method

Sources reviewed: the complete supplied `problem_statement.md`, top-level `AGENTS.md` (especially §§6.3–6.6), and `dataset/deletion_rules.csv`. These local challenge sources define the experiment; no external legal standard or inferred organizer clarification was substituted.

- `VERIFY_RECORD_PRESENT`: “Confirm that a policy-required retained record still exists.” Rule_12 retains SECURITY_AUDIT_LOG only when “Record is within the supplied retention period.” A measured row is not, by itself, proof that the supplied retention condition applies.
- `REPORT_EXPOSED_PII` asserts identifiers that should have been redacted or anonymized; `REPORT_REMAINING_RECORD` asserts a record that should have been deleted. Neither is a neutral observation operation.
- Rule_05 permits REDACT for shared support context; rule_06 permits DELETE for a subject-exclusive attachment. Category membership and subject matching do not establish these conditions.
- INCOMPLETE requires findings, the complete remediation plan, and post-remediation checks. A finding with unknown treatment cannot be made compliant by emitting a guessed remedy or omitting the remedy.

The new evaluation-only `policy_tracks.py` retains observed presence/exposure, witness IDs/source locations/times, explicit deadlines and support predicates separately from an independently evaluated policy result. Inadmissible or unlinked observations supply no asserted facts. Excerpt-scan results retain excerpt scope. Missing predicates produce no action, no compliant-state claim and no new submission steps. Track A cannot resolve Track B, and combining tracks cannot promote facts to policy conclusions.

Fresh public and full predictions were generated with the unchanged 91a8faf pipeline and reproduced its preserved candidates byte for byte. Track A, Track B and combined diagnostics ran independently against the same immutable observations. Their CSVs were separately serialized and validated. Because neither emission change is contract-permitted, the three candidates intentionally equal the baseline; these are diagnostic ablations, not three different scoring policies. The combined ledger is asserted equal to the union of the independent ledgers. Public labels were opened only afterward for metrics and omission-target inventory; they are never read by production prediction or the track functions.

## Track A — security retention

**Rejected emission change:** using VERIFY_RECORD_PRESENT as mere observed presence. The operation includes a policy-required retention assertion, and the fixed CSV schema has no field that can qualify it as retention-unresolved. A blank evidence_id in an INCOMPLETE future check does not remove the policy assertion. An integrity seal proves no retention deadline. No indefinite period or legal obligation was inferred.

Of the 18 missing public security checks, 11 have admissible subject-linked presence but no supplied deadline/duration establishing applicability; these include 13 physical-copy observations because two resources have primary and replica rows. Five have only a later-captured evidence artifact, despite earlier embedded event times. Two have no located artifact witness. The resource-token search is a discovery inventory, not an independent ownership/state proof.

| Public case | Security resource | Admissible witness / availability issue | Decision |
| --- | --- | --- | --- |
| case_09 | audit_record_4902 | evidence_06 captured 2026-09-18T11:55:24+00:00 | Only after audit_at 2026-09-16T09:00:00+00:00 |
| case_11 | audit_record_9394 | evidence_03 | Presence established; supplied retention condition unresolved |
| case_12 | audit_record_2945 | evidence_01 | Presence established; supplied retention condition unresolved |
| case_13 | audit_record_4816 | evidence_03 | Presence established; supplied retention condition unresolved |
| case_14 | audit_record_987 | evidence_03 | Presence established; supplied retention condition unresolved |
| case_15 | audit_record_1596 | evidence_01 | Presence established; supplied retention condition unresolved |
| case_16 | audit_record_9528 | evidence_05 | Presence established; supplied retention condition unresolved |
| case_17 | audit_record_1797 | evidence_01 | Presence established; supplied retention condition unresolved |
| case_18 | audit_record_6645 | No located resource witness | Presence and lineage unavailable |
| case_19 | audit_record_6793 | evidence_01 | Presence established; supplied retention condition unresolved |
| case_20 | audit_record_5569 | No located resource witness | Presence and lineage unavailable |
| case_22 | audit_record_3482 | evidence_05 | Presence established; supplied retention condition unresolved |
| case_23 | audit_record_4128 | evidence_02 captured 2026-09-17T12:00:00+00:00 | Only after audit_at 2026-09-15T12:00:00+00:00 |
| case_24 | audit_record_7095 | evidence_02 captured 2026-09-17T12:00:00+00:00 | Only after audit_at 2026-09-15T12:00:00+00:00 |
| case_29 | audit_record_3954 | evidence_02 captured 2026-09-17T12:00:00+00:00 | Only after audit_at 2026-09-15T12:00:00+00:00 |
| case_30 | audit_record_1707 | evidence_02 captured 2026-09-17T12:00:00+00:00 | Only after audit_at 2026-09-15T12:00:00+00:00 |
| case_31 | audit_record_6909 | evidence_51 | Presence established; supplied retention condition unresolved |
| case_32 | audit_record_7068 | evidence_51 | Presence established; supplied retention condition unresolved |

Checks of raw text handover entries, security readback log lines, SQL primary/replica payloads and JSON security snapshots confirm the distinction: FOUND/rows=1 and integrity fields are present, but no interval or deadline for those eleven target resources is supplied. No matching system_activity row supplies their missing deadlines. Available, explicit retention_until values on other subject-linked records continue to support normal policy decisions; dates are not transferred between subjects or invented from category membership.

Across all public observations, the independent security ledger contains 19 physical-copy observations: 6 with established retention policy and 13 unresolved. Across the 518-request run: 436 observations, 99 established and 337 unresolved. These are per-request physical-copy counts, not additional recovered steps or globally unique records.

## Track B — support context and ownership

**Rejected emission change:** putting neutral exposure/presence into a policy-violation finding while remediation remains unresolved. Facts survive in the diagnostic ledger, but the official operation semantics and plan requirements prevent that CSV transformation. Existing evidence-backed support plans remain untouched.

| Public cases | Target resources | Missing steps | Established facts | Missing proof |
| --- | --- | ---: | --- | --- |
| case_11, case_18, case_19 | support_864; support_5569; support_9553 | 9 | Subject-linked positive PII exposure from evidence_03, evidence_94, evidence_01 respectively | Shared conversation context required for REDACT; no authorized alternative treatment inferred |
| case_13 | support_4218 | 3 | Subject-linked attachment exists in evidence_03 | Subject-exclusive ownership required for DELETE |
| case_26–case_28 | support_4715; support_4707; support_2351 | 3 | Cleared contact fields and shared order context in evidence_92; no identifier hit in the excerpt | No complete-text scan; later evidence_02 remains after the cutoff |

The 15 omissions are nine finding/remediation/verification steps for three exposed messages, three attachment steps, and three clean-message checks. A null requester field or an excerpt with no identifier hit does not establish a clean full message. SUPPORT_MESSAGE does not imply shared_context; matching a subject does not imply sole attachment ownership. No REDACT-versus-DELETE default was added.

The public support ledger contains 11 observations: 4 policy-established and 7 unresolved; 7 show positive exposure. The 518-request ledger contains 227 observations: 62 established and 165 unresolved; 120 show positive exposure. Some positive exposure is already handled by established policy. Raw observations remain distinct from permission to mutate data.

## Independent and combined evaluation

| Metric | 91a8faf baseline | Track A | Track B | Combined |
| --- | ---: | ---: | ---: | ---: |
| Public status accuracy | 32/32 (100%) | 32/32 (100%) | 32/32 (100%) | 32/32 (100%) |
| Exact public cases | 2/32 (6.25%) | 2/32 (6.25%) | 2/32 (6.25%) | 2/32 (6.25%) |
| Step precision | 132/135 (97.777778%) | 132/135 (97.777778%) | 132/135 (97.777778%) | 132/135 (97.777778%) |
| Step recall | 132/193 (68.393782%) | 132/193 (68.393782%) | 132/193 (68.393782%) | 132/193 (68.393782%) |
| Positional field accuracy | 716/1365 (52.454212%) | 716/1365 (52.454212%) | 716/1365 (52.454212%) | 716/1365 (52.454212%) |
| Aligned citation correctness | 50/50 (100%) | 50/50 (100%) | 50/50 (100%) | 50/50 (100%) |
| Public stronger audit-validator failures | 4 | 4 | 4 | 4 |
| Full stronger audit-validator failures | 45 | 45 | 45 | 45 |
| Public changed rows | — | 0 | 0 | 0 |
| Full changed rows against 91a8faf | — | 0/518 | 0/518 | 0/518 |
| Unsupported findings detected | 0 | 0 | 0 | 0 |
| Temporally invalid emitted findings/citations | 0 | 0 | 0 | 0 |
| Support-fact provenance failures | 0 | 0 | 0 | 0 |

All variants preserve 32 public rows and all 518 full request IDs, sorted and unique. No statuses, steps, citations or sequences change. Exact cases remain case_05 and case_06. Missing finding/remediation/verification counts remain 4/4/53. Three supported object-storage steps remain extra against the public reference; they were not removed to improve scoring. All 51 emitted public citations pass provenance/cutoff checks; 50 align with reference cited steps and the extra citation is the already documented object-storage resource.

The four public stronger-validator failures remain case_01, case_02, case_04 and case_31: authorized deletions have empty step arrays. Full failures remain the same 45 rows; the complete case list and reasons are in each full JSON sidecar. This validator is stronger than CSV structure validation (nonempty plans, all phases and paired remediation/checks) but is not a semantic policy or exhaustive-evidence certification. Independent policy assessment and finding/provenance/cutoff checks remain necessary. No new failure was introduced or hidden.

## Accepted and rejected changes

Accepted: evaluation-only fact ledgers, provenance/scope preservation, independent policy outcomes, immutable-track combination checks, candidate/report tooling, and 16 new positive/negative counterexample tests. All **163 tests pass**. The positive tests preserve supported retention, shared-message redaction, exclusive attachment deletion and complete clean scans. Negative tests cover seals without deadlines, expired/invalid/unanchored retention, absent records, late capture/observation, missing lineage, exposure without context, nonexclusive/unknown ownership and incomplete scans. A standalone finding without a remedy is rejected by the stronger validator.

Rejected: presence-only security verification; default or indefinite retention; using integrity fields as deadlines; standalone neutral CSV exposure findings; guessing support redaction/deletion; and converting excerpt scans into full-message clean checks. No speculative production changes were made, and no benchmark label or case ID appears in the track logic.

## Full-dataset impact and candidate files

All candidates are separate files under ignored `artifacts/combined-policy-experiment/`:

| Variant | Public CSV | 518-row CSV |
| --- | --- | --- |
| Preserved baseline | baseline-public.csv | baseline-full.csv |
| Security only | track-a-public.csv | track-a-full.csv |
| Support only | track-b-public.csv | track-b-full.csv |
| Combined | combined-public.csv | combined-full.csv |

Each variant also has a JSON ledger/report. `report.json` includes metrics, the 18/15 omission inventory, admissible witnesses, raw discovery locations, and all stronger-validator failures. The baseline JSON preserves the complete original pipeline sidecar. Candidate ledgers are supplemental diagnostics and do not replace it. Every candidate equals its corresponding baseline byte for byte.

| Artifact | SHA-256 |
| --- | --- |
| All public candidate CSVs | `868a7c3ebf14db3d04663b85cd2cce0907783d8a8b35713fbe7b665694e762c9` |
| All full candidate CSVs | `5f30a16fb7b72a914ac7489e1a06e6967d19fefaf8c992858a7470f6a3e6c25f` |
| Unchanged root output.csv | `b9045f0b71ec8025cfa1b67dd3b7ee5a82f7411787173743580d0f15aa9275b6` |
| Unchanged root code.zip | `cd014d91ffbcf470bdde1acbf96d18767de74926b425b2a45ce605b2140663b7` |

Root output.csv still holds the older preserved release; the 91a8faf experiment baseline is the separate full candidate, not root output.csv. Nothing was packaged, pushed or submitted. Full runtime inference usage: 518 requests; providers/models none; calls 0; input/output/total tokens 0; average tokens/request 0; total/per-request inference cost $0. These totals exclude coding-assistant usage.

## Optional lineage review and next improvement

Inspected the 12 explicit LINK_RESOURCE_IDENTITY catalog events and representative missing-lineage artifacts. They do not link account_6440 or analytics_9406 to the needed subject. evidence_92 gives an identity-free 404 for the former; evidence_94 gives lookup_key=null and cleared direct identifiers for the latter. General shopper cohort, chronology, resource numbering and row order supply no ownership edge. No speculative reconstruction was implemented. This is a scoped review, not a claim that every possible lineage path has been exhausted.

**Next recommended improvement:** add an auditable, time-scoped subject/resource/copy lineage index using only explicit source links and historical identifier-bearing observations, then verify whether any presently unlinked compliant records become reachable. For the 33 security/support steps examined here, the immediate blockers are actual missing retention/context/ownership/scan facts or a clarified official neutral-fact operation; relaxing policy semantics cannot recover them safely.

## Reproduction

```bash
python3 -m unittest discover -s tests -q
python3 code/main.py --all --requests dataset/sample_deletion_requests.csv --mode prediction --output artifacts/combined-policy-experiment/baseline-public.csv --diagnostics artifacts/combined-policy-experiment/baseline-public.json
python3 code/main.py --all --mode prediction --output artifacts/combined-policy-experiment/baseline-full.csv --diagnostics artifacts/combined-policy-experiment/baseline-full.json
python3 code/evaluation/combined_policy.py --directory artifacts/combined-policy-experiment
```

The baseline pipeline runs once per request split. Independent diagnostic tracks share only those immutable extracted observations, not each other's conclusions. Candidate writers validate every result; byte-identity checks establish that shared baseline integrity and stronger-validator results apply unchanged. Reference matching occurs after all candidate files are written.
