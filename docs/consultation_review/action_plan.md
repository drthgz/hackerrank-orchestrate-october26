# Final-Hours Action Plan

**Decision gate: do not submit the current root `output.csv` + `code.zip` pair unchanged.** The repository does not configure an official October deadline, so this plan is relative to the remaining time. It prioritizes evidenced, reversible actions over speculative accuracy work.

## T-180 to T-120 minutes: choose and pin the candidate

1. Review the exact candidate row deltas in `artifacts/historical-lineage/candidate-full.csv` against root `output.csv`.
   - Four tombstone rows add 12 redaction-related steps.
   - Five connector rows add one directly cited `VERIFY_DATA_FLOW_DISABLED` check each.
   - No status changes; candidate validator reports 45 rather than 49 stronger-audit failures.
2. Decide whether to promote that candidate. Do not copy it blindly if its embedded diagnostic sidecar/hash is not the one being released.
3. Confirm the candidate is a competition prediction file, not a verified compliance report: 140 uncertain statuses and 302 incomplete/unproved plans remain.

## T-120 to T-90 minutes: integrate the one verified adapter gap

1. In `code/audit/identity.py`, recognize `subject_selector` as a stable reference only when it exactly equals a known `user_id`; preserve conflicting-ID rejection.
2. Add positive and negative production tests: known stable selector + disabled state, unknown selector, and selector conflicting with another stable reference.
3. Run the five cases from the lineage report. Accept the change only if it adds exactly the five expected connector checks, leaves statuses unchanged, and introduces no new validator failures.

## T-90 to T-60 minutes: validate in a supported environment

1. Ensure Poppler `pdftotext` is available as documented in the README. Do not claim the suite is green until the missing-dependency test failures are resolved.
2. Run the full 189-test suite and the candidate validator.
3. Generate a fresh 518-row output to a temporary path. Compare it against the selected candidate; inspect every changed case and reject unexplained differences.
4. Run both checks: structural/citation validation and the stronger audit validator. Record the distinct counts; passing the first does not imply passing the second.

## T-60 to T-30 minutes: synchronize the release

1. Update README, evaluation report, and usage report from the selected output hash and the actual final run. Keep runtime model/token cost at zero only if the final run indeed made zero calls.
2. Rebuild `code.zip` from the same working tree. Ensure all current source and required reports are inside and that referenced docs are included or links are removed.
3. Inspect ZIP integrity and member list; exclude dataset, output, credentials, caches, and nested archives.
4. Run clean extraction/replay with a fresh environment and compare its output hash to the intended external `output.csv`.

## T-30 minutes to submission: freeze and upload

1. Freeze code, CSV, and reports together; record SHA-256 for each.
2. Confirm 518 sorted unique rows, exact header, 10 N/A rows with `[]`, and zero unsupported citation/resource references.
3. State remaining uncertainty honestly: 140 fallback statuses and 45 stronger-audit failures for the latest candidate unless validation changes them. Do not call those rows complete audits.
4. Upload only the synchronized artifacts; do not substitute the stale root ZIP or claim hidden-set accuracy from the public sample.

## If less than one hour remains

Skip speculative policy/lineage work. The minimum safe sequence is: promote only after reviewing the 17 known evidence-backed additions, regenerate the archive/reports from the same source, run structural and strongest available validation, compare hashes, and submit with the unresolved semantic failures clearly recorded. If Poppler is unavailable, do not represent the clean replay or full test suite as passed.
