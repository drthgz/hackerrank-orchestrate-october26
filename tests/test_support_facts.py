"""Counterexamples for support context, ownership and complete-text scope."""
import json
import unittest
from dataclasses import replace
from unittest.mock import patch

import test_evidence as fixtures
from test_structured import IDENTITY, NOW, EARLY, FUTURE, REQUEST, RULES
from audit.evidence import enrich
from audit.models import AuditError, timestamp
from audit.policy import assess_policy
from audit.reviewed_images import read_image
from audit.sql_evidence import extract_observations


class SupportFactTests(unittest.TestCase):
    # Reuse fixture helpers without importing their tests into this suite.
    setUp = fixtures.EvidenceTests.setUp
    file = fixtures.EvidenceTests.file
    bundle = fixtures.EvidenceTests.bundle
    snapshot = fixtures.EvidenceTests.snapshot
    observations = fixtures.EvidenceTests.observations
    line = fixtures.EvidenceTests.line
    def row(self, **changes):
        return dict(dict(resource_id='thread-copper', subject_reference=IDENTITY['user_id'],
                         requester_name=None, requester_email=None, requester_phone=None), **changes)

    def support(self, **changes):
        return self.bundle(self.snapshot('support_conversations', [self.row(**changes)]))

    def test_category_or_identifier_does_not_prove_shared_context(self):
        for changes in ({}, dict(requester_email=IDENTITY['email']), dict(message_excerpt='agent order delivery')):
            o, = self.observations(self.support(**changes))
            self.assertNotIn('shared_context', o.facts)
            with self.assertRaisesRegex(AuditError, 'shared_context'):
                assess_policy([o], RULES, REQUEST.audit_at)

    def test_partial_exposure_is_not_complete_scan(self):
        o, = self.observations(self.support(shared_context=True, message_excerpt=IDENTITY['email']))
        self.assertNotIn('text_scan_complete', o.facts)
        self.assertFalse(assess_policy([o], RULES, REQUEST.audit_at)[0].compliant)

    def test_delivery_conversation_proves_context_but_not_full_scan(self):
        for text in ('Customer supplied contact details for a delivery query.',
                     'Customer asked support to correct delivery details.'):
            with self.subTest(text=text):
                o, = self.observations(self.support(message_excerpt=text, requester_email=IDENTITY['email']))
                self.assertIs(o.facts['shared_context'], True)
                self.assertNotIn('text_scan_complete', o.facts)
                self.assertFalse(assess_policy([o], RULES, REQUEST.audit_at)[0].compliant)

    def test_clean_excerpt_needs_explicit_complete_scan(self):
        for complete in (None, False, True):
            changes = dict(shared_context=True, message_excerpt='[REDACTED]', text_has_subject_identifiers=False)
            if complete is not None:
                changes['text_scan_complete'] = complete
            o, = self.observations(self.support(**changes))
            if complete is True:
                self.assertTrue(assess_policy([o], RULES, REQUEST.audit_at)[0].compliant)
            else:
                with self.assertRaises(AuditError):
                    assess_policy([o], RULES, REQUEST.audit_at)

    def test_full_text_provenance_and_explicit_incomplete_scope(self):
        for flag in (None, False):
            changes = dict(shared_context=True, message_text='[REDACTED]')
            if flag is not None:
                changes['text_scan_complete'] = flag
            o, = self.observations(self.support(**changes))
            p = o.facts['_support_fact_provenance']['text_scan_complete']
            self.assertIs(p['value'], flag is None)
            self.assertEqual((p['evidence_id'], p['source']), ('bundle', 'support_conversations'))
            self.assertEqual(p['available_at'], REQUEST.audit_at.isoformat())

    def test_subject_match_does_not_prove_exclusive_attachment_ownership(self):
        for explicit in (None, False, True):
            row = self.row(uploaded_by=IDENTITY['email'])
            if explicit is not None:
                row['belongs_only_to_subject'] = explicit
            o, = self.observations(self.bundle(self.snapshot('ticket_attachments', [row])))
            if explicit is True:
                self.assertEqual(assess_policy([o], RULES, REQUEST.audit_at)[0].action, 'DELETE')
            else:
                with self.assertRaises(AuditError):
                    assess_policy([o], RULES, REQUEST.audit_at)

    def test_invalid_predicate_types_remain_unresolved(self):
        for value in ('true', 'false', 'yes', 2, None):
            o, = self.observations(self.support(shared_context=value, message_text='my order'))
            self.assertNotIn('shared_context', o.facts['_support_fact_provenance'])
            with self.assertRaises(AuditError):
                assess_policy([o], RULES, REQUEST.audit_at)

    def test_sql_predicates_are_typed_and_cite_table(self):
        row = self.row(shared_context=1, text_scan_complete=1, text_has_subject_identifiers=False)
        payload = json.dumps(row).replace("'", "''")
        sql = f'''-- Captured at: {NOW}
CREATE TABLE customer_data_primary(resource_id TEXT, origin_system TEXT, collection_name TEXT, record_json TEXT, updated_at TEXT);
INSERT INTO customer_data_primary VALUES ('thread-copper','support_platform','support_conversations','{payload}','{NOW}');'''
        o, = self.observations(self.file('support-db', sql, suffix='.sql'))
        self.assertIs(o.facts['shared_context'], True)
        self.assertEqual(o.facts['_support_fact_provenance']['shared_context']['source'], 'customer_data_primary')
        self.assertTrue(assess_policy([o], RULES, REQUEST.audit_at)[0].compliant)

    def test_log_predicates_cite_line_and_event(self):
        log = self.line('message_read', 'resource_id=thread-copper subject_ref=subject-k shared_context=true '
                        'text_scan_complete=false requester_email=current@example.invalid', service='support_platform')
        o, = self.observations(self.file('support-log', log, suffix='.log'))
        p = o.facts['_support_fact_provenance']
        self.assertEqual(p['shared_context']['source'], 'log:1:message_read')
        self.assertIs(p['text_scan_complete']['value'], False)
        self.assertFalse(assess_policy([o], RULES, REQUEST.audit_at)[0].compliant)

    def test_image_transcription_provenance_keeps_reviewed_region(self):
        file = self.file('screen', 'fixture', suffix='.png')
        with patch('audit.reviewed_images.review', return_value=dict(rows=[
                ('support_platform', 'thread-copper', 'SUPPORT_MESSAGE', self.row(shared_context=True))])):
            o, = read_image(file)
        self.assertEqual(o.facts['_support_fact_provenance']['shared_context']['source'], 'image:reviewed-fields')
        self.assertIn('_image_region', o.facts)

    def test_scope_never_propagates_between_observations_or_copies(self):
        old, = self.observations(self.support(message_excerpt='[REDACTED]'))
        newer = replace(old, observed_at=timestamp(FUTURE), facts=dict(old.facts, shared_context=True))
        # Future or other-copy context must not backfill a historical read.
        from audit.support_facts import extracted
        newer = replace(newer, facts=extracted(newer.facts, newer.category, 'later', 'fixture', newer.observed_at, newer.available_at))
        first, _ = enrich([old, newer], self.subject, timestamp(FUTURE))
        self.assertNotIn('shared_context', first.facts)
        replica = replace(newer, copy_id='other-copy', observed_at=old.observed_at)
        first, _ = enrich([old, replica], self.subject, timestamp(FUTURE))
        self.assertNotIn('shared_context', first.facts)

