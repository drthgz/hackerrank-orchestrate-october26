"""Scoped account snapshots, with copies kept separate until policy planning."""
import json
import re
import sqlite3
from dataclasses import dataclass

from .identity import matches
from .models import AuditError, EvidenceFile, Observation, timestamp

PROFILE_TABLES = {'customer_profiles_primary', 'customer_profiles_failover_replica'}
REQUIRED_COLUMNS = {'resource_id', 'user_id', 'full_name', 'email', 'phone', 'account_status', 'updated_at'}


@dataclass
class Snapshot:
    file: EvidenceFile
    table: str
    rows: list[dict]

    @property
    def copy_id(self):
        # Origin identifies the export lineage; table identifies the physical copy.
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
            if name in PROFILE_TABLES and (not header or not REQUIRED_COLUMNS <= columns):
                raise AuditError(f'{file.file_id}: unsupported profile schema')
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
        for table, rows in tables.items():
            if table in PROFILE_TABLES:
                for row in rows:
                    if timestamp(row['updated_at']) > file.captured_at:
                        raise AuditError(f'{file.file_id}: row update is later than its snapshot')
                snapshots.append(Snapshot(file, table, rows))
            else:
                # Detect subject-linked unsupported SQL without treating another
                # schema as a profile. No JSON evidence-file adapter is involved.
                for row in rows:
                    payload = json.loads(row['record_json']) if 'record_json' in row else row
                    if matches(row, subject) or (isinstance(payload, dict) and matches(payload, subject)):
                        raise AuditError(f'{file.file_id}: subject-linked SQL table unsupported: {table}')
    # Discover resources by identifiers, never by case/resource number patterns.
    resources_by_origin = {}
    for snapshot in snapshots:
        ids = resources_by_origin.setdefault(snapshot.file.origin, set())
        for row in snapshot.rows:
            if matches(row, subject):
                if row['account_status'] != 'ACTIVE':
                    raise AuditError('Non-active account/tombstone interpretation is unsupported')
                ids.add(row['resource_id'])
    observations = []
    for snapshot in snapshots:
        rows = {row['resource_id']: row for row in snapshot.rows}
        for resource in sorted(resources_by_origin[snapshot.file.origin]):
            row = rows.get(resource)
            if row is not None and not matches(row, subject):
                raise AuditError('Known resource has conflicting or removed identity; unsupported transition')
            observations.append(Observation(
                'account_service', resource, 'USER_PROFILE', snapshot.copy_id,
                row is not None, snapshot.file.captured_at,
                timestamp(row['updated_at']) if row else None,
                snapshot.file.file_id, snapshot.file.captured_at, snapshot.table,
                tuple((k, row[k]) for k in ('user_id', 'email', 'phone') if row and row[k]),
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
            if previous.present != observation.present:
                raise AuditError('Conflicting copy states at the same observation time')
        if previous is None or (observation.observed_at, observation.evidence_id) > (previous.observed_at, previous.evidence_id):
            latest[key] = observation
    return tuple(latest[key] for key in sorted(latest))
