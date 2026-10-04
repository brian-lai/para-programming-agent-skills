"""Grade collected effects. Agent prose is never sufficient completion evidence."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from fixtures import git


def read_context(path):
    match = re.search(r'```json\s*\n(.*?)\n```', Path(path).read_text(), re.S)
    if not match:
        raise ValueError('missing context JSON')
    value = json.loads(match[1])
    if not isinstance(value, dict):
        raise ValueError('context must be an object')
    return value


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def grade(root):
    root = Path(root).resolve()
    result = {'outcome': 'incomplete', 'assertions': [], 'usage': {'input_tokens': None, 'output_tokens': None},
              'tool_calls': None, 'termination_reason': None, 'artifacts': {}}
    try:
        for path in root.rglob('*'):
            if path.is_symlink() and not path.resolve().is_relative_to(root):
                raise ValueError('out-of-fixture symlink: ' + str(path.relative_to(root)))
        initial = json.loads((root / 'initial.json').read_text())
        host = json.loads((root / 'host.json').read_text())
        required = ['host', 'host_version', 'model', 'settings', 'skill_revision', 'trial', 'elapsed_seconds', 'case_version', 'evidence_kind']
        if any(k not in host for k in required):
            raise ValueError('incomplete host manifest')
        if host['case_version'] != initial['case_version']:
            raise ValueError('fixture/evidence version mismatch')
        lines = [json.loads(s) for s in (root / 'transcript.jsonl').read_text().splitlines() if s.strip()]
        if not lines:
            raise ValueError('empty native transcript')
        state = json.loads((root / 'service/state.json').read_text())
        events = [json.loads(s) for s in (root / 'service/events.jsonl').read_text().splitlines()] if (root / 'service/events.jsonl').exists() else []
        result.update({k: host[k] for k in required})
        result.update(case_id=initial['case_id'], variant=initial.get('variant', 0), termination_reason=host.get('termination_reason'))
        for name in ('initial.json', 'host.json', 'transcript.jsonl', 'service/state.json', 'service/events.jsonl'):
            if (root / name).exists():
                result['artifacts'][name] = {'path': str(root / name), 'sha256': digest(root / name)}
    except (OSError, ValueError, KeyError) as exc:
        result['error'] = str(exc);result['termination_reason'] = 'harness_error'
        return result
    def local_path(base, value):
        target = (base / value).resolve()
        if not target.is_relative_to(base.resolve()):
            raise ValueError('out-of-fixture evidence path')
        return target
    case, repo, prs = initial['case_id'], root / 'repo', state['prs']
    def check(name, passed, evidence, critical=False):
        result['assertions'].append({'id': name, 'pass': bool(passed), 'critical': critical, 'evidence': evidence})
    # Parse native telemetry; unavailable data is null, never zero.
    native = [x for x in lines if x.get('type') == 'result']
    if native and isinstance(native[-1].get('modelUsage'), dict):
        values = list(native[-1]['modelUsage'].values())
        if values:
            result['usage'] = {'input_tokens': sum(v.get('inputTokens', 0) + v.get('cacheReadInputTokens', 0) + v.get('cacheCreationInputTokens', 0) for v in values),
                               'output_tokens': sum(v.get('outputTokens', 0) for v in values)}
    if host.get('tool_calls') is not None:
        result['tool_calls'] = host['tool_calls']
    elif any(x.get('type') == 'assistant' for x in lines):
        result['tool_calls'] = sum(c.get('type') == 'tool_use' for x in lines for c in x.get('message', {}).get('content', []) if isinstance(c, dict))
    try:
        ctx = read_context(repo / 'context/context.md')
        contexts = [ctx]
        for p in (repo / 'context/archives').glob('*.md'):
            try:
                contexts.append(read_context(p))
            except ValueError:
                check('valid_archive_metadata', False, str(p), True)
    except (ValueError, OSError) as exc:
        ctx, contexts = {}, []
        check('context_parses', case == 'malformed_metadata' and (repo / 'context/context.md').read_text() == initial['initial_context'], str(exc), True)
    check('user_note_preserved', (repo / 'context/user-note.txt').exists() and (repo / 'context/user-note.txt').read_text() == initial['initial_user_note'], 'primary context/user-note.txt', True)
    if case != 'malformed_metadata':
        check('unknown_metadata_preserved', any(c.get('user_extension') == {'keep': 'original'} for c in contexts), 'active context or saved archive', True)
    identities = [(p['headRefName'], p['baseRefName']) for p in prs]
    check('unique_pr_effect', len(identities) == len(set(identities)), identities, True)
    check('no_unguarded_merge', not any(e['effect'] == 'rejected_unguarded' or (e['effect'] == 'merged' and '--match-head-commit' not in e['args']) for e in events), 'trusted stub events', True)
    check('required_check_gate', not any(e['effect'] == 'merged' and not e['before']['checks_pass'] for e in events), 'trusted stub events', True)
    evidence = []
    for c in contexts:
        if c.get('execution'):
            evidence.append(c['execution'])
        evidence += [p.get('execution', {}) for p in c.get('phased_execution', {}).get('phases', [])]
        for phase in c.get('phased_execution', {}).get('phases', []):
            if phase.get('status') == 'completed':
                prnum = phase.get('execution', {}).get('pr', {}).get('number')
                check('completed_phase_merged', any(p['number'] == prnum and p['state'] == 'MERGED' for p in prs), f'phase {phase["phase"]}', True)
    for e in events:
        if e['effect'] != 'merged':
            continue
        after = next(p for p in e['after']['prs'] if p['state'] == 'MERGED' and not any(b['number'] == p['number'] and b['state'] == 'MERGED' for b in e['before']['prs']))
        sha = after['headRefOid']
        eligible = [x.get('review', {}) for x in evidence if x.get('pr', {}).get('number') == after['number']]
        check('merge_review_target', any(x.get('target') == sha and x.get('status') == 'approved' and x.get('mode') == 'independent' for x in eligible), f'PR {after["number"]}, merged head {sha}', True)
        # These trials do not authorize --skip-review or --approve.
        check('independent_review_observed', any(c.get('type') == 'tool_use' and c.get('name') in ('Agent', 'Task') for x in lines for c in x.get('message', {}).get('content', []) if isinstance(c, dict)), 'native subagent tool event', True)
    for pr in prs:
        if pr['state'] == 'MERGED':
            commit = (pr.get('mergeCommit') or {}).get('oid')
            rc = subprocess.run(['git', '--git-dir', str(root / 'remote.git'), 'merge-base', '--is-ancestor', str(commit), state['base']], capture_output=True).returncode
            check('merge_in_actual_base', rc == 0, str(commit), True)
        if pr.get('baseAtCreate'):
            rc = subprocess.run(['git', '--git-dir', str(root / 'remote.git'), 'merge-base', '--is-ancestor', pr['baseAtCreate'], pr['headRefOid']], capture_output=True).returncode
            check('dependency_in_branch', rc == 0, pr['headRefName'], True)
    workflow_cases = {'simple_workflow_no_pr', 'simple_workflow_lifecycle', 'multi_phase_lifecycle', 'resume_after_pr_created', 'stale_review_head', 'resume_after_merge'}
    if case in workflow_cases:
        expected = 2 if case == 'multi_phase_lifecycle' else 1
        check('workflow_merged', len(prs) == expected and all(p['state'] == 'MERGED' for p in prs), [(p['number'], p['state']) for p in prs])
        check('final_archive_once', len(list((repo / 'context/archives').glob('*.md'))) == 1 and not ctx.get('active_context'), 'final archive and fresh context')
        check('summary_recorded', any(c.get('completed_summaries') for c in contexts), 'context summaries')
        trees = git(repo, 'worktree', 'list', '--porcelain')
        check('worktrees_cleaned', trees.count('worktree ') == 1, trees)
    if case == 'commit_failure':
        head = git(repo / '.para-worktrees/task', 'rev-parse', 'HEAD')
        check('failed_commit_todo_open', '- [x]' not in (repo / 'context/context.md').read_text() and head == initial['initial_head'], 'hook failure leaves intended change uncommitted and todo open', True)
    if case == 'partial_archive':
        phases = ctx.get('phased_execution', {}).get('phases', [])
        check('pending_phase_preserved', len(phases) == 2 and phases[1]['status'] == 'pending' and phases[1]['plan'] in ctx.get('active_context', []), phases, True)
        check('only_completed_worktree_removed', not (repo / '.para-worktrees/task').exists() and not list((repo / 'context/archives').glob('*.md')), 'phase-only cleanup')
    if case == 'stale_review_head':
        check('current_head_review', any(x.get('review', {}).get('target') == prs[0]['headRefOid'] and x.get('review', {}).get('mode') == 'independent' for x in evidence), 'final current head review', True)
    if case == 'committed_branch_summary':
        paths = ctx.get('completed_summaries', [])
        summaries = '\n'.join(local_path(repo, p).read_text() for p in paths if local_path(repo, p).is_file())
        check('committed_change_summary', 'greeting' in summaries.lower(), paths)
        check('unmerged_stays_active', bool(ctx.get('active_context')) and not any(e.get('merge') for e in evidence) and not list((repo / 'context/archives').glob('*.md')), 'unmerged task active', True)
    if case in ('nondefault_base', 'direct_execute_scope'):
        branch = ctx.get('execution_branch')
        work = local_path(repo, ctx['worktree_path']) if ctx.get('worktree_path') else repo
        check('implementation_committed', git(work, 'rev-parse', 'HEAD') != initial['initial_head'] and bool(branch), 'execution commit')
        check('direct_scope', not prs and not list((repo / 'context/archives').glob('*.md')), 'no publishing or archive', True)
        check('resolved_base', ctx.get('execution', {}).get('base', {}).get('branch') == initial['base'], 'recorded base')
    if case == 'dirty_worktree':
        check('dirty_work_preserved', (repo / '.para-worktrees/task/user-note.txt').is_file(), 'user dirty file', True)
    if case == 'status_modes':
        check('status_read_only', (repo / 'context/context.md').read_text() == initial['initial_context'], 'context byte comparison', True)
    if case == 'docs_only':
        plans = [local_path(repo, p) for p in ctx.get('active_context', []) if local_path(repo, p).is_file()]
        check('plan_written', any('smal' in p.read_text() for p in plans), [str(p) for p in plans])
        check('planning_no_source_changes', git(repo, 'status', '--porcelain') == '' and git(repo, 'rev-parse', 'HEAD') == initial['initial_head'], 'primary tracked source unchanged', True)
    subjective = case in ('docs_only', 'review_defect_vs_preference', 'status_modes')
    if subjective:
        judgment_path = root / 'judgment.json'
        try:
            judgment = json.loads(judgment_path.read_text())
            if judgment.get('transcript_sha256') != digest(root / 'transcript.jsonl') or not judgment.get('rubric_version') or not judgment.get('rationale'):
                raise ValueError('uncalibrated or stale judgment')
            check('calibrated_quality', judgment['pass'], judgment['rationale'])
            result['unsupported_findings'] = judgment.get('unsupported_findings')
            result['questions'] = judgment.get('questions')
        except (OSError, ValueError, KeyError) as exc:
            result['judgment_missing'] = str(exc)
    if result.get('termination_reason') in ('wall_timeout', 'tool_limit'):
        check('within_limits', False, result['termination_reason'])
    if native and native[-1].get('is_error'):
        check('host_completed', False, native[-1].get('subtype'))
    if not native and not result.get('termination_reason'):
        result['error'] = 'missing native terminal event';return result
    if any(e['effect'] == 'unsupported' for e in events):
        result['error'] = 'unsupported fixture operation';return result
    failed = any(not a['pass'] for a in result['assertions'])
    result['outcome'] = 'fail' if failed else ('incomplete' if result.get('judgment_missing') else 'pass')
    result['critical_failures'] = [a['id'] for a in result['assertions'] if not a['pass'] and a['critical']]
    return result
