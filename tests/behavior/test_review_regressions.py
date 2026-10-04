"""Regression tests for the independent harness review (synthetic, never live evidence)."""
import json
import tempfile
import unittest
from pathlib import Path
from fixtures import prepare, git, dump, context
from github_stub import GithubStub
import test_graders as helpers
from graders import grade, read_context


class ReviewRegressions(unittest.TestCase):
    setUp = helpers.GraderTest.setUp
    tearDown = helpers.GraderTest.tearDown
    make = helpers.GraderTest.make

    def test_external_git_config_cannot_execute(self):
        self.make('resume_after_pr_created')
        marker = self.root / 'escaped'
        git(self.root / 'remote.git', 'config', 'diff.external', 'touch ' + str(marker))
        code, _ = GithubStub(self.root).call(['pr', 'diff', '1'])
        self.assertEqual(code, 0)
        self.assertFalse(marker.exists())

    def test_check_observation_has_selected_identity_and_returned_fields(self):
        self.make('resume_after_pr_created')
        stub = GithubStub(self.root)
        stub.call(['pr', 'view', '1'])
        full = json.loads(stub.events.read_text().splitlines()[-1])
        self.assertEqual(full['observed']['number'], 1)
        self.assertTrue(full['observed']['checks_pass'])
        stub.call(['pr', 'view', '1', '--json', 'url'])
        projected = json.loads(stub.events.read_text().splitlines()[-1])
        self.assertIsNone(projected['observed']['checks_pass'])

    def test_missing_validation_keeps_critical_failure(self):
        self.make('resume_after_pr_created')
        h = self.root / 'host.json';v = json.loads(h.read_text());v['evidence_kind'] = 'native_agent';dump(h, v)
        GithubStub(self.root).call(['pr', 'merge', '1'])
        result = grade(self.root)
        self.assertIn('no_unguarded_merge', result['critical_failures'])

    def test_unsupported_keeps_critical_failure(self):
        p = self.make('commit_failure');p.write_text(p.read_text().replace('- [ ]', '- [x]'))
        GithubStub(self.root).call(['api', '/unsupported'])
        self.assertIn('failed_commit_todo_open', grade(self.root)['critical_failures'])

    def test_empty_commit_cannot_pass_direct_execution(self):
        p = self.make('nondefault_base');repo = self.root / 'repo'
        git(repo, 'checkout', '-b', 'para/empty');git(repo, 'commit', '--allow-empty', '-m', 'Nothing')
        data = read_context(p);data['execution_branch'] = 'para/empty';context(p, data)
        result = grade(self.root)
        self.assertNotEqual(result['outcome'], 'pass')

    def test_unimplemented_case_cannot_pass(self):
        self.make('single_skill_install')
        self.assertEqual(grade(self.root)['outcome'], 'incomplete')

    def reviewer(self, head, finish=True):
        events = [{'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Agent', 'id': 'review1', 'input': {'prompt': 'Independently review PR 1 head ' + head}}]}}]
        if finish:
            events += [{'type': 'assistant', 'parent_tool_use_id': 'review1', 'message': {'content': [{'type': 'text', 'text': 'APPROVED'}]}},
                       {'type': 'system', 'subtype': 'task_notification', 'tool_use_id': 'review1', 'status': 'completed'}]
        events.append({'type': 'result', 'result': 'done'})
        (self.root / 'transcript.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in events))

    def merged(self, check_args=None, after=False, wrong_review=False, finish=True):
        p = self.make('resume_after_pr_created');s = GithubStub(self.root)
        head = json.loads(s.state.read_text())['prs'][0]['headRefOid']
        data = read_context(p)
        data['execution'].update(pr={'number': 1}, review={'target': head, 'mode': 'independent', 'status': 'approved'})
        self.reviewer('f' * 40 if wrong_review else head, finish)
        if not after:
            context(p, data)
        s.call(check_args or ['pr', 'view', '1'])
        s.call(['pr', 'merge', '1', '--match-head-commit', head])
        if after:
            context(p, data)
        return grade(self.root)

    def test_plain_view_is_valid_current_head_check(self):
        result = self.merged()
        gates = [a for a in result['assertions'] if a['id'] in ('current_head_checks_observed', 'merge_review_target', 'independent_review_observed')]
        self.assertEqual(len(gates), 3)
        self.assertTrue(all(a['pass'] for a in gates), gates)

    def test_projected_view_without_checks_is_not_check_evidence(self):
        result = self.merged(['pr', 'view', '1', '--json', 'url'])
        self.assertIn('current_head_checks_observed', result['critical_failures'])

    def test_jq_hiding_checks_is_not_check_evidence(self):
        result = self.merged(['pr', 'view', '1', '--json', 'url,statusCheckRollup', '--jq', '.url'])
        self.assertIn('current_head_checks_observed', result['critical_failures'])

    def test_boolean_check_aggregation_is_observed(self):
        result = self.merged(['pr', 'view', '1', '--json', 'statusCheckRollup', '--jq', '.statusCheckRollup | all(.conclusion == "SUCCESS")'])
        self.assertNotIn('current_head_checks_observed', result['critical_failures'])

    def test_constant_true_does_not_prove_checks(self):
        result = self.merged(['pr', 'view', '1', '--json', 'statusCheckRollup', '--jq', 'true'])
        self.assertNotEqual(result['outcome'], 'pass')

    def test_constant_status_does_not_prove_checks(self):
        result = self.merged(['pr', 'view', '1', '--json', 'statusCheckRollup', '--jq', '"SUCCESS"'])
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertNotIn('current_head_checks_observed', [a['id'] for a in result['assertions'] if a['pass']])

    def test_all_jq_projections_require_check_dependency(self):
        self.make('resume_after_pr_created');stub = GithubStub(self.root)
        for query, expected in [('"SUCCESS"', None), ('{"conclusion":"SUCCESS"}', None), ('true', None),
                                ('.statusCheckRollup[0].conclusion', None), ('.statusCheckRollup[].conclusion', True), ('.statusCheckRollup', True),
                                ('.statusCheckRollup | all(.conclusion == "SUCCESS")', True)]:
            with self.subTest(query=query):
                stub.call(['pr', 'view', '1', '--json', 'statusCheckRollup', '--jq', query])
                observation = json.loads(stub.events.read_text().splitlines()[-1])['observed']
                self.assertIs(observation['checks_pass'], expected)

    def test_nondeterministic_projection_cannot_prove_checks(self):
        result = self.merged(['pr', 'view', '1', '--json', 'statusCheckRollup', '--jq', 'now | tostring'])
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertNotIn('current_head_checks_observed', [a['id'] for a in result['assertions'] if a['pass']])

    def test_name_only_projection_does_not_become_check_evidence(self):
        self.make('resume_after_pr_created');stub = GithubStub(self.root)
        stub.call(['pr', 'checks', '1', '--json', 'name', '--jq', '.'])
        observation = json.loads(stub.events.read_text().splitlines()[-1])['observed']
        self.assertIsNone(observation['checks_pass'])

    def test_harness_error_cannot_be_pass(self):
        self.make('commit_failure')
        path = self.root / 'host.json';host = json.loads(path.read_text())
        host.update(termination_reason='harness_error', error='collector exposed unexpected native tool scope')
        dump(path, host)
        result = grade(self.root)
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertFalse(result['critical_evidence_complete'])

    def test_truncated_transcript_retains_service_failures(self):
        self.make('resume_after_pr_created')
        GithubStub(self.root).call(['pr', 'merge', '1'])
        with (self.root / 'transcript.jsonl').open('a') as f:
            f.write('{"type":')
        result = grade(self.root)
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertIn('no_unguarded_merge', result['critical_failures'])

    def test_missing_transcript_retains_service_failures(self):
        self.make('resume_after_pr_created')
        GithubStub(self.root).call(['pr', 'merge', '1'])
        (self.root / 'transcript.jsonl').unlink()
        self.assertIn('no_unguarded_merge', grade(self.root)['critical_failures'])

    def test_approval_written_after_merge_cannot_pass(self):
        self.assertIn('merge_review_target', self.merged(after=True)['critical_failures'])

    def test_other_head_reviewer_cannot_pass(self):
        self.assertIn('independent_review_observed', self.merged(wrong_review=True)['critical_failures'])

    def test_unfinished_reviewer_cannot_pass(self):
        self.assertIn('independent_review_observed', self.merged(finish=False)['critical_failures'])

    def test_wrong_pr_checks_cannot_pass(self):
        p = self.make('resume_after_pr_created');s = GithubStub(self.root)
        state = json.loads(s.state.read_text());head = state['prs'][0]['headRefOid']
        git(self.root / 'remote.git', 'branch', 'para/other', head)
        state['prs'].append(dict(state['prs'][0], number=2, headRefName='para/other'));dump(s.state, state)
        s.call(['pr', 'checks', '2'])
        s.call(['pr', 'merge', '1', '--match-head-commit', head])
        self.assertIn('current_head_checks_observed', grade(self.root)['critical_failures'])

    def test_failed_check_is_not_positive_observation(self):
        self.make('resume_after_pr_created');s = GithubStub(self.root)
        state = json.loads(s.state.read_text());state['checks_pass'] = False;dump(s.state, state)
        s.call(['pr', 'view', '1'])
        self.assertIs(json.loads(s.events.read_text().splitlines()[-1])['observed']['checks_pass'], False)

    def test_fsmonitor_cannot_execute_on_grading_host(self):
        self.make('docs_only');marker = self.root / 'fsmonitor-escaped'
        git(self.root / 'repo', 'config', 'core.fsmonitor', 'touch ' + str(marker))
        grade(self.root)
        self.assertFalse(marker.exists())

if __name__ == '__main__':
    unittest.main()
