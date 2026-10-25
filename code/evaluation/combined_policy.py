"""Reproduce independent policy-fact experiments from a preserved prediction run.

Both proposed CSV relaxations are disallowed by the supplied contract. Each
track therefore adds only a separate fact ledger. Candidate CSVs are independently
serialized/validated baseline results, not altered to fit public references.
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit.contract import read_output, validate_result
from audit.inputs import load_inputs
from audit.models import Observation, AuditError, timestamp
from audit.prediction import write_predictions
from evaluation.accuracy_changes import content, integrity, load, metrics
from evaluation.policy_tracks import tracks


def hydrate(row):
    row = dict(row)
    for key in ('observed_at', 'available_at', 'updated_at'):
        row[key] = timestamp(row[key]) if row[key] else None
    return Observation(**row)


def summarize(ledgers):
    counts = Counter()
    for case in ledgers.values():
        for name, rows in case.items():
            for row in rows:
                counts[name + '_copies'] += 1
                if not row['admissible']:
                    counts[name + '_inadmissible'] += 1
                    continue
                counts[name + '_policy_established' if row['policy']['established'] else name + '_policy_unresolved'] += 1
                if row['observed_facts'].get('identifier_exposure', {}).get('value') is True:
                    counts[name + '_positive_exposure'] += 1
                if row['observed_facts'].get('present', {}).get('value') is True:
                    counts[name + '_present'] += 1
    return dict(counts)


def run_variants(directory, split, inputs):
    baseline_path = directory / f'baseline-{split}.csv'
    diagnostic_path = directory / f'baseline-{split}.json'
    details = json.loads(diagnostic_path.read_text())['cases']
    results = read_output(baseline_path)
    baseline_integrity = integrity(baseline_path, diagnostic_path, inputs)
    assert not baseline_integrity['unsupported_findings'], 'Unsupported baseline findings'
    assert not baseline_integrity['provenance_failures'], 'Invalid baseline fact provenance'
    validators = {}
    for r in results:
        request = next(q for q in inputs.requests if q.case_id == r.case_id)
        try:
            validate_result(r, request, inputs.citation_times())
        except AuditError as exc:
            validators[r.case_id] = str(exc)
    reports = {}
    track_cases = {}
    saved_details = json.dumps(details, sort_keys=True)
    for variant, enabled in [('track-a', ['security']), ('track-b', ['support']), ('combined', ['security', 'support'])]:
        ledgers = {}
        for request in inputs.requests:
            observations = tuple(hydrate(o) for o in details[request.case_id].get('latest_copy_states', []))
            ledgers[request.case_id] = tracks(observations, inputs.rules, request.audit_at, enabled)
        output = directory / f'{variant}-{split}.csv'
        write_predictions(output, results, inputs.requests, inputs.citation_times())
        report = dict(enabled_tracks=enabled, observation_summary=summarize(ledgers),
                      csv_changed_cases=[], csv_policy_relaxations_accepted=False,
                      csv_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                      strong_audit_validator_failures=validators,
                      integrity=baseline_integrity, cases=ledgers)
        assert output.read_bytes() == baseline_path.read_bytes()
        assert json.dumps(details, sort_keys=True) == saved_details
        (directory / f'{variant}-{split}.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
        reports[variant] = {k:v for k,v in report.items() if k != 'cases'}
        track_cases[variant] = ledgers
    for request in inputs.requests:
        cid = request.case_id
        assert track_cases['combined'][cid] == {
            **track_cases['track-a'][cid], **track_cases['track-b'][cid]}
    return dict(baseline=dict(strong_audit_validator_failures=validators, integrity=baseline_integrity), **reports)


def investigate_gaps(directory, dataset, inputs):
    # Evaluation-only targets. Raw token matches are discovery locations,
    # not proof of record state, ownership, policy, or emission instructions.
    predictions, labels = load(directory / 'baseline-public.csv'), load(dataset / 'sample_output.csv')
    details = json.loads((directory / 'baseline-public.json').read_text())['cases']
    texts = {}
    for f in inputs.evidence:
        if f.path.suffix in {'.sql', '.json', '.txt', '.log'}:
            texts[f.file_id] = f.path.read_text(encoding='utf-8')
        elif f.path.suffix == '.pdf':
            from audit.pdf_evidence import read_pdf
            texts[f.file_id] = '\n'.join(read_pdf(f).pages)
        elif f.path.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
            from audit.reviewed_images import review
            texts[f.file_id] = json.dumps(review(f) or {})
    inventory = dict(security=[], support=[])
    for request in inputs.requests:
        missing = content(labels[request.case_id]['steps']) - content(predictions[request.case_id]['steps'])
        for encoded, count in missing.items():
            step = json.loads(encoded)
            track = 'security' if step['system_id'] == 'security_service' else 'support' if step['system_id'] == 'support_platform' else None
            if track is None:
                continue
            resource = step['resource_id']
            observations = [o for o in details[request.case_id].get('latest_copy_states', [])
                            if o['system_id'] == step['system_id'] and o['resource_id'] == resource]
            pattern = re.compile(r'(?<![\w])'+re.escape(resource)+r'(?![\w])')
            raw_hits = [dict(evidence_id=f.file_id, available_at=f.captured_at.isoformat(),
                            available_by_audit=f.captured_at <= request.audit_at)
                        for f in inputs.evidence if pattern.search(texts.get(f.file_id, ''))]
            values = [{k:o['facts'][k] for k in ('retention_until', 'shared_context', 'belongs_only_to_subject',
                        'text_scan_complete', 'text_has_subject_identifiers', 'identifier_exposure') if k in o['facts']}
                      for o in observations]
            inventory[track].append(dict(case_id=request.case_id, audit_at=request.audit_at.isoformat(),
                missing_step=step, count=count, admissible_subject_linked_observations=len(observations),
                observed_policy_values=values, admissible_evidence_ids=sorted({o['evidence_id'] for o in observations}),
                raw_resource_token_locations=raw_hits))
    return inventory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]; dataset=root/'dataset'; p=args.directory
    public = load_inputs(dataset, dataset/'sample_deletion_requests.csv')
    full = load_inputs(dataset, dataset/'deletion_requests.csv')
    report = dict(public=run_variants(p, 'public', public), full=run_variants(p, 'full', full))
    # Candidate generation and validation finish before opening public labels.
    labels = load(dataset/'sample_output.csv')
    for variant in ('baseline', 'track-a', 'track-b', 'combined'):
        report['public'][variant]['metrics'] = metrics(load(p/f'{variant}-public.csv'), labels)
    report['gap_inventory'] = investigate_gaps(p, dataset, public)
    (p/'report.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps({split: {variant: {k:v for k,v in values.items()
        if k not in ('strong_audit_validator_failures',)} for variant,values in report[split].items()}
        for split in ('public', 'full')}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
