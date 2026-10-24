"""Synthetic fixtures use arbitrary IDs and no sample labels."""
import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
from audit.contract import order_steps, read_output, validate_result, write_output
from audit.identity import matches, resolve_subject
from audit.inputs import Inputs, SCHEMAS, load_inputs
from audit.models import AuditError, EvidenceFile, Request, Step, timestamp
from audit.pipeline import assess_policy, audit, authorize_deletion, plan
from audit.sql_evidence import extract_observations, latest_per_copy, read_sql

T0 = '2026-02-01T00:00:00Z'
T1 = '2026-03-01T00:00:00Z'
T2 = '2026-04-01T00:00:00Z'
T3 = '2026-05-01T00:00:00Z'
IDENTITY = dict(user_id='person-z', name='Fictional Person', email='new@example.invalid',
                phone='+1 555 0100', email_hash='abc', updated_at=T0)
RULE = dict(rule_id='delete-profiles', data_category='USER_PROFILE', condition='Always', required_action='DELETE')
REQUEST = Request('arbitrary-case', 'new@example.invalid', timestamp(T0), 'COMPLETE', timestamp(T0),
                  timestamp(T2), 'Please remove my profile.')


def subject():
    return resolve_subject(REQUEST.email, REQUEST.audit_at, [IDENTITY], [])


def sql_text(rows_by_table, captured=T1, updated=T1):
    parts = [f'-- Captured at: {captured}']
    for table, resources in rows_by_table.items():
        parts.append(f'CREATE TABLE {table} (resource_id TEXT PRIMARY KEY,user_id TEXT,full_name TEXT,email TEXT,phone TEXT,account_status TEXT,updated_at TEXT);')
        for resource, owner, email in resources:
            values = (resource, owner, 'Fictional Person', email, '+1 555 0100', 'ACTIVE', updated)
            parts.append(f'INSERT INTO {table} VALUES (' + ','.join("'" + v.replace("'", "''") + "'" for v in values) + ');')
    return '\n'.join(parts)


class SliceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def evidence(self, rows=None, captured=T1, updated=T1, fid='source-a', origin='account-export', raw=None):
        path = self.root / (fid + '.sql')
        if rows is None:
            rows = {'customer_profiles_primary': [], 'customer_profiles_failover_replica': [('resource-q', 'person-z', IDENTITY['email'])]}
        path.write_text(raw if raw is not None else sql_text(rows, captured, updated))
        return EvidenceFile(fid, path, origin, timestamp(captured))

    def inputs(self, files, activity=None, rules=None):
        return Inputs((REQUEST,), [IDENTITY], [], activity or [], rules if rules is not None else [RULE], tuple(files))

    def test_historical_email_and_case_normalization(self):
        event = dict(audit_id='history-a', user_id='person-z', field_name='email', old_value='old@example.invalid', new_value=IDENTITY['email'], event_time=T1)
        found = resolve_subject('OLD@EXAMPLE.INVALID', timestamp(T2), [IDENTITY], [event])
        self.assertEqual(found.user_id, 'person-z')
        self.assertIn('history-a', found.provenance)
        self.assertIn(IDENTITY['email'], found.aliases['email'])

    def test_future_alias_not_available(self):
        with self.assertRaises(AuditError):
            resolve_subject(IDENTITY['email'], timestamp(T2), [dict(IDENTITY, updated_at=T3)], [])

    def test_earlier_audit_can_resolve_without_future_snapshot(self):
        event = dict(audit_id='h', user_id='person-z', field_name='email', old_value='old@example.invalid', new_value='then@example.invalid', event_time=T1)
        found = resolve_subject('old@example.invalid', timestamp(T2), [dict(IDENTITY, updated_at=T3)], [event])
        self.assertNotIn(IDENTITY['email'], found.aliases['email'])

    def test_future_history_excluded(self):
        event = dict(audit_id='h', user_id='person-z', field_name='email', old_value='old@example.invalid', new_value='future@example.invalid', event_time=T3)
        with self.assertRaises(AuditError):
            resolve_subject('future@example.invalid', timestamp(T2), [IDENTITY], [event])

    def test_ambiguous_identity_fails(self):
        with self.assertRaises(AuditError):
            resolve_subject(REQUEST.email, REQUEST.audit_at, [IDENTITY, dict(IDENTITY, user_id='other')], [])

    def test_names_are_not_identity_keys(self):
        self.assertFalse(matches({'full_name': IDENTITY['name']}, subject()))

    def test_conflicting_stable_reference_fails(self):
        with self.assertRaises(AuditError):
            matches({'user_id': 'other', 'email': IDENTITY['email']}, subject())

    def test_primary_absent_replica_present(self):
        file = self.evidence()
        result, details = audit(REQUEST, self.inputs([file]))
        self.assertEqual(result.deletion_status, 'INCOMPLETE')
        self.assertEqual([s.operation for s in result.steps], ['REPORT_REMAINING_RECORD', 'DELETE_RECORD', 'VERIFY_RECORD_ABSENT'])
        self.assertEqual(result.steps[0].resource_id, 'resource-q')
        self.assertEqual(result.steps[0].evidence_id, 'source-a')
        states = {o['source_table']: o['present'] for o in details['latest_copy_states']}
        self.assertEqual(states, {'customer_profiles_primary': False, 'customer_profiles_failover_replica': True})

    def test_primary_survives_clean_replica(self):
        file = self.evidence({'customer_profiles_primary': [('different-id', 'person-z', IDENTITY['email'])], 'customer_profiles_failover_replica': []})
        result, _ = audit(REQUEST, self.inputs([file]))
        self.assertEqual(result.steps[0].resource_id, 'different-id')

    def test_duplicate_copy_findings_collapse_but_provenance_remains(self):
        row = [('resource-q', 'person-z', IDENTITY['email'])]
        result, detail = audit(REQUEST, self.inputs([self.evidence({t: row for t in ['customer_profiles_primary', 'customer_profiles_failover_replica']})]))
        self.assertEqual(len(result.steps), 3)
        self.assertEqual(len(detail['latest_copy_states']), 2)

    def test_later_primary_cannot_erase_older_replica(self):
        first = self.evidence()
        later = self.evidence({'customer_profiles_primary': []}, captured=T2, fid='source-b')
        result, _ = audit(REQUEST, self.inputs([first, later]))
        self.assertEqual(result.steps[0].evidence_id, 'source-a')

    def test_later_snapshot_of_same_copy_replaces_old_state(self):
        first = self.evidence()
        later = self.evidence({'customer_profiles_failover_replica': []}, captured=T2, fid='source-b')
        observations = extract_observations([first, later], subject(), REQUEST.audit_at)
        states = latest_per_copy(observations, REQUEST.audit_at)
        self.assertTrue(all(not o.present for o in states))
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([first, later]))  # No global COMPLETE claim.

    def test_post_cutoff_evidence_never_changes_answer(self):
        first = self.evidence()
        future = self.evidence(captured=T3, fid='future', raw='ATTACH DATABASE "/tmp/forbidden" AS x;')
        one, _ = audit(REQUEST, self.inputs([first]))
        two, _ = audit(REQUEST, self.inputs([first, future]))
        self.assertEqual(one, two)

    def test_snapshot_capture_boundary_inclusive(self):
        result, _ = audit(REQUEST, self.inputs([self.evidence(captured=T2)]))
        self.assertEqual(result.deletion_status, 'INCOMPLETE')

    def test_updated_after_capture_rejected(self):
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([self.evidence(updated=T3)]))

    def test_manifest_header_conflict_rejected(self):
        file = self.evidence()
        with self.assertRaises(AuditError):
            read_sql(replace(file, captured_at=timestamp(T2)))

    def test_conflicting_same_time_copy_states_rejected(self):
        a = self.evidence()
        b = self.evidence({'customer_profiles_failover_replica': []}, fid='source-b')
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([a, b]))

    def test_unconditional_delete_policy_required(self):
        for rules in [[], [RULE, dict(RULE, rule_id='duplicate')], [dict(RULE, required_action='RETAIN')], [dict(RULE, condition='Legal hold inactive')]]:
            with self.subTest(rules=rules), self.assertRaises(AuditError):
                audit(REQUEST, self.inputs([self.evidence()], rules=rules))

    def test_tombstone_not_deleted_as_profile(self):
        file = self.evidence()
        file.path.write_text(file.path.read_text().replace("'ACTIVE'", "'TOMBSTONE'"))
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([file]))

    def test_reported_workflow_status_does_not_change_state(self):
        data = self.inputs([self.evidence()])
        a, _ = audit(REQUEST, data)
        b, _ = audit(replace(REQUEST, reported_status='NOT_STARTED'), data)
        self.assertEqual(a, b)

    def test_success_claim_cannot_remove_surviving_record(self):
        claim = dict(activity_id='claim', resource_id='resource-q', event_time=T0, reported_result='SUCCESS', event_type='DELETE_RECORD')
        result, details = audit(REQUEST, self.inputs([self.evidence()], [claim]))
        self.assertEqual(result.deletion_status, 'INCOMPLETE')
        self.assertEqual(details['activity_claims'], [claim])

    def test_post_snapshot_claim_requires_further_evidence(self):
        claim = dict(activity_id='claim', resource_id='resource-q', event_time=T2, reported_result='SUCCESS')
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([self.evidence()], [claim]))

    def test_sql_attach_and_file_functions_denied(self):
        for statement in ['ATTACH DATABASE ":memory:" AS other;', 'SELECT load_extension("abc");', 'PRAGMA writable_schema=ON;']:
            with self.subTest(statement=statement), self.assertRaises(AuditError):
                read_sql(self.evidence(raw='-- Captured at: ' + T1 + '\n' + statement))

    def test_subject_linked_unknown_sql_rejected(self):
        file = self.evidence(raw=f'CREATE TABLE unknown (user_id TEXT); INSERT INTO unknown VALUES (\'person-z\');')
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([file]))

    def test_no_identity_link_is_not_absence_proof(self):
        file = self.evidence({'customer_profiles_primary': [], 'customer_profiles_failover_replica': []})
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([file]))

    def test_negated_or_conditional_intent_rejected(self):
        for text in ['Please do not remove my profile.', 'If my invoice is paid, please delete my account.', 'Please export my profile.', 'Should I delete my account?']:
            with self.subTest(text=text), self.assertRaises(AuditError):
                authorize_deletion(text)

    def test_official_operation_order_not_alphabetical(self):
        steps = [Step(0, 'VERIFICATION', 'z', 'b', 'VERIFY_RECORD_ABSENT', 'ABSENT', ''),
                 Step(0, 'FINDING', 'a', 'q', 'REPORT_ACTIVE_DATA_FLOW', 'ACTIVE', 'proof'),
                 Step(0, 'FINDING', 'z', 'q', 'REPORT_REMAINING_RECORD', 'PRESENT', 'proof'),
                 Step(0, 'VERIFICATION', 'a', 'b', 'VERIFY_RECORD_ABSENT', 'ABSENT', '')]
        ordered = order_steps(steps)
        self.assertEqual([s.operation for s in ordered[:2]], ['REPORT_REMAINING_RECORD', 'REPORT_ACTIVE_DATA_FLOW'])
        self.assertEqual([s.system_id for s in ordered[2:]], ['a', 'z'])
        self.assertEqual([s.step_no for s in ordered], [1, 2, 3, 4])

    def test_validation_rejects_future_citation_and_incorrect_state(self):
        result, _ = audit(REQUEST, self.inputs([self.evidence()]))
        with self.assertRaises(AuditError):
            validate_result(result, REQUEST, {'source-a': timestamp(T3)})
        invalid = replace(result, steps=(replace(result.steps[0], state='ABSENT'), *result.steps[1:]))
        with self.assertRaises(AuditError):
            validate_result(invalid, REQUEST, {'source-a': timestamp(T1)})

    def test_validation_rejects_missing_verification_and_bad_number(self):
        result, _ = audit(REQUEST, self.inputs([self.evidence()]))
        for invalid in [replace(result, steps=result.steps[:2]), replace(result, steps=(replace(result.steps[0], step_no=True), *result.steps[1:]))]:
            with self.assertRaises(AuditError):
                validate_result(invalid, REQUEST, {'source-a': timestamp(T1)})

    def test_output_roundtrip_and_exact_coverage(self):
        result, _ = audit(REQUEST, self.inputs([self.evidence()]))
        path = self.root / 'result.csv'
        write_output(path, [result], [REQUEST], {'source-a': timestamp(T1)})
        self.assertEqual(read_output(path), [result])
        with self.assertRaises(AuditError):
            write_output(path, [result, result], [REQUEST], {'source-a': timestamp(T1)})

    def test_loader_rejects_path_escape(self):
        dataset = self.root / 'dataset'
        dataset.mkdir()
        for name, schema in SCHEMAS.items():
            path = dataset / (name + '.csv')
            with path.open('w', newline='') as f:
                w = csv.writer(f); w.writerow(schema.split(','))
                if name == 'evidence_files':
                    w.writerow(['external', '../secret.sql', 'origin', T1])
        (self.root / 'secret.sql').write_text('')
        with self.assertRaises(AuditError):
            load_inputs(dataset, dataset / 'requests.csv')

    def test_validator_rejects_remediation_for_wrong_resource(self):
        result, _ = audit(REQUEST, self.inputs([self.evidence()]))
        steps = order_steps([result.steps[0], replace(result.steps[1], resource_id='wrong'),
                             result.steps[2], replace(result.steps[2], resource_id='wrong')])
        with self.assertRaises(AuditError):
            validate_result(replace(result, steps=steps), REQUEST, {'source-a': timestamp(T1)})

    def test_evaluator_detects_field_and_sequence_errors(self):
        spec = importlib.util.spec_from_file_location('slice_evaluator', ROOT / 'code/evaluation/main.py')
        evaluator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(evaluator)
        result, _ = audit(REQUEST, self.inputs([self.evidence()]))
        expected = {'status': result.deletion_status, 'steps': [asdict(s) for s in result.steps]}
        wrong = replace(result, steps=(replace(result.steps[0], evidence_id='wrong'), *result.steps[1:]))
        report = evaluator.compare(wrong, expected)
        self.assertFalse(report['all_steps_match'])
        self.assertFalse(report['evidence_references_match'])
        self.assertEqual(report['field_matches'], 20)
        shuffled = replace(result, steps=tuple(reversed(result.steps)))
        report = evaluator.compare(shuffled, expected)
        self.assertTrue(report['all_steps_match'])
        self.assertFalse(report['step_ordering_matches'])
        self.assertFalse(evaluator.compare(replace(result, deletion_status='COMPLETE'), expected)['deletion_status_matches'])

    def test_loader_rejects_bad_header_and_duplicate_identity(self):
        from audit.inputs import read_csv
        path = self.root / 'identities.csv'
        path.write_text('wrong,header\n')
        with self.assertRaises(AuditError):
            read_csv(path, SCHEMAS['user_identities'])
        with path.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=SCHEMAS['user_identities'].split(','))
            writer.writeheader()
            writer.writerows([IDENTITY, IDENTITY])
        with self.assertRaises(AuditError):
            read_csv(path, SCHEMAS['user_identities'])

    def test_public_slice_without_label_access(self):
        # The process audit hook makes any attempted label read a test failure.
        script = '''
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
def guard(event, args):
    if event == 'open' and 'sample_output' in str(args[0]):
        raise RuntimeError('Predictor attempted label access')
sys.addaudithook(guard)
from audit.inputs import load_inputs
from audit.pipeline import audit
from audit.contract import write_output
root = Path(sys.argv[2])
data = load_inputs(root / 'dataset', root / 'dataset/sample_deletion_requests.csv')
request = next(r for r in data.requests if r.case_id == 'case_05')
result, _ = audit(request, data)
write_output(Path(sys.argv[3]), [result], [request], data.citation_times())
'''
        outputs = []
        for name in ['one.csv', 'two.csv']:
            output = self.root / name
            subprocess.run([sys.executable, '-c', script, str(ROOT / 'code'), str(ROOT), str(output)], cwd=self.root, check=True, capture_output=True)
            outputs.append(output.read_bytes())
        self.assertEqual(*outputs)


if __name__ == '__main__':
    unittest.main()
