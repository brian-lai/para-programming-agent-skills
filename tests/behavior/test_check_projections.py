"""Validate projection semantics independently of fixture/merge behavior."""
import unittest
from github_stub import supported_check_projection


class ProjectionTest(unittest.TestCase):
    def test_missing_fields_and_incorrect_results_are_rejected(self):
        for query, output in [('.[].bucket', 'null'), ('.|map(.bucket)', '[null]'), ('.|all(.bucket=="pass")', 'false')]:
            with self.subTest(query=query):
                self.assertFalse(supported_check_projection(['pr', 'checks'], query, [{'state': 'SUCCESS'}], output))
        for query, output in [('.[].state', 'FAILURE'), ('.|map(.state)', '["FAILURE"]'), ('.|all(.state=="SUCCESS")', 'false')]:
            with self.subTest(query=query):
                self.assertFalse(supported_check_projection(['pr', 'checks'], query, [{'state': 'SUCCESS'}], output))

    def test_empty_and_partial_sets_are_rejected(self):
        for records in ([], [{'state': 'SUCCESS'}, {'bucket': 'pass'}], [{'state': None}], [{'state': 'UNKNOWN'}]):
            self.assertFalse(supported_check_projection(['pr', 'checks'], '.|all(.state=="SUCCESS")', records, 'true'))

    def test_failed_checks_are_visible_but_not_rewritten_as_success(self):
        self.assertTrue(supported_check_projection(['pr', 'checks'], '.|all(.bucket=="pass")', [{'bucket': 'fail'}], 'false'))
        self.assertFalse(supported_check_projection(['pr', 'checks'], '.|all(.bucket=="pass")', [{'bucket': 'fail'}], 'true'))

    def test_extra_output_and_wrong_types_are_rejected(self):
        for output in ('true\ntrue', '1', 'null', '"true"'):
            self.assertFalse(supported_check_projection(['pr', 'checks'], '.|all(.state=="SUCCESS")', [{'state': 'SUCCESS'}], output))

    def test_multirecord_stream_and_predicate_require_every_record(self):
        records = [{'state': 'SUCCESS'}, {'state': 'FAILURE'}]
        self.assertTrue(supported_check_projection(['pr', 'checks'], '.[].state', records, 'SUCCESS\nFAILURE\n'))
        self.assertFalse(supported_check_projection(['pr', 'checks'], '.[].state', records, 'SUCCESS\n'))
        self.assertTrue(supported_check_projection(['pr', 'checks'], '.|all(.state=="SUCCESS")', records, 'false'))

    def test_view_combined_predicate_requires_status(self):
        query = '.statusCheckRollup | all(.status == "COMPLETED" and .conclusion == "SUCCESS")'
        self.assertFalse(supported_check_projection(['pr', 'view'], query, {'statusCheckRollup': [{'conclusion': 'SUCCESS'}]}, 'false'))
        self.assertTrue(supported_check_projection(['pr', 'view'], query, {'statusCheckRollup': [{'conclusion': 'SUCCESS', 'status': 'COMPLETED'}]}, 'true'))
