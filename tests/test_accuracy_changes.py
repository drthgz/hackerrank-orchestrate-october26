"""Semantic recall and citation metrics must not conflate omission and error."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('accuracy_changes',
    Path(__file__).resolve().parents[1] / 'code/evaluation/accuracy_changes.py')
reporting = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reporting)


class AccuracyChangeTests(unittest.TestCase):
    def step(self, resource='record-violet', evidence='witness', phase='FINDING'):
        return dict(step_no=1, phase=phase, system_id='example', resource_id=resource,
                    operation='REPORT_EXPOSED_PII', state='PRESENT', evidence_id=evidence)

    def test_numbering_shift_is_not_missing_content(self):
        expected = dict(status='INCOMPLETE', steps=[self.step()])
        actual = dict(status='INCOMPLETE', steps=[dict(self.step(), step_no=3)])
        m = reporting.metrics({'arbitrary': actual}, {'arbitrary': expected})
        self.assertEqual((m['matched_steps'], m['exact_cases']), (1, 0))

    def test_wrong_aligned_citation_is_reported_separately(self):
        expected = dict(status='INCOMPLETE', steps=[self.step()])
        actual = dict(status='INCOMPLETE', steps=[self.step(evidence='wrong')])
        m = reporting.metrics({'arbitrary': actual}, {'arbitrary': expected})
        self.assertEqual((m['aligned_citations_correct'], m['aligned_citations']), (0, 1))
        self.assertEqual(len(m['incorrect_aligned_citations']), 1)

    def test_extras_and_missing_phases_are_independent(self):
        expected = dict(status='INCOMPLETE', steps=[self.step(), self.step(phase='VERIFICATION', evidence='')])
        actual = dict(status='INCOMPLETE', steps=[self.step(), self.step(resource='other')])
        m = reporting.metrics({'arbitrary': actual}, {'arbitrary': expected})
        self.assertEqual(m['extra_steps_vs_reference'], 1)
        self.assertEqual(m['missing_steps_by_phase'], {'VERIFICATION': 1})
