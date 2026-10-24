"""Scoped account snapshots, with copies kept separate until policy planning."""
import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime

from .identity import matches, normalize
from .models import AuditError, EvidenceFile, Observation, timestamp

PROFILE_TABLES = {'customer_profiles_primary', 'customer_profiles_failover_replica'}
REQUIRED_COLUMNS = {'resource_id', 'user_id', 'full_name', 'email', 'phone', 'account_status', 'updated_at'}


# Explicit schema adapters, never resource/case-number mappings.
TABLES = {
    'customer_profiles_primary': ('account_service', 'USER_PROFILE', REQUIRED_COLUMNS),
    'customer_profiles_failover_replica': ('account_service', 'USER_PROFILE', REQUIRED_COLUMNS),
    'customer_profiles': ('account_service', 'USER_PROFILE', {'resource_id', 'customer_reference', 'email', 'phone', 'email_hash', 'account_status', 'updated_at'}),
    'customer_search_documents': ('search_service', 'SEARCH_INDEX_ENTRY', {'resource_id', 'customer_reference', 'email', 'updated_at'}),
    'search_documents_primary': ('search_service', 'SEARCH_INDEX_ENTRY', {'resource_id', 'email', 'source_resource_id', 'indexed_at'}),
    'customer_exports': ('export_service', 'USER_EXPORT', {'resource_id', 'customer_reference', 'owner_email', 'updated_at'}),
    'customer_analytics_profiles': ('analytics_platform', 'ANALYTICS_PROFILE', {'resource_id', 'customer_reference', 'email', 'phone', 'email_hash', 'updated_at'}),
    'security_audit_records': ('security_service', 'SECURITY_AUDIT_LOG', {'resource_id', 'subject_reference', 'retention_until', 'updated_at'}),
    'backup_restore_entries': ('backup_service', 'BACKUP_ARCHIVE', {'resource_id', 'customer_reference', 'restore_allowed', 'updated_at'}),
    'connector_subscriptions': ('integration_service', 'DATA_FLOW', {'resource_id', 'customer_reference', 'enabled', 'updated_at'}),
    'support_records': ('support_platform', 'SUPPORT_MESSAGE', {'resource_id', 'customer_reference', 'message_excerpt', 'updated_at'}),
}
COLLECTIONS = {
    'customer_profiles': ('account_service', 'USER_PROFILE'),
    'customer_search_documents': ('search_service', 'SEARCH_INDEX_ENTRY'),
    'customer_export_jobs': ('export_service', 'USER_EXPORT'),
    'customer_analytics_reports': ('analytics_platform', 'ANALYTICS_PROFILE'),
    'security_audit_events': ('security_service', 'SECURITY_AUDIT_LOG'),
    'deleted_customer_references': ('identity_service', 'ACCOUNT_TOMBSTONE'),
    'backup_catalog': ('backup_service', 'BACKUP_ARCHIVE'),
    'connector_configurations': ('integration_service', 'DATA_FLOW'),
    'retained_order_records': ('legal_service', 'LEGAL_HOLD_RECORD'),
    'support_conversations': ('support_platform', 'SUPPORT_MESSAGE'),
    'ticket_attachments': ('support_platform', 'SUPPORT_ATTACHMENT'),
}
JSON_TABLES = {'customer_data_primary', 'customer_data_failover_replica', 'customer_data_read_replica',
               'customer_data_replica_ap_south', 'customer_data_replica_eu_west', 'customer_data_reporting_replica'}


@dataclass
class Snapshot:
    file: EvidenceFile
    table: str
    system: str
    category: str
    observed_at: datetime
    rows: list[dict]

    @property
    def copy_id(self):
        return self.file.origin + ':' + self.table


def read_sql(file):
    text = file.path.read_text(encoding='utf-8')
    header = re.search(r'^-- Captured at: (\S+)\s*$', text, re.MULTILINE)
    if header and timestamp(header[1]) != file.captured_at:
        raise AuditError(f'{file.file_id}: missing or conflicting SQL capture timestamp')
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    # Dumps are data, not trusted programs. No filesystem attachment, pragmas,
    # virtual tables, triggers, views, or user-defined functions are allowed.
    allowed = {sqlite3.SQLITE_CREATE_TABLE, sqlite3.SQLITE_INSERT,
               sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_READ, sqlite3.SQLITE_SELECT,
               sqlite3.SQLITE_TRANSACTION}

    def authorize(action, arg1, arg2, _database, _trigger):
        if action in {sqlite3.SQLITE_CREATE_INDEX, sqlite3.SQLITE_REINDEX}:
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_PRAGMA:
            return sqlite3.SQLITE_OK if arg1 == 'foreign_keys' and arg2 == 'ON' else sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_FUNCTION:
            return sqlite3.SQLITE_OK if arg2 == 'json_valid' else sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY

    db.set_authorizer(authorize)
    # Bound pathological scripts as well as limiting filesystem capabilities.
    budget = 0

    def progress():
        nonlocal budget
        budget += 1
        return budget > 10000

    db.set_progress_handler(progress, 1000)
    try:
        db.executescript(text)
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        result = {}
        for name in tables:
            quoted = '"' + name.replace('"', '""') + '"'
            cursor = db.execute('SELECT * FROM ' + quoted)
            columns = {x[0] for x in cursor.description}
            if name in TABLES and not TABLES[name][2] <= columns:
                raise AuditError(f'{file.file_id}: unsupported columns in {name}')
            if name in JSON_TABLES and not {'resource_id', 'origin_system', 'collection_name', 'record_json', 'updated_at'} <= columns:
                raise AuditError(f'{file.file_id}: invalid JSON SQL schema')
            result[name] = [dict(row) for row in cursor]
        return result
    except sqlite3.Error as exc:
        raise AuditError(f'{file.file_id}: invalid or unsafe SQL: {exc}') from exc
    finally:
        db.close()


