"""Independent structured fixtures; no labels or case-number associations."""
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
from audit.inputs import Inputs
from audit.models import AuditError, EvidenceFile, Request, timestamp
from audit.pipeline import audit, classify_intent
from audit.policy import CONDITIONS

EARLY, NOW, FUTURE = ['2026-' + s + 'T00:00:00Z' for s in ('01-01', '02-01', '03-01')]
IDENTITY = dict(user_id='subject-k', name='Example Person', email='current@example.invalid', phone='15550123', email_hash='hash-k', updated_at=EARLY)
REQUEST = Request('unrelated-request-id', IDENTITY['email'], timestamp(EARLY), 'COMPLETE', timestamp(EARLY), timestamp(NOW), 'Please delete my account.')
RULES = [dict(rule_id='p-'+c, data_category=c, condition=condition, required_action=action)
         for c, (condition, action) in {**CONDITIONS, 'USER_PROFILE': ('Always', 'DELETE'), 'SEARCH_INDEX_ENTRY': ('Always', 'DELETE'), 'USER_EXPORT': ('Always', 'DELETE')}.items()]


def profile():
    return {'resource_id': 'profile-blue', 'customer_reference': 'subject-k', 'full_name': 'Example Person',
            'email': IDENTITY['email'], 'phone': IDENTITY['phone'], 'account_status': 'ACTIVE'}


class StructuredTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def file(self, fid, captured, records, tables=('customer_data_primary',), raw=None):
        path = self.root / (fid + '.sql')
        statements = [f'-- Captured at: {captured}']
        for table in tables:
            statements.append(f'CREATE TABLE {table}(resource_id TEXT PRIMARY KEY, origin_system TEXT, collection_name TEXT, record_json TEXT, updated_at TEXT);')
            for collection, system, facts in records:
                values = [facts['resource_id'], system, collection, json.dumps(facts), captured]
                statements.append(f'INSERT INTO {table} VALUES (' + ','.join("'"+v.replace("'", "''")+"'" for v in values) + ');')
        path.write_text(raw if raw is not None else '\n'.join(statements))
        return EvidenceFile(fid, path, 'generic-capture', timestamp(captured))

    def inputs(self, files, history=(), identities=None, activity=()):
        return Inputs((REQUEST,), identities if identities is not None else [IDENTITY], list(history), list(activity), RULES, tuple(files))

    def prior_profile(self):
        return self.file('prior-profile', EARLY, [('customer_profiles', 'account_service', profile())])

    def test_explicit_non_deletion_needs_no_identity_or_evidence(self):
        for text in ['Please export my data.', 'Please correct my email address.', 'Please unsubscribe me from marketing emails.', 'Please send me a copy of my personal data. Do not delete my account.']:
            result, _ = audit(replace(REQUEST, request_text=text), self.inputs([], identities=[]))
            self.assertEqual((result.deletion_status, result.steps), ('NOT_APPLICABLE', ()))

    def test_non_deletion_mixed_or_qualified_is_not_accepted(self):
        for text in ['Please export my data, then delete my account.', 'Please export my data unless my account is active.', 'Please do not export my data.', 'Please export my data. Delete my account later.']:
            with self.subTest(text=text), self.assertRaises(AuditError):
                classify_intent(text)

    def test_complete_requires_lineage_and_positive_scoped_absence(self):
        old = self.file('old-proof', EARLY, [('customer_profiles', 'account_service', profile())])
        new = self.file('new-proof', NOW, [])
        result, diagnostics = audit(REQUEST, self.inputs([old, new]))
        self.assertEqual(result.deletion_status, 'COMPLETE')
        self.assertEqual([(s.operation, s.evidence_id) for s in result.steps], [('VERIFY_RECORD_ABSENT', 'new-proof')])
        self.assertTrue(diagnostics['observations'])
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([new]))

    def test_unprocessed_source_blocks_complete(self):
        old = self.file('old', EARLY, [('customer_profiles', 'account_service', profile())])
        new = self.file('new', NOW, [])
        extra = self.root/'unparsed.txt'; extra.write_text('business evidence')
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([old, new, EvidenceFile('unparsed', extra, 'business', timestamp(NOW))]))

    def test_historical_alias_matches_nested_search_document(self):
        history = [dict(audit_id='change-z', user_id='subject-k', field_name='email', old_value='past@example.invalid', new_value=IDENTITY['email'], event_time=EARLY)]
        record = {'resource_id': 'search-green', 'document': {'email': 'PAST@EXAMPLE.INVALID'}, 'index_name': 'directory'}
        file = self.file('search-proof', NOW, [('customer_search_documents', 'search_service', record)])
        result, _ = audit(replace(REQUEST, email='past@example.invalid'), self.inputs([file], history))
        self.assertEqual(result.steps[0].resource_id, 'search-green')

    def test_generic_replica_drift_keeps_copy_states(self):
        row = [('customer_profiles', 'account_service', profile())]
        old = self.file('old', EARLY, row, ('customer_data_primary', 'customer_data_read_replica'))
        clean = self.file('clean-primary', NOW, [], ('customer_data_primary',))
        result, detail = audit(REQUEST, self.inputs([old, clean]))
        self.assertEqual(result.deletion_status, 'INCOMPLETE')
        self.assertEqual({o['present'] for o in detail['latest_copy_states']}, {True, False})

    def test_retained_record_is_verified_not_deleted(self):
        record = {'resource_id': 'retained-orange', 'subject_reference': 'subject-k', 'retention_until': FUTURE}
        file = self.file('retain-proof', NOW, [('security_audit_events', 'security_service', record)])
        result, _ = audit(REQUEST, self.inputs([self.prior_profile(), file]))
        self.assertEqual(result.deletion_status, 'COMPLETE')
        self.assertEqual([s.operation for s in result.steps], ['VERIFY_RECORD_ABSENT', 'VERIFY_RECORD_PRESENT'])

    def test_retention_expiry_boundary_and_missing_fact(self):
        for end, success in [(NOW, True), (EARLY, False), (None, False)]:
            facts = {'resource_id': 'r', 'subject_reference': 'subject-k'}
            if end: facts['retention_until'] = end
            file = self.file('retention', NOW, [('security_audit_events', 'security_service', facts)])
            if success:
                self.assertEqual(audit(REQUEST, self.inputs([self.prior_profile(), file]))[0].deletion_status, 'COMPLETE')
            else:
                with self.assertRaises(AuditError):audit(REQUEST, self.inputs([file]))

    def test_tombstone_preserved_redacted_and_exposed(self):
        retained = ('security_audit_events', 'security_service', {'resource_id': 'audit-red', 'subject_reference': 'subject-k', 'retention_until': FUTURE})
        tombstone = {'resource_id': 'tombstone-black', 'subject_reference': 'subject-k', 'account_status': 'DELETED', 'name': None, 'email': None, 'phone': None, 'email_hash': None}
        for exposed in [False, True]:
            facts = dict(tombstone, email=IDENTITY['email'] if exposed else None)
            file = self.file('tombstone-proof', NOW, [retained, ('deleted_customer_references', 'identity_service', facts)])
            result, _ = audit(REQUEST, self.inputs([self.prior_profile(), file]))
            self.assertEqual(result.deletion_status, 'INCOMPLETE' if exposed else 'COMPLETE')
            self.assertNotIn('DELETE_RECORD', [s.operation for s in result.steps])
            self.assertIn('VERIFY_RECORD_REDACTED', [s.operation for s in result.steps])
            if exposed:self.assertIn('REDACT_RECORD', [s.operation for s in result.steps])

    def test_missing_retained_record_cannot_be_declared_complete(self):
        row = [('security_audit_events', 'security_service', {'resource_id': 'audit-red', 'subject_reference': 'subject-k', 'retention_until': FUTURE})]
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([self.file('old', EARLY, row), self.file('new', NOW, [])]))

    def test_anonymized_resource_preserves_historical_lineage(self):
        facts = {'resource_id': 'analytics-violet', 'user_id': 'subject-k', 'email': IDENTITY['email'], 'phone': '15550123', 'email_hash': 'hash-k'}
        old = self.file('old', EARLY, [('customer_analytics_reports', 'analytics_platform', facts), ('customer_profiles', 'account_service', profile())])
        clean = {k: None if k != 'resource_id' else v for k,v in facts.items()}
        new = self.file('clean', NOW, [('customer_analytics_reports', 'analytics_platform', clean)])
        result, _ = audit(REQUEST, self.inputs([old,new]))
        self.assertEqual(result.deletion_status, 'COMPLETE')
        self.assertEqual(result.steps[-1].operation, 'VERIFY_RECORD_ANONYMIZED')

    def test_future_clean_snapshot_does_not_erase_residual(self):
        old = self.file('old', EARLY, [('customer_profiles', 'account_service', profile())])
        future = self.file('future', FUTURE, [])
        result, _ = audit(REQUEST, self.inputs([old,future]))
        self.assertEqual(result.deletion_status, 'INCOMPLETE')
        self.assertEqual(result.steps[0].evidence_id, 'old')

    def test_same_time_pii_disagreement_is_conflict_even_when_both_present(self):
        row = profile()
        a = self.file('a', NOW, [('customer_profiles', 'account_service', row)])
        b = self.file('b', NOW, [('customer_profiles', 'account_service', dict(row, email='different@example.invalid'))])
        with self.assertRaises(AuditError):audit(REQUEST, self.inputs([a,b]))

    def test_active_flow_and_backup_actions_precede_delete(self):
        rows = [('customer_profiles', 'account_service', profile()),
                ('connector_configurations', 'integration_service', {'resource_id':'flow-yellow', 'subject_selector':IDENTITY['email'], 'enabled':True}),
                ('backup_catalog','backup_service',{'resource_id':'backup-pink','subject_reference':'subject-k','restore_allowed':True})]
        result, _ = audit(REQUEST, self.inputs([self.file('states',NOW,rows)]))
        self.assertEqual([s.operation for s in result.steps if s.phase=='REMEDIATION'], ['DISABLE_DATA_FLOW','BLOCK_RESTORE','DELETE_RECORD'])
        self.assertTrue(all(s.evidence_id=='' for s in result.steps if s.phase!='FINDING'))

    def test_relational_inventory_snapshot_scope(self):
        raw = f'''CREATE TABLE snapshot_scope(origin_system TEXT,captured_at TEXT);
INSERT INTO snapshot_scope VALUES ('security_service','{NOW}');
CREATE TABLE security_audit_records(resource_id TEXT,subject_reference TEXT,retention_until TEXT,updated_at TEXT);
INSERT INTO security_audit_records VALUES ('proof-teal','subject-k','{FUTURE}','{EARLY}');'''
        file = self.file('inventory',NOW,[],raw=raw)
        from audit.sql_evidence import extract_observations
        from audit.policy import assess_policy
        from audit.identity import resolve_subject
        observations = extract_observations([file], resolve_subject(REQUEST.email, REQUEST.audit_at, [IDENTITY], []), REQUEST.audit_at)
        decisions = assess_policy(observations, RULES, REQUEST.audit_at)
        self.assertTrue(decisions[0].compliant)
        self.assertEqual(decisions[0].verify_operation, 'VERIFY_RECORD_PRESENT')
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([file]))  # Retention alone cannot prove account absence.

    def test_revoked_permission_is_not_deletion_authorization(self):
        with self.assertRaises(AuditError):
            classify_intent('Please delete my account. I revoke this request.')

    def test_nested_identity_cannot_override_conflicting_owner(self):
        from audit.identity import matches, resolve_subject
        found = resolve_subject(REQUEST.email, REQUEST.audit_at, [IDENTITY], [])
        with self.assertRaises(AuditError):
            matches({'customer_reference': 'somebody-else', 'document': {'email': IDENTITY['email']}}, found)

    def test_tombstone_email_is_not_a_permitted_stable_reference(self):
        retained = ('security_audit_events', 'security_service', {'resource_id': 'audit-red', 'subject_reference': 'subject-k', 'retention_until': FUTURE})
        facts = {'resource_id': 'tombstone', 'subject_reference': IDENTITY['email'], 'account_status': 'DELETED',
                 'name': None, 'email': None, 'phone': None, 'email_hash': None}
        file = self.file('bad-reference', NOW, [retained, ('deleted_customer_references', 'identity_service', facts)])
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([self.prior_profile(), file]))

    def test_tombstone_extra_name_is_prohibited(self):
        retained = ('security_audit_events', 'security_service', {'resource_id': 'audit-red', 'subject_reference': 'subject-k', 'retention_until': FUTURE})
        facts = {'resource_id': 'tombstone', 'subject_reference': 'subject-k', 'account_status': 'DELETED',
                 'name': None, 'email': None, 'phone': None, 'email_hash': None, 'full_name': 'Example Person'}
        file = self.file('extra-name', NOW, [retained, ('deleted_customer_references', 'identity_service', facts)])
        result, _ = audit(REQUEST, self.inputs([self.prior_profile(), file]))
        self.assertEqual(result.deletion_status, 'INCOMPLETE')
        self.assertIn('REDACT_RECORD', [s.operation for s in result.steps])

    def test_canonical_dependency_conflict_is_not_silently_reordered(self):
        search = {'resource_id': 'search', 'email': IDENTITY['email'], 'source_resource_id': 'profile-blue'}
        file = self.file('dependency', NOW, [('customer_profiles', 'account_service', profile()), ('customer_search_documents', 'search_service', search)])
        with self.assertRaisesRegex(AuditError, 'Dependency-safe'):
            audit(REQUEST, self.inputs([file]))

    def test_complete_across_copies_requires_single_citable_witness(self):
        old = self.file('old', EARLY, [('customer_profiles', 'account_service', profile())], ('customer_data_primary', 'customer_data_read_replica'))
        clean = self.file('clean', NOW, [], ('customer_data_primary', 'customer_data_read_replica'))
        result, _ = audit(REQUEST, self.inputs([old, clean]))
        self.assertEqual(result.deletion_status, 'COMPLETE')
        self.assertEqual(result.steps[0].evidence_id, 'clean')
        split = self.file('split', NOW, [], ('customer_data_read_replica',))
        only_primary = self.file('primary', NOW, [], ('customer_data_primary',))
        with self.assertRaisesRegex(AuditError, 'single-citation'):
            audit(REQUEST, self.inputs([old, split, only_primary]))

    def test_unknown_collection_blocks_scope_closure(self):
        old = self.file('old', EARLY, [('customer_profiles', 'account_service', profile())])
        unknown = self.file('new', NOW, [('uninterpreted', 'other_system', {'resource_id': 'profile-blue', 'opaque_payload': 'not parsed'})])
        with self.assertRaises(AuditError):
            audit(REQUEST, self.inputs([old, unknown]))

    def test_unknown_table_blocks_scope_closure(self):
        old = self.file('old',EARLY,[('customer_profiles','account_service',profile())])
        new = self.file('new',NOW,[])
        unknown=self.file('unknown',NOW,[],raw='CREATE TABLE unparsed (payload TEXT);')
        with self.assertRaises(AuditError):audit(REQUEST,self.inputs([old,new,unknown]))


if __name__ == '__main__':
    unittest.main()
