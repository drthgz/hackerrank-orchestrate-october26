"""Independent public-label comparison; prediction never imports this module."""
import argparse
import csv
import json
import sys
import hashlib
import time
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
    cited = lambda steps: {(s['phase'], s['operation'], s['system_id'], s['resource_id']): s['evidence_id']
                           for s in steps if s['evidence_id']}
    actual_cited, expected_cited = cited(actual), cited(expected['steps'])
    return {
        'cited_step_matches': sum(expected_cited.get(key) == value for key, value in actual_cited.items()),
        'cited_step_comparisons': max(len(actual_cited), len(expected_cited)),
        'deletion_status_matches': prediction.deletion_status == expected['status'],
        'all_steps_match': left == right,
        'evidence_references_match': [s['evidence_id'] for s in actual] == [s['evidence_id'] for s in expected['steps']],
        'step_ordering_matches': actual == expected['steps'],
        'citation_field_matches': sum(a['evidence_id'] == b['evidence_id'] for a, b in zip(actual, expected['steps'])),
        'citation_field_comparisons': max(len(actual), len(expected['steps'])),
        'step_matches': matched,
        'expected_steps': len(expected['steps']),
        'predicted_steps': len(actual),
        'field_matches': fields,
        'field_comparisons': denom,
    }


def evaluate_all(inputs, labels_path, output_dir, mode='strict'):
    """Predict every request before opening labels; unsupported stays explicit."""
    from audit.pipeline import audit, classify_intent
    from audit.contract import write_output
    output_dir.mkdir(parents=True, exist_ok=True)
    results, unsupported, reproducible = [], {}, True
    prediction_details, audit_validator_failures = {}, {}
    runner, validator, writer = audit, validate_result, write_output
    if mode == 'prediction':
        from audit.prediction import predict, validate_prediction, write_predictions
        runner = lambda request, inputs, mode: predict(request, inputs)
        validator, writer = validate_prediction, write_predictions
    intent_counts, intent_unsupported = Counter(), {}
    started = time.perf_counter()
    for request in inputs.requests:
        try:
            intent_counts[classify_intent(request.request_text)] += 1
        except AuditError as exc:
            intent_unsupported[request.case_id] = str(exc)
        try:
            result, detail = runner(request, inputs, mode=mode)
            repeated, _ = runner(request, inputs, mode=mode)
            reproducible = reproducible and result == repeated
            validator(result, request, inputs.citation_times())
            if mode == 'prediction':
                prediction_details[request.case_id] = detail['prediction']
                try:
                    validate_result(result, request, inputs.citation_times())
                except AuditError as exc:
                    audit_validator_failures[request.case_id] = str(exc)
            results.append(result)
        except AuditError as exc:
            unsupported[request.case_id] = str(exc)
    elapsed = time.perf_counter() - started
    selected = [r for r in inputs.requests if r.case_id not in unsupported]
    prediction_path = output_dir / 'predictions.csv'
    writer(prediction_path, results, selected, inputs.citation_times())
    # This is the sole label access; it is outside prediction and occurs after
    # all selected requests have been attempted independently.
    with labels_path.open(encoding='utf-8', newline='') as source:
        labels = {row['case_id']: row for row in csv.DictReader(source)}
    comparisons = {}
    for result in results:
        label = labels[result.case_id]
        comparisons[result.case_id] = compare(result, {'status': label['deletion_status'], 'steps': json.loads(label['steps_json'])})
    n = len(results)
    steps_matched = sum(v['step_matches'] for v in comparisons.values())
    predicted_steps = sum(v['predicted_steps'] for v in comparisons.values())
    expected_steps = sum(v['expected_steps'] for v in comparisons.values())
    fields_matched = sum(v['field_matches'] for v in comparisons.values())
    fields_total = sum(v['field_comparisons'] for v in comparisons.values())
    # An explicit benchmark baseline belongs to evaluation only.
    requested_ids = {r.case_id for r in inputs.requests}
    regressions = [cid for cid in ['case_05'] if cid in requested_ids and (cid not in comparisons or not
                   (comparisons[cid]['deletion_status_matches'] and comparisons[cid]['step_ordering_matches']))]
    ratio = lambda a, b: a / b if b else None
    status_count = sum(v['deletion_status_matches'] for v in comparisons.values())
    exact_count = sum(v['deletion_status_matches'] and v['step_ordering_matches'] for v in comparisons.values())
    citation_count = sum(v['evidence_references_match'] for v in comparisons.values())
    sequence_count = sum(v['step_ordering_matches'] for v in comparisons.values())
    citation_fields = sum(v['citation_field_matches'] for v in comparisons.values())
    citation_total = sum(v['citation_field_comparisons'] for v in comparisons.values())
    all_expected_steps = sum(len(json.loads(labels[r.case_id]['steps_json'])) for r in inputs.requests)
    all_expected_citations = sum(bool(s['evidence_id']) for r in inputs.requests
                                 for s in json.loads(labels[r.case_id]['steps_json']))
    cited_matches = sum(v['cited_step_matches'] for v in comparisons.values())
    cited_total = sum(v['cited_step_comparisons'] for v in comparisons.values())
    def blocker_category(reason):
        if 'retention' in reason.lower():
            return 'retention_facts'
        if 'profile-absence' in reason:
            return 'profile_absence_lineage'
        if 'unprocessed evidence scope' in reason:
            return 'unparsed_media_scope'
        if 'Subject-linked activity' in reason:
            return 'unresolved_activity_resource'
        if 'resource lineage' in reason:
            return 'missing_subject_linked_evidence'
        if 'Support text' in reason or 'shared_context' in reason or 'text_scan_complete' in reason:
            return 'support_context_or_full_text'
        return 'other'
    report = {
        'mode': mode,
        'valid_output_coverage': ratio(n, len(inputs.requests)),
        'status_accuracy_all_samples': ratio(status_count, len(inputs.requests)),
        'sequence_accuracy_all_samples': ratio(sequence_count, len(inputs.requests)),
        'step_recall_all_samples': ratio(steps_matched, all_expected_steps),
        'expected_steps_all_samples': all_expected_steps,
        'cited_step_matches': cited_matches, 'cited_step_comparisons': cited_total,
        'cited_step_accuracy_processed': ratio(cited_matches, cited_total),
        'cited_step_accuracy_all_samples': ratio(cited_matches, all_expected_citations),
        'blockers_by_category': dict(Counter(blocker_category(reason) for reason in unsupported.values())),
        'intent_classified': sum(intent_counts.values()),
        'intent_counts': dict(intent_counts), 'intent_unsupported': intent_unsupported,
        'processed': n, 'total_public_samples': len(inputs.requests), 'unsupported': unsupported,
        'all_processed_structurally_valid': True,
        'status_matches': status_count, 'status_accuracy_processed': ratio(status_count, n),
        'exact_case_matches': exact_count, 'exact_case_accuracy_processed': ratio(exact_count, n),
        'exact_case_yield_all_samples': ratio(exact_count, len(inputs.requests)),
        'step_matches': steps_matched, 'predicted_steps': predicted_steps, 'expected_steps_processed': expected_steps,
        'step_precision': ratio(steps_matched, predicted_steps), 'step_recall': ratio(steps_matched, expected_steps),
        'step_f1': ratio(2 * steps_matched, predicted_steps + expected_steps),
        'field_matches': fields_matched, 'field_comparisons': fields_total, 'field_accuracy': ratio(fields_matched, fields_total),
        'citation_field_matches': citation_fields, 'citation_field_comparisons': citation_total,
        'citation_field_accuracy': ratio(citation_fields, citation_total),
        'citation_sequence_matches': citation_count, 'citation_sequence_accuracy': ratio(citation_count, n),
        'sequence_matches': sequence_count, 'sequence_accuracy': ratio(sequence_count, n),
        'regressions': regressions, 'regression_count': len(regressions), 'reproducible_results': reproducible,
        'elapsed_seconds_including_repeat': elapsed,
        'prediction_sha256': hashlib.sha256(prediction_path.read_bytes()).hexdigest(),
        'comparisons': comparisons,
    }
    if mode == 'prediction':
        report.update(prediction_details=prediction_details,
                      uncertain_status_predictions=sorted(cid for cid, d in prediction_details.items() if d['status_uncertain']),
                      audit_validator_failures=audit_validator_failures,
                      incomplete_or_unproved_plans=sorted(cid for cid, d in prediction_details.items() if not d['plan_complete']),
                      semantic_compliance_certified=False, organizer_approved=False)
    (output_dir / 'benchmark.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--all-samples', action='store_true')
    parser.add_argument('--mode', choices=['strict', 'best-effort', 'prediction'], default='strict')
    parser.add_argument('--output-dir', default='artifacts/structured-benchmark')
    parser.add_argument('--prediction')
    parser.add_argument('--repeat', help='Separately generated output to compare byte-for-byte')
    parser.add_argument('--case-id')
    parser.add_argument('--labels', default='dataset/sample_output.csv')
    parser.add_argument('--requests', default='dataset/sample_deletion_requests.csv')
    parser.add_argument('--dataset', default='dataset')
    args = parser.parse_args()
    try:
        inputs = load_inputs(rooted(args.dataset), rooted(args.requests))
        if args.all_samples:
            output_dir = rooted(args.output_dir).resolve()
            if output_dir.is_relative_to(rooted(args.dataset).resolve()):
                raise AuditError('Benchmark outputs cannot overwrite dataset inputs')
            report = evaluate_all(inputs, rooted(args.labels), output_dir, args.mode)
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0 if not report['regressions'] and report['reproducible_results'] else 1
        if not (args.prediction and args.repeat and args.case_id):
            raise AuditError('Use --all-samples or supply --prediction, --repeat and --case-id')
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
