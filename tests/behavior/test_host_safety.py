import importlib.util
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('trial_runner', Path(__file__).resolve().parents[2] / 'scripts/run-skill-trial.py')
runner = importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


class HostSafetyTest(unittest.TestCase):
    def test_agent_and_worker_stopped_before_validation(self):
        order = []
        with patch.object(runner, 'run_bounded', side_effect=lambda *a: order.append('capture') or {'termination_reason': 'wall_timeout'}), patch.object(runner, 'stop_container', side_effect=lambda name: order.append(name)):
            runner.capture_and_stop([], Path('/unused'), {'wall_seconds': 1, 'tool_calls': 1}, 'collector', 'worker')
            order.append('validation')
        self.assertEqual(order, ['capture', 'collector', 'worker', 'validation'])

    def test_capture_exception_still_stops_agent(self):
        with patch.object(runner, 'run_bounded', side_effect=RuntimeError('capture failed')), patch.object(runner, 'stop_container') as stop:
            with self.assertRaises(RuntimeError):
                runner.capture_and_stop([], Path('/unused'), {'wall_seconds': 1, 'tool_calls': 1}, 'owned-agent')
        stop.assert_called_once_with('owned-agent')

    def test_failed_stop_blocks_validation_and_still_stops_other_container(self):
        with patch.object(runner, 'run_bounded', return_value={}), patch.object(runner, 'stop_container', side_effect=[RuntimeError('still running'), None]) as stop:
            with self.assertRaises(RuntimeError):
                runner.capture_and_stop([], Path('/unused'), {'wall_seconds': 1, 'tool_calls': 1}, 'collector', 'worker')
        self.assertEqual(stop.call_count, 2)

    def test_container_absence_is_confirmed(self):
        with patch.object(runner, 'docker', side_effect=[SimpleNamespace(returncode=1), SimpleNamespace(stdout='owned-agent\n')]):
            with self.assertRaises(RuntimeError):
                runner.stop_container('owned-agent')
        with patch.object(runner, 'docker', side_effect=[SimpleNamespace(returncode=1), subprocess.CalledProcessError(1, 'docker ps')]):
            with self.assertRaises(subprocess.CalledProcessError):
                runner.stop_container('owned-agent')

    def test_model_drift_invalidates_collection(self):
        one = {'message': {'model': 'us.anthropic.claude-sonnet-5-5'}}
        other = {'message': {'model': 'us.anthropic.claude-opus-5-5'}}
        self.assertEqual(runner.validate_model_scope([one, one]), ['us.anthropic.claude-sonnet-5-5'])
        with self.assertRaises(ValueError):
            runner.validate_model_scope([one, other])
        with self.assertRaises(ValueError):
            runner.validate_model_scope([])
