"""Evaluation-only semantic deltas and evidence/provenance integrity checks.

Labels enter only this reporting command, never an audit or prediction adapter.
"""
import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit.competition import best_effort_policy
from audit.contract import read_output
from audit.inputs import load_inputs
from audit.models import Observation, timestamp
from audit.prediction import validate_prediction
from audit.support_facts import FIELDS


def content(steps):
    return Counter(json.dumps({k: v for k, v in s.items() if k != 'step_no'}, sort_keys=True) for s in steps)


def load(path):
    with Path(path).open(newline='', encoding='utf-8') as f:
        return {r['case_id']: dict(status=r['deletion_status'], steps=json.loads(r['steps_json'])) for r in csv.DictReader(f)}


def metrics(predictions, labels):
    missing, extra, matched, predicted, expected = Counter(), 0, 0, 0, 0
    status, exact, citation_matches, citation_aligned, citation_emitted = 0, 0, 0, 0, 0
    wrong_aligned_citations = []
    for cid, label in labels.items():
        p = predictions[cid]
        left, right = content(p['steps']), content(label['steps'])
        matched += sum((left & right).values())
        predicted += sum(left.values()); expected += sum(right.values())
        extra += sum((left - right).values())
        for step, count in (right - left).items():
            missing[json.loads(step)['phase']] += count
        status += p['status'] == label['status']
        exact += p == label
        key = lambda s: (s['phase'], s['system_id'], s['resource_id'], s['operation'], s['state'])
        citations = {key(s): s['evidence_id'] for s in label['steps'] if s['evidence_id']}
        for s in p['steps']:
            if s['evidence_id']:
                citation_emitted += 1
                if key(s) in citations:
                    citation_aligned += 1
                    citation_matches += s['evidence_id'] == citations[key(s)]
                    if s['evidence_id'] != citations[key(s)]:
                        wrong_aligned_citations.append(dict(case_id=cid, step=s))
    return dict(cases=len(labels), correct_statuses=status, exact_cases=exact,
                matched_steps=matched, predicted_steps=predicted, expected_steps=expected,
                step_precision=matched/predicted, step_recall=matched/expected,
                missing_steps_by_phase=dict(missing), extra_steps_vs_reference=extra,
                aligned_citations_correct=citation_matches, aligned_citations=citation_aligned,
                emitted_citations=citation_emitted, incorrect_aligned_citations=wrong_aligned_citations)


def integrity(output, sidecar, inputs):
    details = json.loads(Path(sidecar).read_text())['cases']
    requests = {r.case_id: r for r in inputs.requests}
    rows = read_output(Path(output))
    assert [r.case_id for r in rows] == sorted(requests), 'Missing, duplicate or unsorted cases'
    assert set(details) == set(requests), 'Sidecar coverage mismatch'
    unsupported, failures, provenance_count = [], [], 0
    finding_ops = {'DELETE': 'REPORT_REMAINING_RECORD', 'REDACT': 'REPORT_EXPOSED_PII',
                   'ANONYMIZE': 'REPORT_EXPOSED_PII', 'DISABLE_DATA_FLOW': 'REPORT_ACTIVE_DATA_FLOW',
                   'BLOCK_RESTORE': 'REPORT_RESTORE_RISK'}
    for result in rows:
        request = requests[result.case_id]
        validate_prediction(result, request, inputs.citation_times())
        detail = details[result.case_id]
        latest = tuple(Observation(**o) for o in detail.get('latest_copy_states', []))
        decisions, _ = best_effort_policy(latest, inputs.rules, request.audit_at)
        for step in result.steps:
            if step.phase == 'FINDING' and not any(
                    not d.compliant and finding_ops.get(d.action) == step.operation
                    and d.observation.system_id == step.system_id and d.observation.resource_id == step.resource_id
                    and d.observation.evidence_id == step.evidence_id for d in decisions):
                unsupported.append(dict(case_id=result.case_id, step=step.step_no))
        all_observations = detail.get('observations', [])
        for o in all_observations:
            if o['category'] not in {'SUPPORT_MESSAGE', 'SUPPORT_ATTACHMENT'}:
                continue
            for field in FIELDS:
                if field not in o['facts']:
                    continue
                provenance_count += 1
                p = o['facts'].get('_support_fact_provenance', {}).get(field, {})
                witnesses = [w for w in all_observations
                             if w['evidence_id'] == p.get('evidence_id') and w['source_table'] == p.get('source')
                             and w['system_id'] == o['system_id'] and w['resource_id'] == o['resource_id']
                             and w['copy_id'] == o['copy_id'] and w['observed_at'] == p.get('observed_at')]
                valid = (type(o['facts'][field]) is bool and p.get('value') is o['facts'][field]
                         and bool(p.get('basis')) and bool(witnesses)
                         and p.get('evidence_id') in inputs.citation_times()
                         and timestamp(p['observed_at']) <= timestamp(o['observed_at']) <= request.audit_at
                         and timestamp(p['available_at']) <= request.audit_at)
                if not valid:
                    failures.append(dict(case_id=result.case_id, evidence_id=o['evidence_id'], field=field))
    return dict(rows=len(rows), exact_case_coverage=True, unsupported_findings=unsupported,
                support_facts_checked=provenance_count, provenance_failures=failures)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]; p = args.directory
    before = load(p/'before-public/predictions.csv'); after = load(p/'after-public/predictions.csv')
    labels = load(root/'dataset/sample_output.csv')
    base = load(p/'baseline-518.csv'); candidate = load(p/'candidate-518.csv')
    changed = [cid for cid in sorted(base) if base[cid] != candidate[cid]]
    changes = {}
    for cid in changed:
        old, new = content(base[cid]['steps']), content(candidate[cid]['steps'])
        changes[cid] = dict(before_status=base[cid]['status'], after_status=candidate[cid]['status'],
                            added=[json.loads(s) for s in (new-old).elements()],
                            removed=[json.loads(s) for s in (old-new).elements()])
    report = dict(before=metrics(before, labels), after=metrics(after, labels),
                  public_changed_cases=[cid for cid in before if before[cid] != after[cid]],
                  public_integrity=integrity(p/'after-public/predictions.csv', p/'public-details.json',
                      load_inputs(root/'dataset', root/'dataset/sample_deletion_requests.csv')),
                  full_integrity=integrity(p/'candidate-518.csv', p/'candidate-518.json',
                      load_inputs(root/'dataset', root/'dataset/deletion_requests.csv')),
                  full_changed_cases=changed, full_changes=changes)
    (p/'comparison.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'full_changes'}, indent=2))
    assert not report['full_integrity']['unsupported_findings']
    assert not report['full_integrity']['provenance_failures']
    assert not report['public_integrity']['unsupported_findings']
    assert not report['public_integrity']['provenance_failures']


if __name__ == '__main__':
    main()
