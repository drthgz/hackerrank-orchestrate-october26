"""Generalized intent examples: no public IDs, identities or expected plans."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
from audit.intent import classify_intent
from audit.models import AuditError


class IntentTests(unittest.TestCase):
    def test_deletion_and_residual_requests(self):
        for text in [
            'Erase my account forever.', 'Could you remove that search result?',
            'Please delete the export file.', 'Please remove records under both email addresses.',
            'I would like my account to be closed.', 'I no longer need this account. Please remove my name and contact details.',
            'Please delete my account. Security records can stay if policy requires them.',
            'Close my account. You may retain backups if required, but they must not restore my profile.',
            'Please delete my account. Please contact me if you need information to verify the request.',
            'Can you verify that my account was deleted?',
            'Please check that the profile is gone.',
            'Please audit the deletion as of last Tuesday.',
            'Je demande la suppression de mon compte.',
            'Por favor eliminar mi cuenta.', 'Quiero borrar mi cuenta.',
            'アカウントの削除をお願いします。',
            'PLEASE\nDELETE MY ACCOUNT！',
        ]:
            with self.subTest(text=text):
                self.assertEqual(classify_intent(text), 'DELETION')

    def test_non_deletion(self):
        for text in [
            'Please export my data.', 'Give me access to my personal data.',
            'Please update my name.', 'Opt me out of marketing.',
            "Don't erase my profile.",
            'Please download my account data. Do not close my account.',
        ]:
            with self.subTest(text=text):
                self.assertEqual(classify_intent(text), 'NON_DELETION')

    def test_unresolved_scope_never_authorizes_or_becomes_not_applicable(self):
        for text in [
            'If my parcel arrives, delete my account.',
            'Delete my account if required.',
            'We discussed whether to delete my account.',
            'Please delete my account unless I log in.',
            'Should I delete my account?', 'Can you not delete my account?',
            'Maybe remove my profile.', 'Please only remove my name and contact details.',
            'Delete my account except my profile.',
            'Please delete my account. Keep my profile.',
            'Please delete my account. Never erase my profile.',
            'Please delete my account. I withdraw the request.',
            'Export my data, then delete my account.',
            'Please export my data. Delete my account.',
            'No eliminar mi cuenta.', 'Je ne demande pas de supprimer mon compte.',
            'Tell me how to delete my account.', 'I deleted my account yesterday.',
            'Hello there.', '',
        ]:
            with self.subTest(text=text), self.assertRaises(AuditError):
                classify_intent(text)


if __name__ == '__main__':
    unittest.main()
