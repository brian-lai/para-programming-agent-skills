import copy
import sys
import tempfile
import unittest
from pathlib import Path
from comparison import compare, run_bounded


def trial(outcome='pass', revision='candidate'):
    return {'case_id': 'case', 'case_version': 'v1', 'trial': 1, 'variant': 0, 'host': 'native',
        'host_version': '1', 'model': 'model', 'settings': {'limits': {'wall_seconds': 600, 'tool_calls': 100}},
        'skill_revision': revision, 'outcome': outcome, 'critical_failures': [], 'usage': {'input_tokens': None, 'output_tokens': None},
        'elapsed_seconds': 1, 'tool_calls': None, 'evidence_kind': 'native_agent'}


class ComparisonTest(unittest.TestCase):
    def test_pair_settings_mismatch_rejected(self):
        a, b = trial(), trial();b['settings']['limits']['wall_seconds'] = 20
        with self.assertRaises(ValueError): compare([a], [b])

    def test_failed_trial_retained(self):
        result = compare([trial()], [trial('fail')])
        self.assertEqual(result['candidate']['outcomes']['fail'], 1)
        self.assertEqual(result['pairs'], 1)

    def test_null_usage_not_zero(self):
        self.assertIsNone(compare([trial()], [trial()])['candidate']['input_tokens'])

    def test_timeout_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'native.jsonl'
            value = run_bounded([sys.executable, '-u', '-c', 'import time;print("started", flush=True);time.sleep(5)'], p, 0.1, 100)
            self.assertEqual(value['termination_reason'], 'wall_timeout')
            self.assertIn('started', p.read_text())

    def test_mixed_revision_aggregate_labeled(self):
        a, b = trial(revision='one'), trial(revision='two');b['trial'] = 2
        result = compare([a, b], [a, b])
        self.assertTrue(result['candidate']['mixed_revisions'])
        self.assertEqual(set(result['candidate']['by_revision']), {'one', 'two'})
