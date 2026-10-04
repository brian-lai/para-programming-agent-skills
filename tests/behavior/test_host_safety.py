import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('trial_runner', Path(__file__).resolve().parents[2] / 'scripts/run-skill-trial.py')
runner = importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


class HostSafetyTest(unittest.TestCase):
    def test_agent_stopped_before_capture_returns_for_validation(self):
        order = []
        with patch.object(runner, 'run_bounded', side_effect=lambda *a: order.append('capture') or {'termination_reason': 'wall_timeout'}), patch.object(runner, 'docker', side_effect=lambda *a, **k: order.append('stop')):
            runner.capture_and_stop([], Path('/unused'), {'wall_seconds': 1, 'tool_calls': 1}, 'owned-agent')
            order.append('validation')
        self.assertEqual(order, ['capture', 'stop', 'validation'])

    def test_capture_exception_still_stops_agent(self):
        with patch.object(runner, 'run_bounded', side_effect=RuntimeError('capture failed')), patch.object(runner, 'docker') as docker:
            with self.assertRaises(RuntimeError):
                runner.capture_and_stop([], Path('/unused'), {'wall_seconds': 1, 'tool_calls': 1}, 'owned-agent')
        docker.assert_called_once_with('rm', '-f', 'owned-agent', check=False)
