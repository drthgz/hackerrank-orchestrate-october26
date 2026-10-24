"""Best-effort has the same evidence contract, but isolates unresolved resources."""
import json
import tempfile
import unittest
from pathlib import Path
from dataclasses import replace
from unittest.mock import patch
from test_structured import IDENTITY, REQUEST, RULES, EARLY, NOW, FUTURE, profile
from audit.competition import competition_intent
from audit.models import AuditError, EvidenceFile
from audit.inputs import Inputs
from audit.pipeline import audit
from audit.reviewed_images import review
from audit.identity import resolve_subject
from audit.reviewed_images import catalog_attachment_observations


class CompetitionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def inputs(self, records):
        p=self.root/'fixture.json'
        p.write_text(json.dumps(dict(exported_at=NOW, snapshots=records)))
        file=EvidenceFile('fixture',p,'independent-fixture',REQUEST.audit_at)
        return Inputs((REQUEST,),[IDENTITY],[],[],RULES,(file,))

    def snap(self, collection, records):
        return dict(collection=collection,captured_at=NOW,records=records)

    def test_partial_retention_failure_preserves_grounded_violation(self):
        inputs=self.inputs([self.snap('customer_profiles',[profile()]), self.snap('security_audit_events',[
            dict(resource_id='ledger-ochre',subject_reference=IDENTITY['user_id'])])])
        with self.assertRaisesRegex(AuditError,'retention'):audit(REQUEST,inputs)
        result, detail=audit(REQUEST,inputs,mode='best-effort')
        self.assertEqual(result.deletion_status,'INCOMPLETE')
        self.assertEqual(len(result.steps),3)
        self.assertEqual(detail['omissions'][0]['resource_id'],'ledger-ochre')
        self.assertFalse(detail['plan_exhaustive'])

    def test_unknown_retention_alone_cannot_become_incomplete_or_complete(self):
        inputs=self.inputs([self.snap('security_audit_events',[
            dict(resource_id='ledger-ochre',subject_reference=IDENTITY['user_id'])])])
        with self.assertRaises(AuditError):audit(REQUEST,inputs,mode='best-effort')

    def test_no_proof_no_guessed_row(self):
        with self.assertRaises(AuditError):audit(REQUEST,self.inputs([]),mode='best-effort')

    def test_clear_authorization_with_ancillary_conditions(self):
        self.assertEqual(competition_intent('Please begin the deletion process for the account using my email. Contact me if you need identity verification.'),'DELETION')
        self.assertEqual(competition_intent('Solicito a exclusão permanente da conta associada a este e-mail.'),'DELETION')
        self.assertEqual(competition_intent('이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다.'),'DELETION')

    def test_preservation_and_conflict(self):
        self.assertEqual(competition_intent('Please change my email. I want to continue using the service.'),'NON_DELETION')
        with self.assertRaises(AuditError):competition_intent('Please permanently delete the account. Do not delete my account.')
        with self.assertRaises(AuditError):competition_intent('Maybe delete my account only if I stop using it.')

    def test_unknown_image_has_no_cached_facts(self):
        p=self.root/'unreviewed.png';p.write_bytes(b'new image content')
        self.assertIsNone(review(EvidenceFile('new',p,'unknown',REQUEST.audit_at)))

    def test_metadata_event_does_not_invalidate_state(self):
        inputs=self.inputs([self.snap('customer_profiles',[profile()])])
        # Same-cutoff catalog claims change identity metadata, not database state.
        inputs=replace(inputs,activity=[dict(activity_id='catalog-fixture',event_time=NOW,resource_id='profile-blue',
                         event_type='LINK_RESOURCE_IDENTITY',details='Catalog metadata',source_system='catalog',target_system='account_service')])
        result,_=audit(REQUEST,inputs,mode='best-effort')
        self.assertEqual(result.deletion_status,'INCOMPLETE')

    def catalog_fixture(self, event_time=NOW, filename='parcel-note.pdf'):
        p = self.root / 'listing.png'
        p.write_bytes(b'fixture-image')
        file = EvidenceFile('listing', p, 'object-storage', REQUEST.audit_at)
        event = dict(activity_id='ownership', event_time=event_time, event_type='LINK_RESOURCE_IDENTITY',
                     target_system='object_storage', resource_id='upload-ochre',
                     details=f'Attachment catalog confirmed upload-ochre ({filename}) belongs only to {IDENTITY["email"]} and {IDENTITY["user_id"]}; no other subject is linked.')
        subject = resolve_subject(REQUEST.email, REQUEST.audit_at, [IDENTITY], [])
        return file, event, subject

    def test_catalog_ownership_joins_visible_attachment(self):
        file, event, subject = self.catalog_fixture()
        with patch('audit.reviewed_images.review', return_value=dict(
                attachment_folder='support-attachments', filenames=['parcel-note.pdf'])):
            o, = catalog_attachment_observations(file, subject, [event], REQUEST.audit_at)
        self.assertEqual((o.resource_id, o.system_id, o.evidence_id), ('upload-ochre', 'object_storage', 'listing'))
        self.assertTrue(o.facts['belongs_only_to_subject'])
        self.assertEqual(o.facts['_lineage_evidence'], 'ownership')

    def test_catalog_future_metadata_cannot_join_attachment(self):
        file, event, subject = self.catalog_fixture(event_time=FUTURE)
        with patch('audit.reviewed_images.review', return_value=dict(
                attachment_folder='support-attachments', filenames=['parcel-note.pdf'])):
            self.assertEqual(catalog_attachment_observations(file, subject, [event], REQUEST.audit_at), ())

    def test_catalog_does_not_prove_unlisted_attachment_presence(self):
        file, event, subject = self.catalog_fixture(filename='unlisted.pdf')
        with patch('audit.reviewed_images.review', return_value=dict(
                attachment_folder='support-attachments', filenames=['parcel-note.pdf'])):
            self.assertEqual(catalog_attachment_observations(file, subject, [event], REQUEST.audit_at), ())
