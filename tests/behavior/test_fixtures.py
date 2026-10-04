import json
import tempfile
import unittest
from pathlib import Path
from fixtures import prepare, git
from github_stub import GithubStub


class FixturesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='para-fixture-test-')
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, case='simple_workflow_lifecycle', name='trial'):
        return prepare(case, self.root / name)

    def test_fixture_reproducible(self):
        a, b = self.make(name='a'), self.make(name='b')
        self.assertEqual(a['initial_head'], b['initial_head'])
        self.assertEqual(a['case_version'], b['case_version'])
        with self.assertRaises(FileExistsError):
            self.make(name='a')

    def test_pr_create_logged_once(self):
        self.make('simple_workflow_no_pr')
        s = GithubStub(self.root / 'trial')
        args = ['pr', 'create', '--head', 'para/task', '--base', 'main']
        self.assertEqual(s.call(args)[0], 0)
        self.assertNotEqual(s.call(args)[0], 0)
        events = [json.loads(x) for x in s.events.read_text().splitlines()]
        self.assertEqual(sum(x['effect'] == 'created' for x in events), 1)

    def test_help_has_no_effects(self):
        self.make('simple_workflow_no_pr')
        s = GithubStub(self.root / 'trial')
        original = s.state.read_text()
        for operation in ('create', 'merge', 'view'):
            self.assertEqual(s.call(['pr', operation, '--help'])[0], 0)
            self.assertEqual(s.state.read_text(), original)

    def test_json_projection_does_not_supply_unrequested_checks(self):
        self.make('resume_after_pr_created')
        code, output = GithubStub(self.root / 'trial').call(['pr', 'view', '1', '--json', 'url'])
        self.assertEqual(code, 0)
        self.assertEqual(set(json.loads(output)), {'url'})

    def test_global_repository_option_preserves_request_and_check_identity(self):
        self.make('resume_after_pr_created')
        stub = GithubStub(self.root / 'trial')
        for prefix in (['--repo', 'fixture/repo'], ['-R', 'fixture/repo'], ['--repo=fixture/repo']):
            for operation in ('diff', 'checks'):
                args = prefix + ['pr', operation, '1']
                with self.subTest(args=args):
                    self.assertEqual(stub.call(args)[0], 0)
                    event = json.loads(stub.events.read_text().splitlines()[-1])
                    self.assertEqual(event['args'], args)
                    self.assertEqual(event['observed']['number'], 1)
                    if operation == 'checks':
                        self.assertTrue(event['observed']['checks_pass'])
        for args in (['--repo'], ['--repo', 'other/repo', 'pr', 'view', '1']):
            self.assertNotEqual(stub.call(args)[0], 0)

    def test_stub_rejects_unknown_operation(self):
        self.make()
        self.assertNotEqual(GithubStub(self.root / 'trial').call(['api', '/delete-everything'])[0], 0)

    def test_nondefault_base_fixture(self):
        self.make('nondefault_base')
        repo = self.root / 'trial/repo'
        self.assertEqual(git(repo, 'branch', '--show-current'), 'trunk')
        self.assertEqual(git(repo, 'remote'), 'upstream')

    def test_dirty_worktree_preserved(self):
        self.make('dirty_worktree')
        self.assertEqual((self.root / 'trial/repo/.para-worktrees/task/user-note.txt').read_text(), 'keep me\n')

    def test_merge_rejects_changed_head(self):
        self.make('stale_review_head')
        s = GithubStub(self.root / 'trial')
        old = json.loads(s.state.read_text())['prs'][0]['headRefOid']
        code, _ = s.call(['pr', 'merge', '1', '--merge', '--match-head-commit', old])
        self.assertNotEqual(code, 0)
        self.assertEqual(json.loads(s.state.read_text())['prs'][0]['state'], 'OPEN')

    def test_merge_updates_real_base(self):
        self.make('resume_after_pr_created')
        s = GithubStub(self.root / 'trial')
        head = json.loads(s.state.read_text())['prs'][0]['headRefOid']
        self.assertEqual(s.call(['pr', 'merge', '1', '--merge', '--match-head-commit', head])[0], 0)
        self.assertEqual(git(self.root / 'trial/remote.git', 'rev-parse', 'main'), head)
