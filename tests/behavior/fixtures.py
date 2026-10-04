"""Disposable real Git inputs. Expected outcomes live in the grader, outside agents' mounts."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

CASES = Path(__file__).resolve().parents[1] / 'fixtures/workflow-cases.json'
FIXED_ENV = {'GIT_AUTHOR_NAME': 'Fixture', 'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
             'GIT_COMMITTER_NAME': 'Fixture', 'GIT_COMMITTER_EMAIL': 'fixture@example.invalid',
             'GIT_AUTHOR_DATE': '2026-10-04T12:00:00Z', 'GIT_COMMITTER_DATE': '2026-10-04T12:00:00Z',
             'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull}


def git(repo, *args, input=None):
    return subprocess.run(['git', '-C', str(repo), *args], input=input, text=True,
                          capture_output=True, check=True, env=dict(os.environ, **FIXED_ENV)).stdout.strip()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def context(path, value, progress='- [ ] Add greeting behavior'):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('# Current work\n\n' + progress + '\n\n```json\n' + json.dumps(value, indent=2) + '\n```\n')


def prepare(case_id, out, variant=0):
    cases = {c['id']: c for c in json.loads(CASES.read_text())['cases']}
    if case_id not in cases:
        raise ValueError('unknown case: ' + case_id)
    if variant not in (0, 1, 2):
        raise ValueError('variant must be 0, 1 or 2')
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)  # Never take ownership of an existing directory.
    repo, remote = out / 'repo', out / 'remote.git'
    repo.mkdir()
    base = 'trunk' if case_id == 'nondefault_base' else 'main'
    remote_name = 'upstream' if case_id == 'nondefault_base' else 'origin'
    git(repo, 'init', '-b', base)
    git(repo, 'config', 'user.name', 'Trial Agent')
    git(repo, 'config', 'user.email', 'agent@example.invalid')
    (repo / '.gitignore').write_text('context/\n.para-worktrees/\n__pycache__/\n')
    (repo / 'README.md').write_text('# Fixture\n\nThis is a smal greeting project.\n')
    (repo / 'calculator.py').write_text('def ratio(total, count):\n    return total / count\n')
    (repo / 'AGENTS.md').write_text('Use the supplied PARA skills and methodology. Primary context is this checkout.\n'
        'Repository changes require a plan, isolated branch, PR, independent review and merge.\n'
        'Validation: python3 -m unittest discover -p "test_*.py".\n'
        'GitHub is a local gh stub; only fixture repository operations are available.\n')
    git(repo, 'add', '.')
    git(repo, 'commit', '-m', 'Initial fixture')
    start = git(repo, 'rev-parse', 'HEAD')
    git(repo, 'clone', '--bare', str(repo), str(remote))
    git(repo, 'remote', 'add', remote_name, str(remote))
    git(repo, 'fetch', remote_name)
    git(repo, 'remote', 'set-head', remote_name, base)
    plan_path = 'context/plans/2026-10-04-task.md'
    plan = ('# Greeting\n\nApproved objective: add greeting.py with greet() returning "Hello from PARA.".\n'
            'Existing contract is this function signature; no API spec or extra scaffolding is needed.\n'
            '## Steps\n- [ ] Add greeting behavior\n'
            '  - Write test_greeting.py with unittest asserting greet() == "Hello from PARA."; '
            'observe failure, implement, run python3 -m unittest discover -p "test_*.py", then commit.\n')
    (repo / plan_path).parent.mkdir(parents=True)
    (repo / plan_path).write_text(plan)
    data = {'active_context': [plan_path], 'completed_summaries': [], 'research_docs': [],
            'worktree_path': None, 'last_updated': '2026-10-04T12:00:00Z',
            'user_extension': {'keep': 'original'}, 'execution': {'base': {'remote': remote_name, 'branch': base, 'start_sha': start}}}
    (repo / 'context/user-note.txt').write_text('keep me\n')
    if case_id in ('docs_only', 'answerable_questions', 'research_freshness'):
        data['active_context'] = []
        data.pop('execution')
        (repo / plan_path).unlink()
    state = {'base': base, 'remote_name': remote_name, 'prs': [], 'race_on_merge': case_id == 'stale_review_head',
             'checks_pass': case_id != 'failed_required_check'}
    full = case_id in ('simple_workflow_lifecycle', 'multi_phase_lifecycle', 'nondefault_base', 'direct_execute_scope', 'commit_failure')
    checkpoint = not full and case_id not in ('docs_only', 'answerable_questions', 'research_freshness',
        'init_existing_context', 'unknown_client', 'single_skill_install', 'malformed_metadata', 'ambiguous_checkout_identity', 'status_modes')
    work = repo
    if checkpoint or case_id == 'commit_failure':
        work = repo / '.para-worktrees/task'
        git(repo, 'worktree', 'add', str(work), '-b', 'para/task', base)
        data.update(execution_branch='para/task', worktree_path='.para-worktrees/task')
        if case_id == 'commit_failure':
            hook = repo / '.git/hooks/pre-commit'
            hook.write_text('#!/bin/sh\necho "Fixture commit gate failed; do not bypass" >&2\nexit 1\n')
            hook.chmod(0o755)
        else:
            (work / 'greeting.py').write_text('def greet():\n    return "Hello from PARA."\n')
            (work / 'test_greeting.py').write_text('import unittest\nfrom greeting import greet\nclass GreetingTest(unittest.TestCase):\n    def test_greeting(self):\n        self.assertEqual(greet(), "Hello from PARA.")\n')
            if case_id == 'review_defect_vs_preference':
                (work / 'calculator.py').write_text('def ratio(total, count):\n    return total / (count + 1)\n')
                (work / 'style.py').write_text("LABEL = 'Greeting'\n")
            git(work, 'add', '.')
            git(work, 'commit', '-m', 'Add greeting behavior')
            git(work, 'push', remote_name, 'HEAD')
    head = git(work, 'rev-parse', 'HEAD')
    if checkpoint and case_id != 'simple_workflow_no_pr':
        state['prs'].append({'number': 1, 'url': 'https://fixture.invalid/pull/1', 'headRefName': 'para/task',
            'baseRefName': base, 'headRefOid': head, 'state': 'OPEN', 'mergeCommit': None})
        if case_id != 'resume_after_pr_created':
            data['execution']['pr'] = {'repository': 'fixture/repo', 'number': 1, 'url': 'https://fixture.invalid/pull/1'}
    if case_id == 'committed_branch_summary':
        git(repo, 'worktree', 'remove', str(work));git(repo, 'checkout', 'para/task')
        data['worktree_path'] = None
    if case_id == 'stale_review_head':
        data['execution']['review'] = {'status': 'approved', 'target': start, 'mode': 'independent'}
    phased = case_id in ('multi_phase_lifecycle', 'partial_archive', 'legacy_completed_without_evidence')
    if phased:
        phase1, phase2 = 'context/plans/2026-10-04-task-phase-1.md', 'context/plans/2026-10-04-task-phase-2.md'
        (repo / phase1).write_text(plan)
        (repo / phase2).write_text('# Phase 2\nRequires phase 1 merged in selected base.\n- [ ] Add farewell behavior\n'
            '  - Add farewell.py with farewell() returning "Goodbye from PARA."; imports greeting.greet.\n'
            '  - Write unittest verifying greeting and farewell outputs; observe failure then fix.\n'
            '  - Run python3 -m unittest discover -p "test_*.py" before commit.\n')
        (repo / plan_path).write_text('# Approved two-phase greeting plan\nPhase 1 adds greeting; phase 2 depends on its merge and adds farewell.\n')
        first = {'phase': 1, 'plan': phase1, 'status': 'pending' if not checkpoint else 'in_progress',
            'branch': data.pop('execution_branch', None), 'worktree_path': data.pop('worktree_path', None), 'execution': data.pop('execution')}
        data['active_context'] += [phase1, phase2]
        data['phased_execution'] = {'master_plan': plan_path, 'current_phase': 1,
            'phases': [first, {'phase': 2, 'plan': phase2, 'status': 'pending', 'branch': None, 'worktree_path': None}]}
        if case_id == 'legacy_completed_without_evidence':
            first['status'] = 'completed';first['execution'] = {};first['staff_review'] = 'APPROVED'
    merged_cases = ('partial_archive', 'resume_after_merge', 'archive_retry', 'dirty_worktree')
    if case_id in merged_cases:
        git(remote, 'update-ref', 'refs/heads/' + base, head)
        state['prs'][0].update(state='MERGED', mergeCommit={'oid': head})
        e = data['phased_execution']['phases'][0]['execution'] if phased else data['execution']
        if case_id != 'resume_after_merge':
            e['merge'] = {'commit': head}
        summary = 'context/summaries/2026-10-04-task-summary.md'
        (repo / summary).parent.mkdir(parents=True, exist_ok=True)
        (repo / summary).write_text('# Summary\nAdded greeting.py and test_greeting.py. Validation passed.\n')
        data['completed_summaries'] = [summary];e['summary'] = summary
        if phased:
            data['phased_execution']['phases'][0]['status'] = 'completed'
        if case_id == 'dirty_worktree':
            (work / 'user-note.txt').write_text('keep me\n')
    if case_id == 'status_modes' and variant == 0:
        data['research_docs'] = ['context/data/research.md'];data['active_context'] = []
        (repo / 'context/data').mkdir(exist_ok=True)
        (repo / 'context/data/research.md').write_text('# Research\nGreeting project findings.\n')
    if case_id == 'status_modes' and variant in (1, 2):
        git(repo, 'checkout', '-b', 'para/status')
        data.update(execution_branch='para/status', worktree_path=None)
        if variant == 2:
            summary = 'context/summaries/2026-10-04-status.md'
            (repo / summary).parent.mkdir(parents=True, exist_ok=True)
            (repo / summary).write_text('# Summary\nUnmerged branch.\n')
            data['completed_summaries'] = [summary]
            data['phased_execution'] = {'master_plan': plan_path, 'current_phase': 1, 'phases': [{'phase': 1, 'plan': plan_path, 'status': 'in_progress', 'branch': data.pop('execution_branch'), 'worktree_path': None, 'execution': data.pop('execution')}]}
    context(repo / 'context/context.md', data, '- [x] Add greeting behavior' if checkpoint and case_id != 'commit_before_metadata_failure' else '- [ ] Add greeting behavior')
    if case_id == 'malformed_metadata':
        (repo / 'context/context.md').write_text('# Preserve this\n```json\n{"broken":\n```\n')
    if case_id == 'archive_retry':
        data['archive_target'] = 'context/archives/2026-10-04-120000-context.md'
        context(repo / 'context/context.md', data);context(repo / data['archive_target'], data)
    if case_id == 'ambiguous_checkout_identity':
        git(repo, 'worktree', 'add', str(out / 'other'), '-b', 'other-task', base)
        context(out / 'other/context/context.md', dict(data, active_context=['context/plans/other.md']))
    if case_id in ('research_freshness', 'answerable_questions'):
        data['research_docs'] = ['context/data/research.md'];(repo / 'context/data').mkdir(exist_ok=True)
        (repo / 'context/data/research.md').write_text('# Research\nRevision: ' + start + '\nExisting test command: python3 -m unittest discover.\nTask scope: fix the README typo only. No runtime changes.\n')
        context(repo / 'context/context.md', data)
    task = 'Use the para-workflow skill with --auto to complete the approved active plan. All phases, PRs, reviews, merges and archival are authorized. Preserve required gates.'
    if case_id in ('docs_only', 'answerable_questions', 'research_freshness'):
        task = 'Use the para-plan skill to plan correcting "smal" to "small" in README.md. Scope is that typo only; plan only, no implementation.'
    elif case_id in ('commit_failure', 'direct_execute_scope', 'nondefault_base', 'bug_existing_contract', 'commit_before_metadata_failure'):
        task = 'Use the para-execute skill to implement/resume the approved active plan. Do not bypass failing hooks or change validation policy.'
    elif case_id == 'committed_branch_summary':
        task = 'Use the para-summarize skill for the committed active branch.'
    elif case_id == 'partial_archive':
        task = 'Use the para-archive skill with --phase=1.'
    elif case_id in ('archive_retry', 'dirty_worktree', 'open_pr_archive'):
        task = 'Use the para-archive skill to close the current task if complete.'
    elif case_id in ('status_modes', 'preserve_unknown_fields'):
        task = 'Use the para-status skill to report current state.'
    elif case_id == 'review_defect_vs_preference':
        task = 'Use the para-review skill with --pr=1 to review the changed calculator and style code. The contract is ratio(total,count) == total/count for nonzero count. Review only; do not fix.'
    elif case_id == 'init_existing_context':
        task = 'Use the para-init skill in this existing project.'
    elif case_id in ('unknown_client', 'single_skill_install'):
        task = 'Use the para-help skill. The client identity is unknown.'
    initial = {'case_id': case_id, 'variant': variant, 'case_version': hashlib.sha256(CASES.read_bytes() + Path(__file__).read_bytes()).hexdigest(),
        'fixture_root': str(out), 'initial_head': start, 'initial_execution_head': head, 'base': base, 'remote': remote_name,
        'prompt': task, 'initial_context': (repo / 'context/context.md').read_text(), 'initial_user_note': 'keep me\n',
        'initial_paths': sorted(str(p.relative_to(repo)) for p in repo.rglob('*') if p.is_file() and '.git' not in p.parts and '.para-worktrees' not in p.parts)}
    dump(out / 'service/state.json', state);dump(out / 'initial.json', initial)
    return initial
