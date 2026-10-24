"""Offline preflight only. Labels are opened after all predictions finish."""
import csv
import hashlib
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'code'))
from audit.inputs import load_inputs
from audit.pipeline import audit
from audit.models import AuditError
from evaluation.main import compare

CASES = ('case_01', 'case_02', 'case_21', 'case_05', 'case_03', 'case_11', 'case_18', 'case_29')


def run():
    inputs = load_inputs(ROOT / 'dataset', ROOT / 'dataset/sample_deletion_requests.csv')
    predictions, failures, elapsed = {}, {}, {}
    for request in inputs.requests:
        if request.case_id not in CASES:
            continue
        started = time.perf_counter()
        try:
            predictions[request.case_id] = audit(request, inputs, mode='best-effort')[0]
        except AuditError as exc:
            failures[request.case_id] = str(exc)
        elapsed[request.case_id] = time.perf_counter() - started
    # Evaluation boundary: no labels are passed to audit or any runtime prompt.
    with (ROOT / 'dataset/sample_output.csv').open() as f:
        labels = {r['case_id']: r for r in csv.DictReader(f)}
    rows = {}
    for cid in CASES:
        expected = json.loads(labels[cid]['steps_json'])
        prediction = predictions.get(cid)
        metrics = compare(prediction, {'status': labels[cid]['deletion_status'], 'steps': expected}) if prediction else {}
        actual = [asdict(s) for s in prediction.steps] if prediction else []
        key = lambda s: (s['system_id'], s['resource_id'], s['operation'], s['state'])
        observed = {key(s) for s in actual if s['phase'] == 'VERIFICATION'}
        rows[cid] = dict(metrics, unsupported=failures.get(cid), seconds=elapsed[cid],
                        expected_steps=len(expected), missing_verification=sum(
                            key(s) not in observed for s in expected if s['phase'] == 'VERIFICATION'))
    result = {'baseline_commit': '938035d', 'mode': 'best-effort', 'cases': rows,
              'runtime_api_calls': 0, 'runtime_api_cost_usd': 0,
              'B': 'NOT_RUN', 'C': 'NOT_RUN',
              'blockers': ['Runtime external API permission unverified', 'OPENAI_API_KEY absent'],
              'input_hashes': {name: hashlib.sha256((ROOT / 'dataset' / name).read_bytes()).hexdigest()
                               for name in ('sample_deletion_requests.csv', 'sample_output.csv')}}
    path = Path(__file__).with_name('baseline_results.json')
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    run()
