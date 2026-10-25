"""Production-only stable selector fixtures; no experiment index or labels."""
from pathlib import Path
import tempfile
import unittest

import test_structured as fixtures
from test_structured import IDENTITY, REQUEST, EARLY, NOW, FUTURE
from audit.identity import matches, resolve_subject
from audit.models import AuditError
from audit.prediction import predict


class ReleaseSelectorTests(unittest.TestCase):
    file = fixtures.StructuredTests.file
    inputs = fixtures.StructuredTests.inputs

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.subject = resolve_subject(REQUEST.email, REQUEST.audit_at, [IDENTITY], [])

    def connector(self, selector=None, enabled=False, **extra):
        return dict(resource_id='connector-copper', subject_selector=selector or IDENTITY['user_id'],
                    enabled=enabled, **extra)

    def snapshot(self, row, captured=NOW, tables=('customer_data_primary', 'customer_data_failover_replica')):
        return self.file('selector-proof', captured,
                         [('connector_configurations', 'integration_service', row)], tables=tables)

    def test_exact_stable_selector_two_copies_produces_cited_disabled_check(self):
        result, detail = predict(REQUEST, self.inputs([self.snapshot(self.connector())]))
        self.assertEqual(result.deletion_status, 'COMPLETE')
        self.assertEqual([(s.resource_id, s.operation, s.evidence_id) for s in result.steps],
                         [('connector-copper', 'VERIFY_DATA_FLOW_DISABLED', 'selector-proof')])
        self.assertTrue(detail['prediction']['status_uncertain'])
        self.assertEqual(len(detail['latest_copy_states']), 2)

    def test_unknown_selector_never_assigns_subject(self):
        result, _ = predict(REQUEST, self.inputs([self.snapshot(self.connector('unknown-subject'))]))
        self.assertEqual(result.steps, ())

    def test_stable_selector_is_exact_not_normalized_or_substring(self):
        for value in ('SUBJECT-K', ' subject-k ', 'subject-k-suffix'):
            with self.subTest(value=value):
                self.assertFalse(matches(self.connector(value), self.subject))

    def test_email_selector_remains_supported(self):
        self.assertTrue(matches(self.connector(IDENTITY['email'].upper()), self.subject))

    def test_selector_conflicting_with_stable_owner_rejects(self):
        with self.assertRaisesRegex(AuditError, 'conflicting stable'):
            predict(REQUEST, self.inputs([self.snapshot(self.connector(customer_reference='other-subject'))]))

    def test_unknown_selector_conflicting_with_known_owner_rejects(self):
        with self.assertRaisesRegex(AuditError, 'conflicting stable'):
            matches(self.connector('other-subject', user_id=IDENTITY['user_id']), self.subject)

    def test_nested_selector_conflicting_with_enclosing_owner_rejects(self):
        with self.assertRaisesRegex(AuditError, 'Nested identity conflicts'):
            matches(dict(user_id='other-subject', payload=self.connector()), self.subject)

    def test_future_capture_emits_no_check(self):
        result, _ = predict(REQUEST, self.inputs([self.snapshot(self.connector(), FUTURE)]))
        self.assertEqual(result.steps, ())

    def test_enabled_flow_is_not_verified_disabled(self):
        result, _ = predict(REQUEST, self.inputs([self.snapshot(self.connector(enabled=True))]))
        self.assertEqual(result.deletion_status, 'INCOMPLETE')
        self.assertEqual([s.operation for s in result.steps],
                         ['REPORT_ACTIVE_DATA_FLOW', 'DISABLE_DATA_FLOW', 'VERIFY_DATA_FLOW_DISABLED'])
        self.assertEqual([s.evidence_id for s in result.steps], ['selector-proof', '', ''])

    def test_selector_reassignment_in_later_snapshot_rejects(self):
        old = self.file('old-selector', EARLY,
                        [('connector_configurations', 'integration_service', self.connector())])
        new = self.snapshot(self.connector('other-subject'))
        with self.assertRaisesRegex(AuditError, 'reassigned'):
            predict(REQUEST, self.inputs([old, new]))

    def test_disagreeing_replica_never_proves_disabled(self):
        old = self.file('enabled-copy', NOW,
                        [('connector_configurations', 'integration_service', self.connector(enabled=True))],
                        tables=('customer_data_primary',))
        new = self.file('disabled-copy', NOW,
                        [('connector_configurations', 'integration_service', self.connector())],
                        tables=('customer_data_failover_replica',))
        result, _ = predict(REQUEST, self.inputs([old, new]))
        self.assertEqual(result.deletion_status, 'INCOMPLETE')
        self.assertTrue(all(s.evidence_id == '' for s in result.steps if s.phase == 'VERIFICATION'))
