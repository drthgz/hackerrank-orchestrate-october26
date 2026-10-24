"""Run a deterministic evidence deletion audit; no public labels are read here."""
import argparse
import json
import sys
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
    parser = argparse.ArgumentParser(description='SQL/JSON/text/log audit; unsupported scopes fail explicitly. Not a full-dataset submission runner yet.')
    parser.add_argument('--dataset', default='dataset')
    parser.add_argument('--requests', required=True)
    parser.add_argument('--case-id', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--diagnostics')
    args = parser.parse_args()
    try:
        inputs = load_inputs(rooted(args.dataset), rooted(args.requests))
        requests = [r for r in inputs.requests if r.case_id == args.case_id]
        if len(requests) != 1:
            raise AuditError('Selected case not found')
        output = rooted(args.output).resolve()
        if output == ROOT / 'output.csv' or output.is_relative_to(rooted(args.dataset).resolve()):
            raise AuditError('Slice outputs must be outside dataset and must not replace final root output.csv')
        diagnostic = rooted(args.diagnostics).resolve() if args.diagnostics else None
        if diagnostic and (diagnostic == output or diagnostic == ROOT / 'output.csv' or diagnostic.is_relative_to(rooted(args.dataset).resolve())):
            raise AuditError('Diagnostics must not overwrite input or prediction files')
        result, details = audit(requests[0], inputs)
        write_output(output, [result], requests, inputs.citation_times())
        if diagnostic:
            diagnostic.parent.mkdir(parents=True, exist_ok=True)
            diagnostic.write_text(json.dumps(details, default=json_value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print(f'Validated 1 selected row: {result.deletion_status}; {len(result.steps)} steps. PDF/image evidence remains outside interpretation.')
        return 0
    except (AuditError, OSError, ValueError) as exc:
        print(f'Audit failed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
