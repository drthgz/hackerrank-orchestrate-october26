import csv
import json
from dataclasses import asdict, replace
from pathlib import Path

from .models import AuditError, Result, Step

OUTPUT_HEADER = ['case_id', 'deletion_status', 'steps_json']
STEP_FIELDS = set(Step.__dataclass_fields__)
OP_GROUPS = {
    'FINDING': [('REPORT_REMAINING_RECORD', 'PRESENT'), ('REPORT_EXPOSED_PII', 'PRESENT'),
                ('REPORT_ACTIVE_DATA_FLOW', 'ACTIVE'), ('REPORT_RESTORE_RISK', 'ACTIVE')],
    'REMEDIATION': [('DISABLE_DATA_FLOW', 'DISABLED'), ('BLOCK_RESTORE', 'BLOCKED'),
                    ('DELETE_RECORD', 'ABSENT'), ('REDACT_RECORD', 'REDACTED'), ('ANONYMIZE_RECORD', 'ANONYMIZED')],
    'VERIFICATION': [('VERIFY_RECORD_ABSENT', 'ABSENT'), ('VERIFY_RECORD_PRESENT', 'PRESENT'),
                     ('VERIFY_RECORD_REDACTED', 'REDACTED'), ('VERIFY_RECORD_ANONYMIZED', 'ANONYMIZED'),
                     ('VERIFY_DATA_FLOW_DISABLED', 'DISABLED'), ('VERIFY_RESTORE_BLOCKED', 'BLOCKED')],
}
ORDER = {op: (phase_no, op_no, phase, state)
         for phase_no, (phase, operations) in enumerate(OP_GROUPS.items())
         for op_no, (op, state) in enumerate(operations)}


def sort_key(step):
    return (*ORDER[step.operation][:2], step.system_id, step.resource_id)


def order_steps(steps):
    return tuple(replace(step, step_no=i) for i, step in enumerate(sorted(steps, key=sort_key), 1))


def validate_result(result: Result, request, citation_times):
    if result.case_id != request.case_id:
        raise AuditError('Case ID mismatch')
    if result.deletion_status not in {'COMPLETE', 'INCOMPLETE', 'NOT_APPLICABLE'}:
        raise AuditError('Invalid deletion status')
    if result.deletion_status == 'NOT_APPLICABLE':
        if result.steps:
            raise AuditError('Non-deletion requests must have no steps')
        return
    if not result.steps:
        raise AuditError('Authorized deletion requires evidence-backed steps')
    seen = set()
    for i, step in enumerate(result.steps, 1):
        values = asdict(step)
        if type(step.step_no) is not int or step.step_no != i:
            raise AuditError('Nonconsecutive or noninteger step number')
        if any(not isinstance(v, str) for k, v in values.items() if k != 'step_no'):
            raise AuditError('Step fields must be strings')
        spec = ORDER.get(step.operation)
        if spec is None or (step.phase, step.state) != spec[2:]:
            raise AuditError('Invalid phase/operation/state combination')
        if not step.system_id or not step.resource_id:
            raise AuditError('Empty resource or system')
        key = (step.phase, step.operation, step.system_id, step.resource_id)
        if key in seen:
            raise AuditError('Duplicate step')
        seen.add(key)
        if result.deletion_status == 'COMPLETE' and step.phase != 'VERIFICATION':
            raise AuditError('Complete cases only allow verification')
        needs_citation = step.phase == 'FINDING' or result.deletion_status == 'COMPLETE'
        if needs_citation:
            if step.evidence_id not in citation_times or citation_times[step.evidence_id] > request.audit_at:
                raise AuditError('Missing, invalid or future evidence citation')
        elif step.evidence_id != '':
            raise AuditError('Future work must use empty evidence_id')
    if tuple(result.steps) != order_steps(result.steps):
        raise AuditError('Steps are not in official canonical order')
    if result.deletion_status == 'INCOMPLETE':
        if {s.phase for s in result.steps} != set(OP_GROUPS):
            raise AuditError('Incomplete case requires all three phases')
        pairs = {'DELETE_RECORD': 'VERIFY_RECORD_ABSENT', 'REDACT_RECORD': 'VERIFY_RECORD_REDACTED',
                 'ANONYMIZE_RECORD': 'VERIFY_RECORD_ANONYMIZED', 'DISABLE_DATA_FLOW': 'VERIFY_DATA_FLOW_DISABLED',
                 'BLOCK_RESTORE': 'VERIFY_RESTORE_BLOCKED'}
        remedies = {'REPORT_REMAINING_RECORD': {'DELETE_RECORD'},
                    'REPORT_EXPOSED_PII': {'REDACT_RECORD', 'ANONYMIZE_RECORD'},
                    'REPORT_ACTIVE_DATA_FLOW': {'DISABLE_DATA_FLOW'},
                    'REPORT_RESTORE_RISK': {'BLOCK_RESTORE'}}
        for finding in (s for s in result.steps if s.phase == 'FINDING'):
            if not any(('REMEDIATION', op, finding.system_id, finding.resource_id) in seen
                       for op in remedies[finding.operation]):
                raise AuditError('Finding has no compatible remediation')
        for remedy in (s for s in result.steps if s.phase == 'REMEDIATION'):
            if not any(s.phase == 'FINDING' and s.system_id == remedy.system_id
                       and s.resource_id == remedy.resource_id and remedy.operation in remedies[s.operation]
                       for s in result.steps):
                raise AuditError('Remediation has no compatible finding')
        for step in result.steps:
            if step.phase == 'REMEDIATION' and ('VERIFICATION', pairs[step.operation], step.system_id, step.resource_id) not in seen:
                raise AuditError('Missing post-remediation verification')


def write_output(path: Path, results, requests, citation_times):
    expected = {r.case_id: r for r in requests}
    results = sorted(results, key=lambda x: x.case_id)
    if len(results) != len(expected) or {r.case_id for r in results} != set(expected):
        raise AuditError('Output coverage differs from selected request set')
    for result in results:
        validate_result(result, expected[result.case_id], citation_times)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as target:
        writer = csv.writer(target, lineterminator='\n')
        writer.writerow(OUTPUT_HEADER)
        for result in results:
            writer.writerow([result.case_id, result.deletion_status,
                             json.dumps([asdict(s) for s in result.steps], separators=(',', ':'), ensure_ascii=False)])


def read_output(path: Path):
    results = []
    with path.open(encoding='utf-8', newline='') as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != OUTPUT_HEADER:
            raise AuditError('Invalid output header')
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise AuditError('Malformed output row')
            def unique_object(pairs):
                obj = dict(pairs)
                if len(obj) != len(pairs):
                    raise AuditError('Duplicate JSON object key')
                return obj
            steps = json.loads(row['steps_json'], object_pairs_hook=unique_object)
            if not isinstance(steps, list) or any(not isinstance(s, dict) or set(s) != STEP_FIELDS for s in steps):
                raise AuditError('Invalid step field set')
            results.append(Result(row['case_id'], row['deletion_status'], tuple(Step(**s) for s in steps)))
    ids = [r.case_id for r in results]
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise AuditError('Duplicate or unsorted output IDs')
    return results
