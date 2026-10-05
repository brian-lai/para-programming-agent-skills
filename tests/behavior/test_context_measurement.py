import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
spec = importlib.util.spec_from_file_location('measure', Path(__file__).resolve().parents[2] / 'scripts/measure-skill-context.py')
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)


class MeasurementTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory();self.root = Path(self.tmp.name)
        (self.root / 'SKILL.md').write_text('---\nname: sample\n---\nRead resource.md\n')
        (self.root / 'resource.md').write_text('é')
        self.manifest = {'scenarios': {'sample': {'paths': ['SKILL.md', 'resource.md'], 'required_resources': ['resource.md']}}}
        self.baseline = {'scenarios': {'sample': {'bytes': 100}}}

    def tearDown(self):
        self.tmp.cleanup()

    def test_required_reference_counted(self):
        result = measure.measure(self.root, self.manifest, self.baseline)
        self.assertEqual(result['scenarios']['sample']['bytes'], len((self.root / 'SKILL.md').read_bytes()) + 2)
        del self.manifest['scenarios']['sample']['paths'][1]
        with self.assertRaises(ValueError):
            measure.measure(self.root, self.manifest, self.baseline)

    def test_missing_path_is_error(self):
        (self.root / 'resource.md').unlink()
        with self.assertRaises(OSError):
            measure.measure(self.root, self.manifest, self.baseline)

    def test_growth_fails_gate(self):
        self.baseline['scenarios']['sample']['bytes'] = 1
        self.assertFalse(measure.measure(self.root, self.manifest, self.baseline)['within_budget'])

    def test_utf8_counts_are_bytes(self):
        self.assertEqual(measure.measure(self.root, self.manifest, self.baseline)['files']['resource.md']['bytes'], 2)
