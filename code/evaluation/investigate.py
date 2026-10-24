"""Label-free evidence-sufficiency review of a saved deterministic run.

Raw hits are discovery aids, never new state observations or prediction labels.
The report separates recovered decisions, policy omissions and first proof gates.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit.inputs import load_inputs
from audit.identity import resolve_subject
from audit.models import timestamp
from audit.pdf_evidence import read_pdf
from audit.reviewed_images import review

ROOT = Path(__file__).resolve().parents[2]


def inventory_text(file):
    if file.path.suffix == '.pdf':
        return '\n'.join(read_pdf(file).pages)
    if file.path.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
        return json.dumps(review(file) or {}, ensure_ascii=False)
    return file.path.read_text(encoding='utf-8')


def investigate(run_path, baseline_path=None):
    inputs = load_inputs(ROOT / 'dataset', ROOT / 'dataset/deletion_requests.csv')
    run = json.loads(run_path.read_text())
    unsupported = run['summary']['unsupported']
    baseline = json.loads(baseline_path.read_text())['summary']['unsupported'] if baseline_path else unsupported
    texts = {f.file_id: inventory_text(f) for f in inputs.evidence}
    records = {}
    for request in inputs.requests:
        if request.case_id not in baseline and request.case_id not in unsupported:
            continue
        detail = run['cases'].get(request.case_id, {})
        subject = resolve_subject(request.email, request.audit_at, inputs.identities, inputs.history)
        observations = detail.get('observations', [])
        resources = sorted({o['resource_id'] for o in observations})
        selectors = {subject.user_id, *subject.aliases['email'], *subject.aliases['email_hash'], *resources}
        pattern = re.compile(r'(?<![\w@.])(?:' + '|'.join(re.escape(k) for k in sorted(selectors) if k) + r')(?![\w@.])', re.I)
        hits = [dict(file_id=f.file_id, captured_at=f.captured_at.isoformat(),
                     admissible=f.captured_at <= request.audit_at,
                     matching_lines=[n for n, line in enumerate(texts[f.file_id].splitlines(), 1) if pattern.search(line)])
                for f in inputs.evidence if pattern.search(texts[f.file_id])]
        missing = sorted({x['reason'] for x in detail.get('omissions', [])})
        # Early lineage failures have no attached pipeline details. Raw hits
        # explicitly remain unclassified, rather than treated as proof.
        records[request.case_id] = dict(
            previous_blocker=baseline.get(request.case_id), blocker=unsupported.get(request.case_id),
            classification='A_RECOVERED_DECISION' if request.case_id not in unsupported else 'B_UNRESOLVED_EVIDENCE',
            resources=resources, policy_or_state_gaps=missing,
            observation_citations=sorted({o['evidence_id'] for o in observations}),
            profile_absence_observed=any(o['category'] == 'USER_PROFILE' and not o['present'] for o in observations),
            unprocessed_formats=detail.get('unprocessed_evidence_formats', []),
            raw_identifier_or_resource_hits=hits,
        )
    return dict(
        attempted=run['summary']['attempted'], produced=run['summary']['produced'],
        baseline_unsupported=len(baseline), remaining_unsupported=len(unsupported),
        recovered=sorted(cid for cid in baseline if cid not in unsupported),
        first_blockers=dict(Counter(unsupported.values())),
        independent_gaps=dict(Counter(reason for cid, r in records.items() if cid in unsupported
                                      for reason in r['policy_or_state_gaps'])),
        cases=records,
    )


def markdown(report):
    lines = ['# Evidence sufficiency and submission conflict', '',
             'This review uses only participant-facing evidence and saved predictor diagnostics. '
             'It reads no public or private answer labels. Raw identifier/resource hits are discovery aids; '
             'they do not establish policy, ownership or current state. Later captures are listed separately '
             'and cannot repair an earlier audit.', '',
             f"Coverage: **{report['produced']}/{report['attempted']}**; **{report['remaining_unsupported']} unresolved**. "
             f"Recovered decisions from the original {report['baseline_unsupported']} blockers: "
             + ', '.join(report['recovered']) + '.', '',
             '## A. Recoverable facts', '',
             'Pipe-delimited observability logs contain service/trace/event headers that the previous parser '
             'discarded. Parsing those headers restores subject-correlated readbacks in evidence_21 and '
             'evidence_48. Ten formerly unlinked cases now have observations: six support a grounded '
             'INCOMPLETE decision; four still lack independent policy facts. The object-storage listing '
             'in evidence_46 plus the explicit ownership/filename/resource link in activity_4007 recovers '
             'case_61. The screenshot proves presence; the catalog proves sole ownership and identity. '
             'Both are available by the cutoff.', '',
             '## B. Missing facts and current limits', '',
             '| First remaining blocker | Cases |', '| --- | ---: |']
    lines.extend(f'| {reason} | {n} |' for reason, n in sorted(report['first_blockers'].items()))
    lines += ['', 'Independent omissions below overlap the first blockers. Counts are cases with each reason, '
              'not physical-copy counts. A missing profile proof is often not the only gap.', '',
              '| Independent policy/state gap | Cases |', '| --- | ---: |']
    lines.extend(f'| {reason} | {n} |' for reason, n in sorted(report['independent_gaps'].items()))
    lines += ['',
              'case_103: evidence_10 contains audit_record_9522 for user_101 in both primary and read replica '
              'at the cutoff, but no retention deadline. Rule_12 is conditional on a supplied retention period. '
              'No evidence-backed deletion violation establishes INCOMPLETE; no account-absence/retention '
              'proof establishes COMPLETE. A seal or workflow event cannot supply a missing retention date.', '',
              'case_126: evidence_87 has an explicit in-period security record, but no grounded account '
              'resource lineage for an account-absence step. An identifier search returning no profile '
              'cannot supply the missing account resource ID required by the output schema. '
              'No resource ID is derived from a user/case number.', '',
              'case_55: evidence_32 shows backup_9287 and its subject but no restore permission/block. '
              'case_63: evidence_60 assigns marketing_001 to a different person than activity_4008. '
              'Overwriting the measured owner with the catalog claim would create an unsupported finding.', '',
              'The JSON sidecar lists admissible and later raw matches for each original blocker, including '
              'resource IDs, citation IDs, missing policy facts and profile-absence coverage. A textual match '
              'alone is not a recovered fact. The review establishes what current extraction can prove; '
              'it does not claim that all ambiguous business evidence is intrinsically uninterpretable.', '',
              '## C. Permitted output and required clarification', '',
              'The supplied problem_statement.md requires 518 rows, exactly three statuses, evidence-backed '
              'COMPLETE verification, and findings plus a complete plan for INCOMPLETE. AGENTS.md §6.5 '
              'defines completeness over every relevant copy. Neither document defines an uncertainty '
              'status or permits unknown to mean INCOMPLETE. NOT_APPLICABLE requires non-deletion intent. '
              'An empty authorized-deletion plan, invented resource, inferred retention date or workflow-only '
              'proof cannot resolve this conflict.', '',
              'Grounded INCOMPLETE rows with policy omissions remain reviewable partial plans; the statement '
              'does not explicitly permit them as complete answers or promise partial credit. Their status '
              'can be defensible while their plan remains incomplete. They are not a valid 518-row submission. '
              'The CLI therefore retains exit 2 and writes artifacts/supported.csv, not a fabricated output.csv.', '',
              'Organizer clarification needed: (1) specify how to encode an authorized request when '
              'completion and violation are both unproved; (2) supply pre-cutoff subject/resource lineage '
              'for identity-free/absent records; (3) supply applicable retention deadlines, support-context '
              'and ownership facts; (4) define whether a scoped inventory with no matching profile permits '
              'COMPLETE without a profile resource verification step; (5) confirm whether partial plans '
              'are accepted and how they score. No organizer message has been sent.', '',
              '## Original blocker disposition', '',
              '| Case | Disposition | Remaining first blocker | Resources observed |', '| --- | --- | --- | --- |']
    for cid, record in sorted(report['cases'].items()):
        lines.append(f"| {cid} | {record['classification']} | {record['blocker'] or 'Recovered'} | {', '.join(record['resources']) or 'None'} |")
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, default=ROOT / 'artifacts/submission-run.json')
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    report = investigate(args.run, args.baseline)
    (ROOT / 'artifacts/evidence-sufficiency.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    (ROOT / 'docs/evidence_sufficiency.md').write_text(markdown(report))
    print(json.dumps({k: v for k, v in report.items() if k != 'cases'}, indent=2))
