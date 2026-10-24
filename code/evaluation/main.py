"""Independent public-label comparison; prediction never imports this module."""
import argparse
import csv
import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit.contract import read_output, validate_result
from audit.inputs import load_inputs
from audit.models import AuditError

ROOT = Path(__file__).resolve().parents[2]


def rooted(value):
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def compare(prediction, expected):
    actual = [asdict(s) for s in prediction.steps]
    content = lambda steps: Counter(json.dumps({k: v for k, v in s.items() if k != 'step_no'}, sort_keys=True) for s in steps)
    left, right = content(actual), content(expected['steps'])
    matched = sum((left & right).values())
    denom = max(len(actual), len(expected['steps'])) * 7
    fields = sum(a.get(k) == b.get(k) for a, b in zip(actual, expected['steps']) for k in a)
    return {
        'deletion_status_matches': prediction.deletion_status == expected['status'],
        'all_steps_match': left == right,
        'evidence_references_match': [s['evidence_id'] for s in actual] == [s['evidence_id'] for s in expected['steps']],
        'step_ordering_matches': actual == expected['steps'],
        'step_matches': matched,
        'expected_steps': len(expected['steps']),
        'predicted_steps': len(actual),
        'field_matches': fields,
        'field_comparisons': denom,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prediction', required=True)
    parser.add_argument('--repeat', required=True, help='Separately generated output to compare byte-for-byte')
    parser.add_argument('--case-id', required=True)
    parser.add_argument('--labels', default='dataset/sample_output.csv')
    parser.add_argument('--requests', default='dataset/sample_deletion_requests.csv')
    parser.add_argument('--dataset', default='dataset')
    args = parser.parse_args()
    try:
        inputs = load_inputs(rooted(args.dataset), rooted(args.requests))
        request = next(r for r in inputs.requests if r.case_id == args.case_id)
        results = read_output(rooted(args.prediction))
        if len(results) != 1 or results[0].case_id != args.case_id:
            raise AuditError('Expected exactly the selected case')
        validate_result(results[0], request, inputs.citation_times())
        with rooted(args.labels).open(encoding='utf-8', newline='') as source:
            labels = [r for r in csv.DictReader(source) if r['case_id'] == args.case_id]
        if len(labels) != 1:
            raise AuditError('Expected exactly one public label')
        label = labels[0]
        report = {'structurally_valid': True, **compare(results[0], {
            'status': label['deletion_status'], 'steps': json.loads(label['steps_json'])}),
            'reproducible_bytes': rooted(args.prediction).read_bytes() == rooted(args.repeat).read_bytes()}
        report['exact_case_match'] = report['deletion_status_matches'] and report['step_ordering_matches']
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if all(report[k] for k in ['structurally_valid', 'exact_case_match', 'reproducible_bytes']) else 1
    except (AuditError, ValueError, OSError, StopIteration) as exc:
        print(json.dumps({'structurally_valid': False, 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