def extract_observations(files, subject, cutoff):
    snapshots = []
    for file in sorted(files, key=lambda x: (x.captured_at, x.file_id)):
        if file.path.suffix != '.sql' or file.captured_at > cutoff:
            continue
        tables = read_sql(file)
        header = re.search(r'^-- Captured at: (\S+)', file.path.read_text(), re.MULTILINE)
        scope = {r['origin_system']: timestamp(r['captured_at']) for r in tables.get('snapshot_scope', [])}
        if any(t > file.captured_at for t in scope.values()):
            raise AuditError('Scope observation is later than file capture')
        for table, rows in tables.items():
            if table == 'snapshot_scope':
                continue
            groups = {}
            if table in TABLES:
                system, category, _ = TABLES[table]
                if system not in scope and not header:
                    if any(matches(row, subject) for row in rows):
                        raise AuditError('Subject-linked table has no declared snapshot scope')
                    continue
                groups[(system, category)] = rows
            elif table in JSON_TABLES:
                if not header:
                    raise AuditError('JSON SQL export lacks snapshot capture metadata')
                # A whole-table database snapshot includes empty collections;
                # resource lineage is still mandatory before inferring absence.
                groups = {pair: [] for pair in COLLECTIONS.values()}
                for row in rows:
                    payload = json.loads(row['record_json'])
                    if not isinstance(payload, dict) or payload.get('resource_id') != row['resource_id']:
                        raise AuditError('Invalid resource identity in SQL JSON')
                    pair = COLLECTIONS.get(row['collection_name'])
                    if pair is None:
                        if matches(payload, subject):
                            raise AuditError('Unsupported subject-linked SQL collection')
                        continue
                    if pair[0] != row['origin_system']:
                        raise AuditError('Conflicting collection/system mapping')
                    groups[pair].append({**payload, 'updated_at': row['updated_at']})
            else:
                if any(matches(row, subject) for row in rows):
                    raise AuditError(f'{file.file_id}: subject-linked SQL table unsupported: {table}')
            for (system, category), records in groups.items():
                observed = scope.get(system, file.captured_at)
                for row in records:
                    update = row.get('updated_at', row.get('indexed_at'))
                    if update is None or timestamp(update) > observed:
                        raise AuditError(f'{file.file_id}: row update is later than its snapshot or missing')
                snapshots.append(Snapshot(file, table, system, category, observed, records))
    # Association is established by real identifiers in any admissible snapshot.
    linked = {}
    for snapshot in snapshots:
        key = (snapshot.file.origin, snapshot.system, snapshot.category)
        ids = linked.setdefault(key, set())
        ids.update(r['resource_id'] for r in snapshot.rows if matches(r, subject))
    observations = []
    for snapshot in snapshots:
        key = (snapshot.file.origin, snapshot.system, snapshot.category)
        rows = {row['resource_id']: row for row in snapshot.rows}
        if len(rows) != len(snapshot.rows):
            raise AuditError('Duplicate resource inside scoped copy')
        for resource in sorted(linked[key]):
            row = rows.get(resource)
            if row:
                # Known resources may legitimately lose identifiers after
                # redaction/anonymization; contradictory surviving IDs may not.
                has_link = matches(row, subject)
                for field in ('user_id', 'customer_reference', 'subject_reference'):
                    if row.get(field) and row[field] != subject.user_id and normalize('email', row[field]) not in subject.aliases['email']:
                        raise AuditError('Resource reassigned to another subject')
                if not has_link and snapshot.category in {'USER_PROFILE', 'SEARCH_INDEX_ENTRY', 'USER_EXPORT'}:
                    raise AuditError('Known deletable resource has conflicting/removed identity')
                if snapshot.category == 'USER_PROFILE' and row.get('account_status') != 'ACTIVE':
                    raise AuditError('Non-active profile requires a dedicated tombstone schema')
            observations.append(Observation(
                snapshot.system, resource, snapshot.category, snapshot.copy_id,
                row is not None, snapshot.observed_at,
                timestamp(row.get('updated_at', row.get('indexed_at'))) if row else None,
                snapshot.file.file_id, snapshot.file.captured_at, snapshot.table,
                tuple((k, str(row[k])) for k in ('user_id', 'customer_reference', 'subject_reference', 'email', 'phone') if row and row.get(k)),
                row or {}, subject.user_id,
            ))
    return tuple(observations)


def latest_per_copy(observations, cutoff):
    latest = {}
    for observation in observations:
        if observation.available_at > cutoff or observation.observed_at > cutoff:
            continue
        key = (observation.system_id, observation.resource_id, observation.copy_id)
        previous = latest.get(key)
        if previous and previous.observed_at == observation.observed_at:
            if (previous.present, previous.facts) != (observation.present, observation.facts):
                raise AuditError('Conflicting copy states at the same observation time')
        if previous is None or (observation.observed_at, observation.evidence_id) > (previous.observed_at, previous.evidence_id):
            latest[key] = observation
    return tuple(latest[key] for key in sorted(latest))
