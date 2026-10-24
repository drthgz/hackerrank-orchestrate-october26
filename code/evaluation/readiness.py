"""Label-free full-dataset readiness audit; never fabricates or writes output.csv."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit.inputs import load_inputs
from audit.pipeline import audit
from audit.models import AuditError

ROOT = Path(__file__).resolve().parents[2]


def assess(dataset):
    inputs = load_inputs(dataset, dataset / 'deletion_requests.csv')
    supported, unsupported = {}, {}
    for request in inputs.requests:
        try:
            result, _ = audit(request, inputs)
            supported[request.case_id] = result.deletion_status
        except AuditError as exc:
            unsupported[request.case_id] = str(exc)
    return dict(requests=len(inputs.requests), supported=len(supported),
                supported_statuses=dict(Counter(supported.values())),
                unsupported_count=len(unsupported), unsupported=unsupported,
                blockers=dict(Counter(unsupported.values())),
                can_produce_complete_output=not unsupported,
                model_calls=0, input_tokens=0, output_tokens=0, inference_cost_usd=0)


if __name__ == '__main__':
    print(json.dumps(assess(ROOT / 'dataset'), indent=2, sort_keys=True))
