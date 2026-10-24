"""Validate prediction artifacts, reporting structural validity apart from proof."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit.contract import read_output, validate_result
from audit.inputs import load_inputs
from audit.models import AuditError
from audit.prediction import validate_prediction

ROOT = Path(__file__).resolve().parents[2]


def validate(output, diagnostics, baseline=None):
    inputs = load_inputs(ROOT / 'dataset', ROOT / 'dataset/deletion_requests.csv')
    requests = {r.case_id: r for r in inputs.requests}
    rows = read_output(output)
    sidecar = json.loads(diagnostics.read_text())
    assert len(rows) == len(requests) == 518
    assert {r.case_id for r in rows} == set(requests) == set(sidecar['cases'])
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    assert sidecar['summary']['output_sha256'] == digest
    failures = {}
    for row in rows:
        validate_prediction(row, requests[row.case_id], inputs.citation_times())
        detail = sidecar['cases'][row.case_id]
        assert detail['prediction']['verified_compliance_decision'] is False
        observed = {(o['system_id'], o['resource_id']) for o in detail.get('observations', [])}
        for step in row.steps:
            assert (step.system_id, step.resource_id) in observed, 'Step resource lacks subject-linked observation'
            if step.evidence_id:
                assert any(o['system_id'] == step.system_id and o['resource_id'] == step.resource_id
                           and o['evidence_id'] == step.evidence_id for o in detail['observations'])
        try:
            validate_result(row, requests[row.case_id], inputs.citation_times())
        except AuditError as exc:
            failures[row.case_id] = str(exc)
    assert failures == sidecar['summary']['audit_validator_failures']
    preserved = None
    if baseline:
        current = {r.case_id: r for r in rows}
        old = read_output(baseline)
        assert all(current[r.case_id] == r for r in old)
        preserved = len(old)
    return dict(rows=len(rows), exact_request_ids=True, unique_sorted_ids=True,
                structural_invalid=0, citation_or_resource_provenance_invalid=0,
                uncertain_statuses=len(sidecar['summary']['uncertain_status_predictions']),
                incomplete_or_unproved_plans=len(sidecar['summary']['incomplete_or_unproved_plans']),
                audit_validator_failures=failures, preserved_baseline_rows=preserved,
                output_sha256=digest, semantic_compliance_certified=False, organizer_approved=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'output.csv')
    parser.add_argument('--diagnostics', type=Path, default=ROOT / 'artifacts/prediction-run.json')
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    report = validate(args.output, args.diagnostics, args.baseline)
    (ROOT / 'artifacts/candidate-validation.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'audit_validator_failures'}, indent=2))
