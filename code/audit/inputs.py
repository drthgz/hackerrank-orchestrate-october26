import csv
from dataclasses import dataclass
from pathlib import Path

from .models import AuditError, EvidenceFile, Request, timestamp

SCHEMAS = {
    'requests': 'case_id,email,requested_at,reported_status,reported_at,audit_at,request_text',
    'user_identities': 'user_id,name,email,phone,email_hash,updated_at',
    'user_audit_log': 'audit_id,user_id,event_time,field_name,old_value,new_value',
    'system_activity': 'activity_id,event_time,event_type,source_system,target_system,resource_id,reported_result,details',
    'deletion_rules': 'rule_id,data_category,condition,required_action',
    'evidence_files': 'file_id,file_path,origin,captured_at',
}


def read_csv(path: Path, schema: str) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != schema.split(','):
            raise AuditError(f'{path.name}: unexpected CSV header')
        rows = list(reader)
    key = schema.split(',')[0]
    seen = set()
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise AuditError(f'{path.name}: malformed CSV row')
        if not row[key] or row[key] in seen:
            raise AuditError(f'{path.name}: empty or duplicate {key}')
        seen.add(row[key])
    return rows


@dataclass(frozen=True)
class Inputs:
    requests: tuple[Request, ...]
    identities: list[dict[str, str]]
    history: list[dict[str, str]]
    activity: list[dict[str, str]]
    rules: list[dict[str, str]]
    evidence: tuple[EvidenceFile, ...]

    def citation_times(self):
        return {
            **{e.file_id: e.captured_at for e in self.evidence},
            **{x['audit_id']: timestamp(x['event_time']) for x in self.history},
            **{x['activity_id']: timestamp(x['event_time']) for x in self.activity},
        }


def load_inputs(dataset: Path, requests_path: Path) -> Inputs:
    dataset = dataset.resolve()
    rows = read_csv(requests_path, SCHEMAS['requests'])
    loaded = {name: read_csv(dataset / f'{name}.csv', schema)
              for name, schema in SCHEMAS.items() if name != 'requests'}
    requests = []
    for row in rows:
        item = Request(**{k: timestamp(v) if k.endswith('_at') else v for k, v in row.items()})
        if item.reported_status not in {'COMPLETE', 'PARTIALLY_COMPLETE', 'NOT_STARTED'}:
            raise AuditError('Invalid reported status')
        if item.requested_at > item.audit_at or not item.email or not item.request_text:
            raise AuditError('Invalid request timing or missing intent/identity')
        requests.append(item)
    ids = {x['user_id'] for x in loaded['user_identities']}
    for row in loaded['user_identities']:
        timestamp(row['updated_at'])
    for row in loaded['user_audit_log']:
        timestamp(row['event_time'])
        if row['user_id'] not in ids or row['field_name'] not in {'name', 'email', 'phone', 'email_hash'}:
            raise AuditError('Invalid identity audit reference or field')
    for row in loaded['system_activity']:
        timestamp(row['event_time'])
    for row in loaded['deletion_rules']:
        if row['required_action'] not in {'DELETE', 'REDACT', 'ANONYMIZE', 'RETAIN'}:
            raise AuditError('Invalid policy action')
    evidence = []
    for row in loaded['evidence_files']:
        path = (dataset / row['file_path']).resolve()
        if not path.is_relative_to(dataset / 'evidence') or not path.is_file():
            raise AuditError('Evidence path missing or outside dataset/evidence')
        evidence.append(EvidenceFile(row['file_id'], path, row['origin'], timestamp(row['captured_at'])))
    return Inputs(tuple(requests), loaded['user_identities'], loaded['user_audit_log'],
                  loaded['system_activity'], loaded['deletion_rules'], tuple(evidence))
