"""Generated-in-test evidence with unrelated identifiers; never public labels."""
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from test_structured import IDENTITY, REQUEST, RULES, EARLY, NOW, FUTURE, profile
from audit.models import AuditError, EvidenceFile, timestamp
from audit.inputs import Inputs
from audit.identity import resolve_subject, matches
from audit.evidence import extract_observations, json_records
from audit.sql_evidence import latest_per_copy
from audit.pipeline import audit
from audit.text_evidence import parse_line


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.subject = resolve_subject(REQUEST.email, REQUEST.audit_at, [IDENTITY], [])

    def file(self, name, data, captured=NOW, suffix='.json'):
        path = self.root / (name + suffix)
        path.write_text(json.dumps(data) if suffix == '.json' else data, encoding='utf-8')
        return EvidenceFile(name, path, 'fixture-service', timestamp(captured))

    def bundle(self, *snapshots, name='bundle', captured=NOW):
        return self.file(name, dict(exported_at=captured, snapshots=list(snapshots)), captured)

    def snapshot(self, collection, records, captured=NOW, **kwargs):
        return dict(collection=collection, captured_at=captured, records=records, **kwargs)

    def observations(self, *files):
        return latest_per_copy(extract_observations(files, self.subject, REQUEST.audit_at), REQUEST.audit_at)

    def inputs(self, *files):
        return Inputs((REQUEST,), [IDENTITY], [], [], RULES, tuple(files))

    def line(self, event, fields='', service='account_service', trace='arbitrary-trace', when=NOW):
        return f'{when} service={service} trace_id={trace} event={event} {fields}\n'

    def test_nested_json_search_document_and_lists(self):
        file = self.bundle(self.snapshot('customer_search_documents', [dict(resource_id='index-amber', document={'owners': [{'email': IDENTITY['email']}]} )]))
        o, = self.observations(file)
        self.assertEqual((o.resource_id, o.evidence_id), ('index-amber', 'bundle'))
        self.assertTrue(matches({'owners': [{'email': IDENTITY['email']}]}, self.subject))

    def test_nested_conflicting_owner_rejected(self):
        file = self.bundle(self.snapshot('customer_search_documents', [dict(resource_id='index-amber', customer_reference='different-subject', document={'email': IDENTITY['email']})]))
        with self.assertRaises(AuditError):
            self.observations(file)

    def test_anonymous_record_needs_lineage(self):
        row = dict(resource_id='metric-mauve', user_id=None, email=None, phone=None, email_hash=None)
        file = self.bundle(self.snapshot('customer_analytics_reports', [row]))
        self.assertEqual(self.observations(file), ())

    def test_anonymized_record_keeps_historical_resource_lineage(self):
        current = dict(resource_id='metric-mauve', user_id=None, email=None, phone=None, email_hash=None)
        old = dict(current, user_id=IDENTITY['user_id'], email=IDENTITY['email'])
        file = self.bundle(self.snapshot('customer_analytics_reports', [old], EARLY), self.snapshot('customer_analytics_reports', [current]))
        o, = self.observations(file)
        self.assertIsNone(o.facts['email'])
        self.assertEqual(o.observed_at, timestamp(NOW))

    def test_complete_covers_absent_profile_and_retained_security(self):
        file = self.bundle(self.snapshot('customer_profiles', [profile()], EARLY),
                           self.snapshot('customer_profiles', []),
                           self.snapshot('security_audit_events', [dict(resource_id='audit-copper', subject_reference=IDENTITY['user_id'], retention_until=FUTURE)]))
        result, _ = audit(REQUEST, self.inputs(file))
        self.assertEqual(result.deletion_status, 'COMPLETE')
        self.assertEqual([s.operation for s in result.steps], ['VERIFY_RECORD_ABSENT', 'VERIFY_RECORD_PRESENT'])
        self.assertTrue(all(s.evidence_id == file.file_id for s in result.steps))

    def test_independent_json_replica_survives_clean_primary(self):
        file = self.bundle(self.snapshot('customer_profiles', [profile()], EARLY, copy_id='primary'),
                           self.snapshot('customer_profiles', [], copy_id='primary'),
                           self.snapshot('customer_profiles', [profile()], copy_id='failover'))
        result, _ = audit(REQUEST, self.inputs(file))
        self.assertEqual(result.deletion_status, 'INCOMPLETE')
        copies = self.observations(file)
        self.assertEqual({o.copy_id: o.present for o in copies}, {'account_service:primary': False, 'account_service:failover': True})

    def test_unrelated_collection_snapshot_does_not_erase_resource(self):
        old = self.bundle(self.snapshot('security_audit_events', [dict(resource_id='audit-copper', subject_reference=IDENTITY['user_id'])]), name='one')
        other = self.bundle(self.snapshot('security_audit_events', []), name='other')
        o, = self.observations(old, other)
        self.assertTrue(o.present)

    def test_late_file_cannot_supply_earlier_state(self):
        file = self.bundle(self.snapshot('customer_profiles', [profile()], EARLY), captured=FUTURE)
        self.assertEqual(self.observations(file), ())

    def test_future_dated_rows_are_excluded(self):
        file = self.bundle(self.snapshot('customer_profiles', [profile()], FUTURE))
        self.assertEqual(self.observations(file), ())

    def test_manifest_conflict_and_post_snapshot_update_fail(self):
        file = self.bundle(self.snapshot('customer_profiles', [profile()]))
        with self.assertRaises(AuditError):
            json_records(replace(file, captured_at=timestamp(FUTURE)))
        file = self.bundle(self.snapshot('customer_profiles', [dict(profile(), updated_at=FUTURE)]))
        with self.assertRaises(AuditError):
            self.observations(file)

    def test_resource_reassignment_is_not_silently_joined(self):
        old = self.snapshot('customer_profiles', [profile()], EARLY)
        new = self.snapshot('customer_profiles', [dict(profile(), customer_reference=None, email='other@example.invalid', phone=None)])
        with self.assertRaises(AuditError):
            self.observations(self.bundle(old, new))

    def test_internal_connector_selector(self):
        file = self.bundle(self.snapshot('connector_configurations', [dict(resource_id='stream-gold', subject_selector=IDENTITY['user_id'], enabled=True)]))
        o, = self.observations(file)
        self.assertEqual(o.category, 'DATA_FLOW')

    def test_trace_start_proves_subject_of_resource_readback(self):
        log = self.line('profile_lookup_started', 'lookup_key=' + IDENTITY['email'])
        log += self.line('profile_lookup_completed', 'resource_id=profile-blue rows=0 http_status=404')
        o, = self.observations(self.file('trace', log, suffix='.log'))
        self.assertFalse(o.present)
        self.assertEqual((o.evidence_id, o.source_table), ('trace', 'log:2:profile_lookup_completed'))

    def test_interleaved_traces_do_not_mix_subjects(self):
        log = self.line('profile_lookup_started', 'lookup_key=' + IDENTITY['email'], trace='ours')
        log += self.line('profile_lookup_started', 'lookup_key=other@example.invalid', trace='theirs')
        log += self.line('profile_lookup_completed', 'resource_id=other-resource rows=1 http_status=200', trace='theirs')
        log += self.line('profile_lookup_completed', 'resource_id=our-resource rows=0 http_status=404', trace='ours')
        o, = self.observations(self.file('trace', log, suffix='.log'))
        self.assertEqual(o.resource_id, 'our-resource')

    def test_trace_context_does_not_cross_files_or_services(self):
        start = self.file('start', self.line('profile_lookup_started', 'lookup_key=' + IDENTITY['email']), suffix='.log')
        end = self.file('end', self.line('profile_lookup_completed', 'resource_id=unlinked rows=0 http_status=404'), suffix='.log')
        self.assertEqual(self.observations(start, end), ())
        mixed = self.file('mixed', start.path.read_text() + self.line('index_query_completed', 'resource_id=unlinked result=hit', service='search_service'), suffix='.log')
        self.assertEqual(self.observations(mixed), ())

    def test_trace_reuse_resets_context(self):
        log = self.line('profile_lookup_started', 'lookup_key=' + IDENTITY['email'])
        log += self.line('profile_lookup_started', 'lookup_key=other@example.invalid')
        log += self.line('profile_lookup_completed', 'resource_id=other-resource rows=1 http_status=200')
        self.assertEqual(self.observations(self.file('reuse', log, suffix='.log')), ())

    def test_mutation_success_and_cache_miss_are_not_absence(self):
        log = self.line('delete_completed', 'resource_id=profile-blue result=SUCCESS correlation_key=' + IDENTITY['email'])
        log += self.line('cache_lookup', 'resource_id=profile-blue result=miss')
        self.assertEqual(self.observations(self.file('claims', log, suffix='.log')), ())

    def test_failed_lookup_is_not_a_state(self):
        log = self.line('profile_lookup_completed', 'resource_id=profile-blue rows=0 http_status=503 correlation_key=' + IDENTITY['email'])
        self.assertEqual(self.observations(self.file('error', log, suffix='.log')), ())

    def test_all_log_encodings_parse_equivalent_fields(self):
        payload = dict(service='account_service', trace_id='t', event='profile_lookup_completed', resource_id='r', rows='0', http_status='404')
        encoded = json.dumps('event="profile_lookup_completed" resource_id="r" rows="0" http_status="404"')
        lines = [
            NOW + ' ' + json.dumps(payload),
            NOW + ' | INFO | account_service | t | profile_lookup_completed | resource_id="r" rows="0" http_status="404"',
            NOW + ' [INFO] [account_service] [t] profile_lookup_completed: resource_id="r" rows="0" http_status="404"',
            NOW + ' <14>1 node account_service t - - event="profile_lookup_completed" resource_id="r" rows="0" http_status="404"',
            NOW + ' requestId=t function=account_service message=' + encoded,
        ]
        for line in lines:
            with self.subTest(line=line):
                _, fields = parse_line(line)
                self.assertEqual((fields['service'], fields['trace_id'], fields['event'], fields['resource_id']), ('account_service', 't', 'profile_lookup_completed', 'r'))

    def test_pipe_log_context_and_interleaved_subjects(self):
        log = f'{NOW} | DEBUG | account_service | ours | profile_lookup_started | instance="one" lookup_key="{IDENTITY["email"]}"\n'
        log += f'{NOW} | DEBUG | account_service | theirs | profile_lookup_started | instance="one" lookup_key="other@example.invalid"\n'
        log += f'{NOW} | INFO | account_service | theirs | profile_lookup_completed | instance="one" resource_id="other" rows="1" http_status="200"\n'
        log += f'{NOW} | INFO | account_service | ours | profile_lookup_completed | instance="one" resource_id="our-profile" rows="0" http_status="404"\n'
        o, = self.observations(self.file('pipe', log, suffix='.log'))
        self.assertEqual(o.resource_id, 'our-profile')
        self.assertFalse(o.present)

    def test_log_future_event_is_excluded(self):
        log = self.line('profile_lookup_completed', 'resource_id=profile-blue rows=0 http_status=404 correlation_key=' + IDENTITY['email'], when=FUTURE)
        self.assertEqual(self.observations(self.file('future', log, suffix='.log')), ())

    def test_readback_result_is_not_workflow_success(self):
        row = dict(recorded_at=NOW, system='account_service', resource_id='profile-blue', record_type='USER_PROFILE', result='SUCCESS', subject_reference=IDENTITY['email'])
        with self.assertRaises(AuditError):
            self.observations(self.file('claims', dict(exported_at=NOW, records=[row])))

    def test_service_json_nested_search_hit(self):
        row = dict(observed_at=NOW, resource_id='search-lime', hits={'total': 1, 'documents': [dict(resource_id='search-lime', email=IDENTITY['email'])]})
        file = self.file('service', dict(exported_at=NOW, service_exports={'search_service': {'index_queries': [row]}}))
        o, = self.observations(file)
        self.assertEqual(o.facts['email'], IDENTITY['email'])

    def test_plain_text_readback_preserves_citation(self):
        line = f'- {NOW} | account_service | profile-blue | USER_PROFILE | NOT_FOUND | {IDENTITY["email"]}'
        result, _ = audit(REQUEST, self.inputs(self.file('handover', line, suffix='.txt')))
        self.assertEqual(result.deletion_status, 'COMPLETE')
        self.assertEqual(result.steps[0].evidence_id, 'handover')

    def test_missing_retention_date_remains_unsupported(self):
        file = self.bundle(self.snapshot('security_audit_events', [dict(resource_id='audit-copper', subject_reference=IDENTITY['user_id'])]))
        with self.assertRaisesRegex(AuditError, 'retention applicability'):
            audit(REQUEST, self.inputs(file))

    def test_support_context_and_exposed_identifiers(self):
        file = self.bundle(self.snapshot('support_conversations', [dict(resource_id='ticket-plum', subject_reference=IDENTITY['user_id'], message_text='Please update my order using ' + IDENTITY['email'])]))
        result, _ = audit(REQUEST, self.inputs(file))
        self.assertEqual([s.operation for s in result.steps], ['REPORT_EXPOSED_PII', 'REDACT_RECORD', 'VERIFY_RECORD_REDACTED'])

    def test_partial_support_text_does_not_prove_redaction(self):
        file = self.bundle(self.snapshot('support_conversations', [dict(resource_id='ticket-plum', subject_reference=IDENTITY['user_id'], message_excerpt='Customer followed up about an order update.')]))
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs(file))

    def test_complete_incomplete_plan_includes_already_retained_record(self):
        file = self.bundle(self.snapshot('customer_profiles', [profile()]), self.snapshot('security_audit_events', [dict(resource_id='audit-copper', subject_reference=IDENTITY['user_id'], retention_until=FUTURE)]))
        result, _ = audit(REQUEST, self.inputs(file))
        self.assertEqual(result.deletion_status, 'INCOMPLETE')
        self.assertEqual([s.operation for s in result.steps], ['REPORT_REMAINING_RECORD', 'DELETE_RECORD', 'VERIFY_RECORD_ABSENT', 'VERIFY_RECORD_PRESENT'])
        self.assertEqual(result.steps[-1].evidence_id, '')

    def test_unparsed_media_still_blocks_complete(self):
        log = self.line('profile_lookup_completed', 'resource_id=profile-blue rows=0 http_status=404 correlation_key=' + IDENTITY['email'])
        file = self.file('trace', log, suffix='.log')
        unknown = self.file('unparsed', 'placeholder', suffix='.pdf')
        with self.assertRaisesRegex(AuditError, 'unprocessed evidence scope'):
            audit(REQUEST, self.inputs(file, unknown))

    def test_explicit_source_reference_supplies_account_verification(self):
        sql = f"""-- Captured at: {NOW}
CREATE TABLE customer_profiles_primary (resource_id TEXT,user_id TEXT,full_name TEXT,email TEXT,phone TEXT,account_status TEXT,updated_at TEXT);
CREATE TABLE search_documents_primary (resource_id TEXT,email TEXT,source_resource_id TEXT,indexed_at TEXT);
INSERT INTO search_documents_primary VALUES ('index-amber','{IDENTITY['email']}','profile-blue','{EARLY}');
"""
        result, _ = audit(REQUEST, self.inputs(self.file('inventory', sql, suffix='.sql')))
        self.assertEqual([(s.operation, s.resource_id) for s in result.steps if s.phase == 'VERIFICATION'],
                         [('VERIFY_RECORD_ABSENT', 'profile-blue'), ('VERIFY_RECORD_ABSENT', 'index-amber')])

    def test_name_and_formatted_phone_scans_detect_pii(self):
        for content in [IDENTITY['name'], '+1 (555) 0123']:
            file = self.bundle(self.snapshot('support_conversations', [dict(
                resource_id='ticket-plum', subject_reference=IDENTITY['user_id'],
                requester_name=None, requester_email=None, requester_phone=None,
                message_text='Please update the order for ' + content)]))
            with self.subTest(content=content):
                result, _ = audit(REQUEST, self.inputs(file))
                self.assertEqual(result.steps[0].operation, 'REPORT_EXPOSED_PII')

    def test_excerpt_with_null_contact_fields_is_not_full_redaction_proof(self):
        file = self.bundle(self.snapshot('support_conversations', [dict(
            resource_id='ticket-plum', subject_reference=IDENTITY['user_id'],
            requester_name=None, requester_email=None, requester_phone=None,
            message_excerpt='Customer followed up about an order update.')]))
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs(file))

    def test_secondary_contact_replica_preserves_logical_system_and_copy(self):
        log = self.line('contact_query_started', 'lookup_key=' + IDENTITY['email'], service='support_replica')
        log += self.line('contact_query_completed', 'resource_id=contact-teal rows=1', service='support_replica')
        o, = self.observations(self.file('contacts', log, suffix='.log'))
        self.assertEqual((o.system_id, o.copy_id, o.category),
                         ('support_platform', 'support_platform:support_replica', 'SECONDARY_IDENTIFIER'))

    def test_missing_attachment_can_be_verified_without_deleting_context(self):
        file = self.bundle(self.snapshot('ticket_attachments', [dict(
            resource_id='upload-pink', uploaded_by=IDENTITY['email'], belongs_only_to_subject=True)], EARLY),
            self.snapshot('ticket_attachments', []), self.snapshot('customer_profiles', [profile()]))
        # Ownership is a policy condition, not an assumption from the uploader.
        result, _ = audit(REQUEST, self.inputs(file))
        self.assertTrue(any(s.operation == 'VERIFY_RECORD_ABSENT' and s.resource_id == 'upload-pink' for s in result.steps))
        self.assertFalse(any(s.phase == 'REMEDIATION' and s.resource_id == 'upload-pink' for s in result.steps))

    def test_legal_retention_metadata_and_complete_verification(self):
        file = self.bundle(self.snapshot('customer_profiles', [profile()]), self.snapshot('retained_order_records', [dict(
            resource_id='legal-jade', subject_reference=IDENTITY['user_id'], legal_hold_active=True, retained_until=FUTURE)]))
        result, _ = audit(REQUEST, self.inputs(file))
        self.assertEqual(result.steps[-1].operation, 'VERIFY_RECORD_PRESENT')

    def test_prediction_does_not_read_labels_across_all_adapters(self):
        import subprocess
        import sys
        root = Path(__file__).resolve().parents[1]
        script = """
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
def guard(event, args):
    if event == 'open' and 'sample_output' in str(args[0]):
        raise RuntimeError('Predictor attempted label access')
sys.addaudithook(guard)
from audit.inputs import load_inputs
from audit.pipeline import audit
from audit.models import AuditError
root = Path(sys.argv[2])
inputs = load_inputs(root / 'dataset', root / 'dataset/sample_deletion_requests.csv')
for request in inputs.requests:
    try:
        audit(request, inputs)
    except AuditError:
        pass
"""
        subprocess.run([sys.executable, '-c', script, str(root / 'code'), str(root)], check=True, capture_output=True)


if __name__ == '__main__':
    unittest.main()
