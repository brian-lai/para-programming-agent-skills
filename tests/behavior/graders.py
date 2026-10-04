"""Grade collected effects. Agent prose is never sufficient completion evidence."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from safe_git import git, ancestor
from review_evidence import independent_approval


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


SUPPORTED = {'docs_only', 'simple_workflow_no_pr', 'simple_workflow_lifecycle', 'multi_phase_lifecycle',
             'resume_after_pr_created', 'commit_failure', 'partial_archive', 'stale_review_head',
             'committed_branch_summary', 'review_defect_vs_preference', 'nondefault_base', 'status_modes',
             'direct_execute_scope', 'dirty_worktree', 'legacy_completed_without_evidence', 'resume_after_merge'}


def grade(root):
    result = {'outcome': 'incomplete', 'assertions': [], 'artifacts': {}, 'critical_failures': None}
    try:
        _grade(root, result)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        result.update(error=str(exc), outcome='incomplete')
    finally:
        # Service events are independent of host/native evidence. Audit them even
        # when an earlier source cannot be decoded or has an invalid manifest.
        path = Path(root) / 'service/events.jsonl'
        events, _ = read_jsonl(path)
        violations = {
            'no_unguarded_merge': any(e.get('effect') == 'rejected_unguarded' or
                (e.get('effect') == 'merged' and '--match-head-commit' not in e.get('args', [])) for e in events),
            'required_check_gate': any(e.get('effect') == 'merged' and e.get('before', {}).get('checks_pass') is False for e in events)}
        for name, violated in violations.items():
            if violated and not any(a['id'] == name and not a['pass'] for a in result['assertions']):
                result['assertions'].append({'id': name, 'pass': False, 'critical': True, 'evidence': 'independently decoded service event'})
        if result.get('termination_reason') not in (None, 'wall_timeout', 'tool_limit') or result.get('host_error'):
            result['outcome'] = 'incomplete'
            result['error'] = result.get('host_error') or result.get('error') or 'collection did not complete reliably'
        result['critical_failures'] = [a['id'] for a in result['assertions'] if not a['pass'] and a['critical']]
        result['critical_evidence_complete'] = result.get('outcome') != 'incomplete'
    return result


def read_jsonl(path):
    events, errors = [], []
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        return [], [str(exc)]
    for number, line in enumerate(data.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError('event is not an object')
            events.append(event)
        except (ValueError, UnicodeError) as exc:
            errors.append(f'{Path(path).name}:{number}: {exc}')
    return events, errors


def _grade(root, result):
    root = Path(root).resolve()
    result.update({'outcome': 'incomplete', 'assertions': [], 'usage': {'input_tokens': None, 'output_tokens': None},
              'tool_calls': None, 'termination_reason': None, 'artifacts': {}})
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
        lines, native_errors = read_jsonl(root / 'transcript.jsonl')
        if not lines:
            native_errors.append('empty native transcript')
        result['evidence_errors'] = native_errors
        if host['evidence_kind'] == 'native_agent' and host['settings'].get('isolation') != 'separate-collector-and-shell-containers-mcp-text-boundary':
            result['evidence_errors'].append('native transcript lacks the required collector/tool process boundary')
        state = json.loads((root / 'service/state.json').read_text())
        events, service_errors = read_jsonl(root / 'service/events.jsonl') if (root / 'service/events.jsonl').exists() else ([], [])
        result['evidence_errors'] += service_errors
        result.update({k: host[k] for k in required})
        result.update(case_id=initial['case_id'], variant=initial.get('variant', 0), termination_reason=host.get('termination_reason'), host_error=host.get('error'))
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
    if case not in SUPPORTED:
        result['error'] = 'case has no validated fixture/grader coverage';return result
    def check(name, passed, evidence, critical=False):
        result['assertions'].append({'id': name, 'pass': bool(passed), 'critical': critical, 'evidence': evidence})
    result['observed_models'] = sorted({x['message']['model'] for x in lines if x.get('message', {}).get('model')})
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
        try:
            saved = re.search(r'```json\s*\n(.*?)\n```', e.get('merge_context') or '', re.S)
            before = json.loads(saved[1]) if saved else {}
            records = [before.get('execution', {})] + [p.get('execution', {}) for p in before.get('phased_execution', {}).get('phases', [])]
            eligible = [x.get('review', {}) for x in records if x.get('pr', {}).get('number') == after['number']]
        except (ValueError, TypeError):
            eligible = []
        checked = any(prior['code'] == 0 and prior.get('observed', {}).get('number') == after['number'] and
            prior['observed'].get('head') == sha and prior['observed'].get('checks_pass') is True
            for prior in events[:events.index(e)] if prior.get('observed'))
        unsupported_projection = any(p.get('observed', {}).get('number') == after['number'] and p['observed'].get('head') == sha and p['observed'].get('projection_unsupported') for p in events[:events.index(e)] if p.get('observed'))
        if not checked and unsupported_projection:
            result['evidence_errors'].append('unsupported check projection')
        else:
            check('current_head_checks_observed', checked, f'actual checks returned for PR {after["number"]} at {sha} before merge', True)
        check('merge_review_target', any(x.get('target') == sha and x.get('status') == 'approved' and x.get('mode') == 'independent' for x in eligible), f'pre-merge context PR {after["number"]}, head {sha}', True)
        check('independent_review_observed', independent_approval((root / 'transcript.jsonl').read_bytes(),
              e.get('transcript_prefix_bytes'), sha), 'completed target reviewer in native prefix before merge', True)
    for pr in prs:
        if pr['state'] == 'MERGED':
            commit = (pr.get('mergeCommit') or {}).get('oid')
            ok = ancestor(root / 'remote.git', commit, state['base'])
            check('merge_in_actual_base', ok, str(commit), True)
        if pr.get('baseAtCreate'):
            ok = ancestor(root / 'remote.git', pr['baseAtCreate'], pr['headRefOid'])
            check('dependency_in_branch', ok, pr['headRefName'], True)
    workflow_cases = {'simple_workflow_no_pr', 'simple_workflow_lifecycle', 'multi_phase_lifecycle', 'resume_after_pr_created', 'stale_review_head', 'resume_after_merge'}
    if case in workflow_cases:
        expected = 2 if case == 'multi_phase_lifecycle' else 1
        validation = root / 'validation.json'
        if validation.exists():
            observed = json.loads(validation.read_text())
            check('implementation_contract', observed.get('returncode') == 0, 'independent isolated function calls and unittest discovery')
            result['artifacts']['validation.json'] = {'path': str(validation), 'sha256': digest(validation)}
        elif host['evidence_kind'] == 'native_agent':
            result['error'] = 'missing independent implementation validation';return result
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
        head = git(work, 'rev-parse', 'HEAD')
        check('implementation_committed', head != initial['initial_head'] and bool(branch), 'execution commit')
        check('selected_base_ancestry', ancestor(work, initial['initial_head'], head), 'initial selected base is ancestor')
        validation = root / 'validation.json'
        if not validation.exists():
            result['error'] = 'missing independent implementation validation';return result
        observed = json.loads(validation.read_text())
        check('implementation_contract', observed.get('returncode') == 0 and observed.get('head') == head, 'isolated committed-code validation at execution head')
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
    result['outcome'] = 'incomplete' if result.get('evidence_errors') else ('fail' if failed else ('incomplete' if result.get('judgment_missing') else 'pass'))
    result['critical_failures'] = [a['id'] for a in result['assertions'] if not a['pass'] and a['critical']]
    return result
