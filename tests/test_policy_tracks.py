"""Facts survive unresolved policy; no speculative CSV instructions result."""
import copy
import unittest
from dataclasses import replace

from test_structured import NOW, EARLY, FUTURE, REQUEST, RULES
from audit.models import Observation, timestamp, Result, Step, AuditError
from audit.contract import validate_result
from evaluation.policy_tracks import security_track, support_track, tracks


class PolicyTrackTests(unittest.TestCase):
    def observation(self, category='SECURITY_AUDIT_LOG', **facts):
        return Observation('service-fixture', 'resource-copper', category, 'copy-violet', True,
            timestamp(NOW), timestamp(EARLY), 'witness-ochre', timestamp(NOW), 'fixture-readback',
            (('subject_reference', 'subject-k'),), facts, 'subject-k')

    def security(self, o):
        return security_track([o], RULES, REQUEST.audit_at)[0]

    def support(self, o):
        return support_track([o], RULES, REQUEST.audit_at)[0]

    def test_security_presence_is_distinct_from_retention(self):
        row = self.security(self.observation(integrity_seal='valid'))
        self.assertTrue(row['observed_facts']['present']['value'])
        self.assertNotIn('retention_until', row['observed_facts'])
        self.assertFalse(row['policy']['established'])
        self.assertEqual(row['submission_changes'], [])

    def test_security_supplied_deadline_supports_retained_presence(self):
        row = self.security(self.observation(retention_until=FUTURE))
        self.assertTrue(row['policy']['established'])
        self.assertEqual(row['policy']['verify_operation'], 'VERIFY_RECORD_PRESENT')
        self.assertEqual(row['observed_facts']['retention_until']['provenance']['evidence_id'], 'witness-ochre')

    def test_expired_invalid_or_unanchored_duration_is_unresolved(self):
        for facts in (dict(retention_until=EARLY), dict(retention_until='invalid'), dict(retention_days=90)):
            with self.subTest(facts=facts):
                row = self.security(self.observation(**facts))
                self.assertFalse(row['policy']['established'])
                self.assertIsNone(row['policy']['verify_operation'])

    def test_missing_record_cannot_be_verified_present(self):
        row = self.security(replace(self.observation(retention_until=FUTURE), present=False))
        self.assertFalse(row['observed_facts']['present']['value'])
        self.assertFalse(row['policy']['established'])

    def test_security_and_support_reject_late_capture_even_for_old_readback(self):
        for category in ('SECURITY_AUDIT_LOG', 'SUPPORT_MESSAGE'):
            o = replace(self.observation(category, retention_until=FUTURE), available_at=timestamp(FUTURE))
            row = self.security(o) if category == 'SECURITY_AUDIT_LOG' else self.support(o)
            self.assertFalse(row['admissible'])
            self.assertEqual(row['observed_facts'], {})

    def test_future_observation_conflicting_times_and_missing_lineage_rejected(self):
        o = self.observation(retention_until=FUTURE)
        for other in (replace(o, observed_at=timestamp(FUTURE)), replace(o, updated_at=timestamp(FUTURE)),
                      replace(o, subject_id=''), replace(o, available_at=timestamp(EARLY))):
            with self.subTest(other=other):
                self.assertFalse(self.security(other)['admissible'])

    def test_exposure_survives_without_inventing_context_or_remedy(self):
        row = self.support(self.observation('SUPPORT_MESSAGE', requester_email='subject@example.invalid'))
        self.assertTrue(row['observed_facts']['identifier_exposure']['value'])
        self.assertNotIn('shared_context', row['observed_facts'])
        self.assertNotIn('text_scan_complete', row['observed_facts'])
        self.assertFalse(row['policy']['established'])
        self.assertIsNone(row['policy']['action'])
        self.assertEqual(row['submission_changes'], [])

    def test_shared_exposed_support_has_supported_redaction(self):
        row = self.support(self.observation('SUPPORT_MESSAGE', shared_context=True, identifier_exposure=True))
        self.assertEqual((row['policy']['action'], row['policy']['compliant']), ('REDACT', False))

    def test_category_and_subject_do_not_prove_shared_context(self):
        row = self.support(self.observation('SUPPORT_MESSAGE', subject_reference='subject-k'))
        self.assertNotIn('shared_context', row['observed_facts'])
        self.assertFalse(row['policy']['established'])

    def test_attachment_presence_does_not_imply_sole_ownership(self):
        row = self.support(self.observation('SUPPORT_ATTACHMENT', owner_email='subject@example.invalid'))
        self.assertTrue(row['observed_facts']['present']['value'])
        self.assertNotIn('belongs_only_to_subject', row['observed_facts'])
        self.assertFalse(row['policy']['established'])

    def test_only_explicit_exclusive_attachment_supports_deletion(self):
        for exclusive in (True, False, 'true'):
            row = self.support(self.observation('SUPPORT_ATTACHMENT', belongs_only_to_subject=exclusive))
            self.assertEqual(row['policy']['established'], exclusive is True)
            if exclusive is True:
                self.assertEqual(row['policy']['action'], 'DELETE')

    def test_clean_excerpt_does_not_establish_clean_full_text(self):
        row = self.support(self.observation('SUPPORT_MESSAGE', shared_context=True,
            requester_name=None, requester_email=None, requester_phone=None,
            message_excerpt='[REDACTED]', text_has_subject_identifiers=False))
        self.assertNotIn('identifier_exposure', row['observed_facts'])
        self.assertNotIn('text_scan_complete', row['observed_facts'])
        self.assertFalse(row['policy']['established'])
        self.assertEqual(row['observed_facts']['text_has_subject_identifiers']['scope'], 'message_excerpt')

    def test_full_scoped_clean_scan_supports_redaction_check(self):
        row = self.support(self.observation('SUPPORT_MESSAGE', shared_context=True,
            requester_name=None, requester_email=None, requester_phone=None,
            text_scan_complete=True, text_has_subject_identifiers=False))
        self.assertTrue(row['policy']['compliant'])
        self.assertEqual(row['policy']['verify_operation'], 'VERIFY_RECORD_REDACTED')

    def test_presence_in_other_track_cannot_resolve_retention(self):
        observations = [self.observation(), self.observation('SUPPORT_MESSAGE', shared_context=True, identifier_exposure=True)]
        saved = copy.deepcopy(observations)
        combined = tracks(observations, RULES, REQUEST.audit_at, ['support', 'security'])
        self.assertEqual(combined['security'], security_track(observations, RULES, REQUEST.audit_at))
        self.assertEqual(combined['support'], support_track(observations, RULES, REQUEST.audit_at))
        self.assertFalse(combined['security'][0]['policy']['established'])
        self.assertEqual(observations, saved)

    def test_unsupported_finding_without_remediation_fails_stronger_validator(self):
        finding = Step(1, 'FINDING', 'example-service', 'example-record', 'REPORT_EXPOSED_PII', 'PRESENT', 'witness')
        with self.assertRaisesRegex(AuditError, 'all three phases'):
            validate_result(Result(REQUEST.case_id, 'INCOMPLETE', (finding,)), REQUEST, {'witness': REQUEST.audit_at})

    def test_unknown_track_does_not_silently_run(self):
        with self.assertRaises(ValueError):
            tracks([], RULES, REQUEST.audit_at, ['unsupported'])
