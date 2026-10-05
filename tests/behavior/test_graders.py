import json
import tempfile
import unittest
from pathlib import Path
from fixtures import prepare, dump, context
from graders import grade, read_context


class GraderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='para-grader-')
        self.root = Path(self.tmp.name) / 'trial'

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, case):
        initial = prepare(case, self.root)
        (self.root / 'transcript.jsonl').write_text(json.dumps({'type': 'result', 'subtype': 'success', 'result': 'done'}) + '\n')
        dump(self.root / 'host.json', {'host': 'test-only-synthetic', 'host_version': '1', 'model': 'none',
            'settings': {'limits': {'wall_seconds': 600, 'tool_calls': 100}}, 'skill_revision': 'test', 'trial': 0,
            'case_version': initial['case_version'], 'elapsed_seconds': 1, 'termination_reason': None,
            'evidence_kind': 'synthetic_grader_test'})
        return self.root / 'repo/context/context.md'

    def test_agent_done_claim_not_sufficient(self):
        self.make('simple_workflow_lifecycle')
        self.assertEqual(grade(self.root)['outcome'], 'fail')

    def test_duplicate_pr_fails(self):
        self.make('resume_after_pr_created')
        p = self.root / 'service/state.json';s = json.loads(p.read_text());s['prs'].append(dict(s['prs'][0], number=2));dump(p, s)
        self.assertIn('unique_pr_effect', [a['id'] for a in grade(self.root)['assertions'] if not a['pass']])

    def test_commit_failure_leaves_todo_open(self):
        p = self.make('commit_failure')
        self.assertEqual(grade(self.root)['outcome'], 'pass')
        p.write_text(p.read_text().replace('- [ ]', '- [x]'))
        self.assertEqual(grade(self.root)['outcome'], 'fail')

    def test_legacy_completion_needs_merge_evidence(self):
        self.make('legacy_completed_without_evidence')
        self.assertEqual(grade(self.root)['outcome'], 'fail')

    def test_partial_archive_retains_pending_phase(self):
        p = self.make('partial_archive');s = read_context(p)
        s['phased_execution']['phases'].pop();context(p, s)
        self.assertIn('pending_phase_preserved', [a['id'] for a in grade(self.root)['assertions'] if not a['pass']])

    def test_stale_head_fails(self):
        self.make('stale_review_head')
        self.assertIn('current_head_review', [a['id'] for a in grade(self.root)['assertions'] if not a['pass']])

    def test_missing_evidence_is_incomplete(self):
        self.make('commit_failure');(self.root / 'transcript.jsonl').unlink()
        self.assertEqual(grade(self.root)['outcome'], 'incomplete')

    def test_unknown_usage_is_null(self):
        self.make('commit_failure')
        self.assertEqual(grade(self.root)['usage'], {'input_tokens': None, 'output_tokens': None})
