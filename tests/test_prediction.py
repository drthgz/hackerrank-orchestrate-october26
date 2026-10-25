"""Independent fixtures for a prediction layer that never relaxes the audit API."""
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_structured import IDENTITY, REQUEST, RULES, NOW, FUTURE, profile
from audit.inputs import Inputs
from audit.models import AuditError, EvidenceFile, Result, Step, timestamp
from audit.pipeline import audit
from audit.prediction import predict, validate_prediction, write_predictions


class PredictionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def inputs(self, snapshots=()):
        path = self.root / 'fixture.json'
        path.write_text(json.dumps(dict(exported_at=NOW, snapshots=snapshots)))
        file = EvidenceFile('independent-proof', path, 'fixture', REQUEST.audit_at)
        return Inputs((REQUEST,), [IDENTITY], [], [], RULES, (file,))

    def snapshot(self, collection, rows):
        return dict(collection=collection, captured_at=NOW, records=rows)

    def test_existing_best_effort_steps_are_identical(self):
        inputs = self.inputs([self.snapshot('customer_profiles', [profile()])])
        baseline, _ = audit(REQUEST, inputs, mode='best-effort')
        result, detail = predict(REQUEST, inputs)
        self.assertEqual(result, baseline)
        self.assertFalse(detail['prediction']['status_uncertain'])
        self.assertFalse(detail['prediction']['verified_compliance_decision'])

    def test_empty_evidence_is_uncertain_prediction_and_audit_still_rejects(self):
        inputs = self.inputs()
        result, detail = predict(REQUEST, inputs)
        self.assertEqual((result.deletion_status, result.steps), ('COMPLETE', ()))
        self.assertTrue(detail['prediction']['status_uncertain'])
        self.assertEqual(detail['prediction']['confidence'], 'low')
        validate_prediction(result, REQUEST, inputs.citation_times())
        with self.assertRaises(AuditError):
            audit(REQUEST, inputs, mode='best-effort')
        with self.assertRaises(AuditError):
            audit(REQUEST, inputs, mode='strict')

    def test_exposed_tombstone_preserves_plan_without_inventing_retained_link(self):
        row = dict(resource_id='tombstone-ochre', subject_reference=IDENTITY['user_id'],
                   account_status='DELETED', name=IDENTITY['name'], email=IDENTITY['email'],
                   phone=IDENTITY['phone'], email_hash=IDENTITY['email_hash'])
        inputs = self.inputs([self.snapshot('deleted_customer_references', [row])])
        result, detail = predict(REQUEST, inputs)
        self.assertEqual(result.deletion_status, 'INCOMPLETE')
        self.assertEqual([s.operation for s in result.steps],
                         ['REPORT_EXPOSED_PII', 'REDACT_RECORD', 'VERIFY_RECORD_REDACTED'])
        self.assertFalse(detail['prediction']['status_uncertain'])
        self.assertFalse(detail['prediction']['plan_complete'])
        self.assertTrue(any('retained-record relationship' in x['reason'] for x in detail['omissions']))

    def test_supported_retention_verification_survives_missing_profile_proof(self):
        row = dict(resource_id='ledger-mauve', subject_reference=IDENTITY['user_id'], retention_until=FUTURE)
        inputs = self.inputs([self.snapshot('security_audit_events', [row])])
        result, detail = predict(REQUEST, inputs)
        self.assertEqual(result.deletion_status, 'COMPLETE')
        self.assertEqual([(s.resource_id, s.operation, s.evidence_id) for s in result.steps],
                         [('ledger-mauve', 'VERIFY_RECORD_PRESENT', 'independent-proof')])
        self.assertTrue(detail['prediction']['status_uncertain'])
        self.assertIn('profile-absence', detail['audit_blocker'])

    def test_missing_retention_does_not_create_verification_or_deadline(self):
        row = dict(resource_id='ledger-mauve', subject_reference=IDENTITY['user_id'])
        result, detail = predict(REQUEST, self.inputs([self.snapshot('security_audit_events', [row])]))
        self.assertEqual(result.steps, ())
        self.assertTrue(detail['prediction']['status_uncertain'])
        self.assertTrue(any('retention' in reason for reason in detail['prediction']['missing_proof']))

    def test_reported_status_and_case_identifier_do_not_drive_fallback(self):
        inputs = self.inputs()
        first, _ = predict(REQUEST, inputs)
        other = replace(REQUEST, case_id='unrelated-case-label', reported_status='NOT_STARTED')
        second, _ = predict(other, inputs)
        self.assertEqual((first.deletion_status, first.steps), (second.deletion_status, second.steps))

    def test_invalid_inputs_are_not_swallowed_as_predictions(self):
        with patch('audit.prediction.audit', side_effect=AuditError('malformed SQL')):
            with self.assertRaisesRegex(AuditError, 'malformed SQL'):
                predict(REQUEST, self.inputs())

    def test_prediction_cannot_invent_or_use_future_citation(self):
        for citation in ('fabricated-proof', 'future-proof'):
            step = Step(1, 'VERIFICATION', 'account_service', 'known-profile', 'VERIFY_RECORD_ABSENT', 'ABSENT', citation)
            with self.subTest(citation=citation):
                with self.assertRaises(AuditError):
                    validate_prediction(Result(REQUEST.case_id, 'COMPLETE', (step,)), REQUEST,
                                        {'future-proof': timestamp(FUTURE)})

    def test_writer_has_only_official_columns_and_rejects_duplicate_cases(self):
        inputs = self.inputs()
        result, _ = predict(REQUEST, inputs)
        path = self.root / 'predictions.csv'
        write_predictions(path, [result], [REQUEST], inputs.citation_times())
        self.assertEqual(path.read_text().splitlines()[0], 'case_id,deletion_status,steps_json')
        self.assertNotIn('confidence', path.read_text())
        with self.assertRaises(AuditError):
            write_predictions(path, [result, result], [REQUEST], inputs.citation_times())


if __name__ == '__main__':
    unittest.main()
