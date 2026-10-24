"""Run a deterministic evidence deletion audit; no public labels are read here."""
import argparse
import json
import sys
import time
import hashlib
from collections import Counter
from datetime import datetime
from pathlib import Path

from audit.contract import write_output
from audit.inputs import load_inputs
from audit.models import AuditError
from audit.pipeline import audit

ROOT = Path(__file__).resolve().parents[1]


def rooted(value):
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def json_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    raise TypeError(type(value).__name__)


def main():
    parser = argparse.ArgumentParser(description='Evidence-grounded deletion audit; strict or best-effort plans.')
    parser.add_argument('--dataset', default='dataset')
    parser.add_argument('--requests', default='dataset/deletion_requests.csv')
    parser.add_argument('--case-id')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--mode', choices=['strict', 'best-effort'], default='strict')
    parser.add_argument('--output', default='output.csv')
    parser.add_argument('--diagnostics', default='artifacts/run.json')
    args = parser.parse_args()
    try:
        inputs = load_inputs(rooted(args.dataset), rooted(args.requests))
        if args.all == bool(args.case_id):
            raise AuditError('Choose exactly one of --all or --case-id')
        requests = list(inputs.requests) if args.all else [r for r in inputs.requests if r.case_id == args.case_id]
        if not requests:
            raise AuditError('Selected case not found')
        output = rooted(args.output).resolve()
        if output.is_relative_to(rooted(args.dataset).resolve()):
            raise AuditError('Output must not overwrite dataset inputs')
        if not args.all and output == ROOT / 'output.csv':
            raise AuditError('Partial outputs must not replace final root output.csv')
        diagnostic = rooted(args.diagnostics).resolve()
        if diagnostic == output or diagnostic == ROOT / 'output.csv' or diagnostic.is_relative_to(rooted(args.dataset).resolve()):
            raise AuditError('Diagnostics must not overwrite inputs or predictions')
        started = time.perf_counter()
        results, details, unsupported = [], {}, {}
        for request in requests:
            try:
                result, detail = audit(request, inputs, mode=args.mode)
                results.append(result)
                details[request.case_id] = detail
            except AuditError as exc:
                unsupported[request.case_id] = str(exc)
        summary = dict(mode=args.mode, attempted=len(requests), produced=len(results), unsupported=unsupported,
                       statuses=dict(Counter(r.deletion_status for r in results)),
                       model_providers=[], model_names=[], model_calls=0, input_tokens=0, output_tokens=0,
                       total_tokens=0, average_tokens_per_request=0, estimated_total_cost_usd=0,
                       estimated_cost_per_request_usd=0, elapsed_seconds=time.perf_counter()-started)
        if not unsupported:
            temporary = output.with_name(output.name + '.tmp')
            write_output(temporary, results, requests, inputs.citation_times())
            temporary.replace(output)
            summary['output_sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
        else:
            partial = ROOT / 'artifacts' / 'supported.csv'
            selected = [r for r in requests if r.case_id not in unsupported]
            write_output(partial, results, selected, inputs.citation_times())
            summary['partial_output'] = str(partial)
        diagnostic.parent.mkdir(parents=True, exist_ok=True)
        diagnostic.write_text(json.dumps(dict(summary=summary, cases=details), default=json_value,
                                         indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print(json.dumps(summary, indent=2, sort_keys=True))
        if unsupported:
            return 2
        return 0
    except (AuditError, OSError, ValueError) as exc:
        print(f'Audit failed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
