"""Independent PDF text fixtures plus an actual minimal selectable-text PDF.

No participant labels, IDs, dates or private data are used in these tests.
"""
import tempfile
import unittest
from pathlib import Path
from dataclasses import replace
from unittest.mock import patch

from test_structured import EARLY, NOW, FUTURE, IDENTITY, REQUEST, RULES
from audit.models import EvidenceFile, timestamp, AuditError
from audit.pdf_evidence import read_pdf, supplement_retention, _pages
from audit.evidence import extract_observations
from audit.identity import resolve_subject
from audit.policy import assess_policy

JOURNAL = '''COMPLIANCE JOURNAL - SIGNED RECORD EXTRACT
Event reference ledger-azure
subject reference subject-k
issued 01 Feb 2026 00     00 UTC
recorded 01 Jan 2026 00   00 UTC
retain until 01 Mar 2026 00  00 UTC
'''
ATTACHMENT = '''DELIVERY ADDRESS CORRECTION REQUEST
Support reference CS-test / upload-violet
Detail current@example.invalid
submitted 01 Jan 2026 00 00 UTC
\fContinued - Attachment properties
file customer-change.pdf
uploader customer
captured 01 Feb 2026 00 00 UTC
'''
REGISTER = '''DISPUTED ORDERS AND TAX RECORDS REGISTER
ORD-EXAMPLE | subject-k | Card dispute | 01 Jan 2026 | USD 8 | Retain until 01 Mar 2026 | ZZ
'''


class PDFTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'document.pdf'
        self.path.write_bytes(b'fixture')
        self.file = EvidenceFile('fixture-pdf', self.path, 'fixture-origin', timestamp(NOW))
        self.subject = resolve_subject(REQUEST.email, REQUEST.audit_at, [IDENTITY], [])

    def document(self, text, file=None):
        with patch('audit.pdf_evidence._pages', return_value=tuple(text.split('\f'))):
            return read_pdf(file or self.file)

    def test_security_retention_and_page_provenance(self):
        doc = self.document(JOURNAL)
        o, = doc.observations
        self.assertEqual((o.resource_id, o.evidence_id, o.facts['_pdf_pages']), ('ledger-azure', 'fixture-pdf', (1,)))
        self.assertEqual(o.facts['_source_origin'], 'fixture-origin')
        self.assertEqual(o.observed_at, timestamp(NOW))
        self.assertEqual(o.available_at, timestamp(NOW))
        self.assertTrue(assess_policy([o], RULES, timestamp(NOW))[0].compliant)
        with self.assertRaises(AuditError):
            assess_policy([o], RULES, timestamp(FUTURE).replace(day=2))

    def test_attachment_subject_ownership_and_two_pages(self):
        doc = self.document(ATTACHMENT)
        o, = doc.observations
        self.assertEqual(o.facts['_pdf_pages'], (1, 2))
        self.assertTrue(o.facts['belongs_only_to_subject'])
        with patch('audit.pdf_evidence._pages', return_value=tuple(ATTACHMENT.split('\f'))):
            selected = extract_observations([self.file], self.subject, timestamp(NOW))
        self.assertEqual(len(selected), 1)
        decision, = assess_policy(selected, RULES, timestamp(NOW))
        self.assertEqual((decision.action, decision.compliant), ('DELETE', False))

    def test_other_subject_not_correlated(self):
        with patch('audit.pdf_evidence._pages', return_value=(JOURNAL.replace('subject-k', 'other-person'),)):
            self.assertEqual(extract_observations([self.file], self.subject, timestamp(NOW)), ())

    def test_future_capture_not_read_even_for_old_embedded_event(self):
        with patch('audit.pdf_evidence._pages', side_effect=AssertionError('future extraction')):
            self.assertEqual(extract_observations([replace(self.file, captured_at=timestamp(FUTURE))], self.subject, timestamp(NOW)), ())

    def test_observation_after_capture_rejected(self):
        with self.assertRaisesRegex(AuditError, 'later than capture'):
            self.document(JOURNAL.replace('issued 01 Feb', 'issued 02 Feb'))

    def test_missing_and_ambiguous_attachment_links_rejected(self):
        for text in [ATTACHMENT.replace(' / upload-violet', ''), ATTACHMENT.replace('uploader customer', 'uploader agent'), ATTACHMENT + '\nother@example.invalid']:
            with self.subTest(text=text), self.assertRaises(AuditError):
                self.document(text)

    def test_unknown_document_does_not_establish_retention(self):
        doc = self.document('NORTHSTAR SHOP - CUSTOMER STATEMENT\nsubject-k\norder ORD-EXAMPLE')
        self.assertFalse(doc.understood)
        self.assertEqual((doc.retention, doc.observations), ((), ()))

    def test_register_requires_exact_subject_and_order_and_preserves_resource(self):
        from audit.evidence import observation
        doc = self.document(REGISTER)
        self.assertFalse(doc.observations)
        base = observation(self.file, 'legal_service', 'hold-amber', 'LEGAL_HOLD_RECORD',
                           dict(subject_reference='subject-k', order_reference='ORD-EXAMPLE'), timestamp(NOW))
        o, = supplement_retention([base], [doc], self.subject, timestamp(NOW))
        self.assertEqual(o.resource_id, 'hold-amber')
        self.assertTrue(assess_policy([o], RULES, timestamp(NOW))[0].compliant)
        self.assertEqual(o.facts['_policy_evidence']['retained_until'], 'fixture-pdf')
        wrong = replace(base, facts=dict(base.facts, order_reference='ORD-OTHER'))
        self.assertNotIn('retained_until', supplement_retention([wrong], [doc], self.subject, timestamp(NOW))[0].facts)
        other = replace(self.subject, user_id='other-person')
        self.assertNotIn('retained_until', supplement_retention([base], [doc], other, timestamp(NOW))[0].facts)

    def test_register_does_not_override_inactive_hold(self):
        from audit.evidence import observation
        base = observation(self.file, 'legal_service', 'hold-amber', 'LEGAL_HOLD_RECORD',
                           dict(order_reference='ORD-EXAMPLE', legal_hold_active=False), timestamp(NOW))
        o, = supplement_retention([base], [self.document(REGISTER)], self.subject, timestamp(NOW))
        self.assertFalse(o.facts['legal_hold_active'])

    def test_complete_journal_and_scoped_profile_absence(self):
        from audit.inputs import Inputs
        from audit.pipeline import audit
        from test_structured import StructuredTests, profile
        # Independent SQL fixtures supply prior lineage and current absence.
        fixture = StructuredTests(); fixture.setUp()
        try:
            old = fixture.file('prior', EARLY, [('customer_profiles', 'account_service', profile())])
            new = fixture.file('current', NOW, [])
            inputs = Inputs((REQUEST,), [IDENTITY], [], [], RULES, (old, new, self.file))
            with patch('audit.pdf_evidence._pages', return_value=(JOURNAL,)):
                result, _ = audit(REQUEST, inputs)
            self.assertEqual(result.deletion_status, 'COMPLETE')
            self.assertEqual([(s.resource_id, s.operation, s.evidence_id) for s in result.steps],
                             [('profile-blue', 'VERIFY_RECORD_ABSENT', 'current'),
                              ('ledger-azure', 'VERIFY_RECORD_PRESENT', 'fixture-pdf')])
        finally:
            fixture.doCleanups()

    def test_attachment_plan_includes_existing_absence_verification(self):
        from audit.inputs import Inputs
        from audit.pipeline import audit
        import json
        path = self.path.with_suffix('.json')
        path.write_text(json.dumps(dict(records=[dict(recorded_at=NOW, system='account_service',
            resource_id='profile-peach', record_type='USER_PROFILE', result='NOT_FOUND',
            subject_reference=IDENTITY['email'])])))
        file = EvidenceFile('profile-proof', path, 'fixture-origin', timestamp(NOW))
        inputs = Inputs((REQUEST,), [IDENTITY], [], [], RULES, (self.file, file))
        with patch('audit.pdf_evidence._pages', return_value=tuple(ATTACHMENT.split('\f'))):
            result, _ = audit(REQUEST, inputs)
        self.assertEqual(result.deletion_status, 'INCOMPLETE')
        self.assertEqual([(s.phase, s.resource_id) for s in result.steps],
                         [('FINDING', 'upload-violet'), ('REMEDIATION', 'upload-violet'),
                          ('VERIFICATION', 'profile-peach'), ('VERIFICATION', 'upload-violet')])
        self.assertEqual(result.steps[0].evidence_id, 'fixture-pdf')

    def test_real_selectable_pdf_poppler(self):
        # Minimal PDF generated directly: tests extraction without extra packages.
        stream = b'BT /F1 12 Tf 20 80 Td (Selectable fixture text) Tj ET'
        objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
                   b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 100] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
                   b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>', b'<< /Length ' + str(len(stream)).encode() + b' >>\nstream\n' + stream + b'\nendstream']
        data = b'%PDF-1.4\n'; offsets = [0]
        for i, obj in enumerate(objects, 1):
            offsets.append(len(data)); data += str(i).encode() + b' 0 obj\n' + obj + b'\nendobj\n'
        offset = len(data)
        data += b'xref\n0 6\n0000000000 65535 f \n' + b''.join(f'{n:010d} 00000 n \n'.encode() for n in offsets[1:])
        data += f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{offset}\n%%EOF\n'.encode()
        self.path.write_bytes(data)
        stat = self.path.stat()
        self.assertIn('Selectable fixture text', _pages(self.path, stat.st_size, stat.st_mtime_ns)[0])
