import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / 'scripts/evaluate-skills.py'


class CliTest(unittest.TestCase):
    def test_missing_evidence_returns_two_and_result(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'result.json'
            process = subprocess.run([sys.executable, str(SCRIPT), 'grade', '--case', 'commit_failure', '--run', d, '--out', str(out)], capture_output=True)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(json.loads(out.read_text())['outcome'], 'incomplete')

    def test_unknown_fixture_returns_two(self):
        with tempfile.TemporaryDirectory() as d:
            process = subprocess.run([sys.executable, str(SCRIPT), 'prepare', '--case', 'not-a-case', '--out', str(Path(d) / 'fixture')], capture_output=True)
            self.assertEqual(process.returncode, 2)
            self.assertFalse((Path(d) / 'fixture').exists())
