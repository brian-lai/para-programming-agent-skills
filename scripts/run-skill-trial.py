#!/usr/bin/env python3
"""Run one real Claude CLI trial inside Docker with fixture-only mounts and model-only egress."""
import argparse
import hashlib
import io
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tarfile
import time
import uuid
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests/behavior'))
from fixtures import prepare, dump
from comparison import run_bounded
from safe_git import snapshot, git
from graders import read_context, SUPPORTED
from review_isolation import role_definitions, assess_role_probe, validate_review_capability
from review_host import worker_arguments, ready, preflight

SOURCE = Path(__file__).resolve().parents[1]
IMAGE = 'para-skill-eval:claude-2.1.289'


def docker(*args, check=True):
    return subprocess.run(['docker', *args], capture_output=True, text=True, check=check)


def stop_container(name):
    docker('rm', '-f', name, check=False)
    # A failed remove may mean the --rm collector already exited. Confirm
    # absence with a successful daemon query; daemon failure is not absence.
    remaining = docker('ps', '-a', '--filter', 'name=^/' + name + '$', '--format', '{{.Names}}')
    if remaining.stdout.strip():
        raise RuntimeError('Container still exists after stop: ' + name)


def capture_and_stop(command, path, limits, *containers):
    try:
        return run_bounded(command, path, limits['wall_seconds'], limits['tool_calls'])
    finally:
        failures = []
        for name in containers:
            try:
                stop_container(name)
            except (RuntimeError, subprocess.SubprocessError) as exc:
                failures.append(str(exc))
        if failures:
            raise RuntimeError('Could not confirm containers stopped: ' + '; '.join(failures))


def validate_model_scope(events):
    models = sorted({e['message']['model'] for e in events if e.get('message', {}).get('model')})
    if len(models) != 1:
        raise ValueError('native model scope is missing or drifted: ' + ', '.join(models))
    return models


def run(args):
    if not os.environ.get('ANTHROPIC_BASE_URL', '').startswith('https://'):
        raise ValueError('Set the authorized HTTPS model endpoint before running trials')
    if args.case not in SUPPORTED:
        raise ValueError('case lacks validated live fixture/grader coverage')
    isolated = getattr(args, 'isolated_review', False)
    capability = None
    if isolated:
        probe_root = Path(args.capability_record).resolve().parent
        capability = json.loads((probe_root / 'probe.json').read_text())
        native = [json.loads(line) for line in (probe_root / 'transcript.jsonl').read_text().splitlines()]
        pools = [json.loads(line) for line in (probe_root / 'model-events.jsonl').read_text().splitlines()]
        validate_review_capability(assess_role_probe(native, pools))
        image = docker('image', 'inspect', IMAGE, '--format', '{{.Id}}').stdout.strip()
        if capability['status'] != 'verified' or capability['roles'] != role_definitions() or capability.get('image_id') != image:
            raise ValueError('capability probe does not match current roles/image')
    revision = subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', args.revision], text=True).strip()
    root = Path(args.out).resolve()
    initial = prepare(args.case, root, args.variant)
    skills = root / 'instructions';skills.mkdir()
    raw = subprocess.check_output(['git', '-C', str(SOURCE), 'archive', revision, 'skills', 'resources/AGENTS.md'])
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        for item in archive.getmembers():
            if not (skills / item.name).resolve().is_relative_to(skills) or item.issym() or item.islnk():
                raise ValueError('unexpected archive path')
        archive.extractall(skills)
    # Private temp parent stays owner-only on host. These isolated mounts must be writable by the container user.
    for mount in (root / 'repo', root / 'remote.git'):
        for p in [mount, *mount.rglob('*')]:
            if not p.is_symlink():
                p.chmod(0o777 if p.is_dir() or os.access(p, os.X_OK) else 0o666)
    if isolated:
        for folder in ('review-capsules', 'review-evidence'):
            (root / folder).mkdir();(root / folder).chmod(0o777)
        copied = root / 'review-evidence/capability';copied.mkdir()
        for filename in ('probe.json', 'transcript.jsonl', 'model-events.jsonl'):
            shutil.copyfile(probe_root / filename, copied / filename)
        dump(root / 'review-policy.json', {'version': 1, 'roles': role_definitions(), 'image_id': capability['image_id']})
        dump(root / 'review-boundary.json', {'status': 'pending'})
    (root / 'transcript.jsonl').touch()
    (root / 'service').chmod(0o777)
    for p in (root / 'service').iterdir():
        p.chmod(0o666)
    name = 'para-eval-' + uuid.uuid4().hex[:12]
    network, gateway, agent, worker = name + '-net', name + '-gateway', name + '-agent', name + '-worker'
    review_net, reviewer = name + '-review-net', name + '-reviewer'
    limits = {'wall_seconds': 1800 if args.case == 'multi_phase_lifecycle' else 1200 if args.case == 'simple_workflow_lifecycle' else 600,
              'tool_calls': 300 if args.case == 'multi_phase_lifecycle' else 200 if args.case == 'simple_workflow_lifecycle' else 100}
    harness_files = sorted(p for p in (SOURCE / 'tests/behavior').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    harness_files += [SOURCE / 'scripts' / name for name in ('run-skill-trial.py', 'evaluate-skills.py', 'measure-skill-context.py')]
    harness_hash = hashlib.sha256(b''.join(p.read_bytes() for p in harness_files)).hexdigest()
    settings = {'limits': limits, 'effort': 'low', 'model': args.model, 'safe_mode': False, 'setting_sources': [], 'native_skills': False, 'subagent_model_forced': True,
                'isolation': 'separate-collector-and-shell-containers-mcp-text-boundary', 'harness_sha256': harness_hash,
                'skill_loading': 'explicit body/resource reads; metadata model hints not applied', 'image': docker('image', 'inspect', IMAGE, '--format', '{{.Id}}').stdout.strip()}
    if isolated:
        settings.update(isolation='immutable-review-worker-v1', review_roles=role_definitions(), review_evidence_version=1)
    manifest = {'host': 'claude-code', 'host_version': '2.1.289', 'model': args.model, 'settings': settings,
                'skill_revision': revision, 'trial': args.trial, 'case_version': initial['case_version'],
                'evidence_kind': 'native_agent', 'elapsed_seconds': 0, 'termination_reason': 'harness_error',
                'installed_resources': {str(p.relative_to(skills)): hashlib.sha256(p.read_bytes()).hexdigest() for p in skills.rglob('*') if p.is_file()}}
    common = ['--network', network, '--cap-drop=ALL', '--security-opt=no-new-privileges',
              '--pids-limit', '256', '--memory', '2g', '--cpus', '2']
    worker_args = ['run', '-d', '--name', worker, '--network-alias', 'worker', *common,
            '--mount', f'type=bind,source={root / "repo"},target={root / "repo"}',
            '--mount', f'type=bind,source={root / "remote.git"},target={root / "remote.git"}',
            '--mount', f'type=bind,source={skills},target=/opt/para-instructions,readonly',
            '--mount', f'type=bind,source={SOURCE / "tests/behavior/host/gh"},target=/usr/local/bin/gh,readonly',
            '--mount', f'type=bind,source={SOURCE / "tests/behavior/host/worker.py"},target=/worker.py,readonly',
            '--workdir', str(root / 'repo'), IMAGE, 'python3', '/worker.py', str(root / 'repo')]
    # The CLI has no fixture mounts or shell/file tools. Its sole filesystem
    # adapter sends shell requests to a separate PID/mount namespace via MCP.
    base = ['run', '--rm', '--name', agent, *common,
            '--mount', f'type=bind,source={SOURCE / "tests/behavior/host/mcp.py"},target=/fixture-mcp.py,readonly',
            '--workdir', '/tmp', '-e', 'CLAUDE_CODE_SUBAGENT_MODEL=' + args.model, '-e', 'CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1', '-e', 'ANTHROPIC_BASE_URL', '-e', 'ANTHROPIC_AUTH_TOKEN',
            '-e', 'ANTHROPIC_API_KEY', '-e', 'HTTPS_PROXY=http://gateway:8080', '-e', 'HTTP_PROXY=http://gateway:8080',
            '-e', 'NO_PROXY=gateway,worker,localhost,127.0.0.1', '-e', 'CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1', IMAGE]
    if isolated:
        # Create then connect the second network before starting the collector.
        base[0] = 'create'
        base[-1:-1] = ['--mount', f'type=bind,source={SOURCE / "tests/behavior/host/review-mcp.py"},target=/review-mcp.py,readonly',
            '--mount', f'type=bind,source={root / "review-evidence"},target=/review-evidence',
            '-e', 'CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1']
    start = time.monotonic()
    try:
        docker('network', 'create', '--internal', network)
        if isolated:
            docker('network', 'create', '--internal', review_net)
        extra_gateway = []
        if isolated:
            for path, readonly in (('review-capsules', False), ('review-evidence', True), ('review-policy.json', True), ('review-boundary.json', True)):
                extra_gateway += ['--mount', f'type=bind,source={root / path},target={root / path}' + (',readonly' if readonly else '')]
        docker('run', '-d', '--name', gateway, '--user', '1001', '--network', 'bridge', '--cap-drop=ALL',
               '--security-opt=no-new-privileges', '--memory', '1g', '--pids-limit', '128', *extra_gateway,
               '--mount', f'type=bind,source={root / "repo"},target={root / "repo"},readonly',
               '--mount', f'type=bind,source={root / "remote.git"},target={root / "remote.git"}',
               '--mount', f'type=bind,source={root / "service"},target={root / "service"}',
               '--mount', f'type=bind,source={root / "transcript.jsonl"},target={root / "transcript.jsonl"},readonly',
               '--mount', f'type=bind,source={SOURCE / "tests/behavior"},target=/harness,readonly',
               '-e', 'ANTHROPIC_BASE_URL', IMAGE, 'python3', '/harness/host/gateway.py', str(root))
        docker('network', 'connect', '--alias', 'gateway', network, gateway)
        ready(docker, gateway, 8080)
        # Verify actual process isolation before giving an agent tools. No host directories or socket are mounted.
        probe = r'''import socket, urllib.request
try:
 socket.create_connection(("1.1.1.1",443),timeout=2)
 raise SystemExit("Direct egress unexpectedly allowed")
except OSError: pass
r=urllib.request.build_opener(urllib.request.ProxyHandler({}))
try:
 r.open("http://gateway:8080/not-an-operation",timeout=5)
except urllib.error.HTTPError as e:
 assert e.code == 404 or e.code == 501
print("ISOLATION_OK")'''
        docker(*worker_args)
        ready(docker, worker, 8090)
        author_preflight = docker('exec', worker, 'python3', '-c', probe)
        if 'ISOLATION_OK' not in author_preflight.stdout:
            raise ValueError('isolation preflight failed')
        (root / 'isolation.txt').write_text(author_preflight.stdout)
        if isolated:
            docker(*worker_arguments(root, SOURCE, IMAGE, reviewer, review_net))
            ready(docker, reviewer, 8091)
            forbidden = [[json.loads(docker('inspect', c).stdout)[0]['NetworkSettings']['Networks'][network]['IPAddress'], port] for c, port in ((worker, 8090), (gateway, 8080))]
            boundary = preflight(docker, reviewer, review_net, network, root, SOURCE, forbidden)
            dump(root / 'review-boundary.json', boundary)
        methodology = (skills / 'resources/AGENTS.md').read_text()
        system = methodology + '\nEvaluation environment: The primary checkout is ' + str(root / 'repo') + '. '
        system += 'All PARA skills are under /opt/para-instructions/skills. Read the named SKILL.md and applicable resources to carry out requests. '
        system += 'Use the configured model for all subagents. Skills are instructions, not shell commands. '
        system += 'The gh command is a local substitute; all Git remotes are local fixtures. No services outside this fixture are needed. '
        system += 'Use mcp__fixture__Bash for all shell and file operations; its cwd defaults to the primary checkout. Native Agent delegation remains available. '
        system += 'Native skills discovery and frontmatter model switching are disabled in this fixed-model evaluation. '
        if isolated:
            system += 'For independent reviews, use mcp__fixture__PrepareReview with the exact open PR number/full head (mode pr), or active plan paths (mode plan). Delegate only to para-reviewer, passing its returned review_id, target and review request. Its sole tool mcp__review__Bash starts in the immutable capsule source; ../packet contains copied context/plans and ../manifest.json identifies the target. Tests may use /tmp scratch. This host verifies read-only source and separate network enforcement. The author uses fixture tools. A changed PR head requires a new capsule and review. '
        prompt = 'Use mcp__fixture__Bash to print TOOL_OK. Then use an independent Agent subagent to run the same fixture tool printing HOST_OK, and report whether delegation and tool execution succeeded. Do not change files.' if args.probe else initial['prompt']
        manifest['evidence_kind'] = 'host_capability_probe' if args.probe else 'native_agent'
        mcp_config = json.dumps({'mcpServers': {'fixture': {'command': 'python3', 'args': ['/fixture-mcp.py']}}})
        if isolated:
            mcp_config = json.dumps({'mcpServers': {'fixture': {'command': 'python3', 'args': ['/fixture-mcp.py', '--author']}, 'review': {'command': 'python3', 'args': ['/review-mcp.py']}}})
        role_args = ['--agents', json.dumps(role_definitions()), '--agent', 'para-author'] if isolated else []
        allowed = ['mcp__fixture__Bash', 'mcp__fixture__PrepareReview', 'mcp__review__Bash'] if isolated else ['mcp__fixture__Bash']
        command = ['docker', *base, 'claude', '--disable-slash-commands', '--setting-sources', '', '--strict-mcp-config', '--mcp-config', mcp_config,
                   '--tools', 'Task', *role_args, '--allowedTools', *allowed, '--no-session-persistence', '--dangerously-skip-permissions', '--model', args.model, '--effort', 'low',
                   '--print', '--output-format', 'stream-json', '--verbose', '--forward-subagent-text',
                   '--append-system-prompt', system, prompt]
        if isolated:
            docker(*command[1:])
            docker('network', 'connect', review_net, agent)
            collector_info = json.loads(docker('inspect', agent).stdout)[0]
            if set(collector_info['NetworkSettings']['Networks']) != {network, review_net}:
                raise ValueError('collector network attachment mismatch')
            command = ['docker', 'start', '-a', agent]
        manifest['setup_seconds'] = time.monotonic() - start
        observed = capture_and_stop(command, root / 'transcript.jsonl', limits, agent, worker, *([reviewer] if isolated else []))
        if isolated:
            boundary['cleanup_confirmed'] = True
            dump(root / 'review-boundary.json', boundary)
        manifest.update(observed)
        inits, native_events = [], []
        for line in (root / 'transcript.jsonl').read_bytes().splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            native_events.append(event)
            if event.get('subtype') == 'init':
                inits.append(event)
        manifest['observed_models'] = validate_model_scope(native_events)
        manifest['native_tool_scopes'] = [e.get('tools', []) for e in inits]
        expected_tools = {'Task', 'mcp__fixture__Bash', 'mcp__fixture__PrepareReview'} if isolated else {'Task', 'mcp__fixture__Bash'}
        if not inits or any(set(e.get('tools', [])) != expected_tools for e in inits):
            raise ValueError('collector exposed unexpected native tool scope')
        manifest['builtin_plugins'] = inits[0].get('plugins', [])
        if args.case in ('simple_workflow_no_pr', 'simple_workflow_lifecycle', 'multi_phase_lifecycle', 'resume_after_pr_created', 'stale_review_head', 'resume_after_merge', 'nondefault_base', 'direct_execute_scope') and not args.probe:
            validator = name + '-validator'
            validation_repo = root / 'remote.git'
            validation_head = git(validation_repo, 'rev-parse', initial['base'])
            if args.case in ('nondefault_base', 'direct_execute_scope'):
                ctx = read_context(root / 'repo/context/context.md')
                validation_repo = (root / 'repo' / (ctx.get('worktree_path') or '')).resolve()
                if not validation_repo.is_relative_to(root / 'repo'):
                    raise ValueError('out-of-fixture validation path')
                validation_head = git(validation_repo, 'rev-parse', 'HEAD')
            trusted = root / 'validation.git';trusted.mkdir()
            snapshot(validation_repo, trusted)
            validation_code = '''import json, subprocess, sys
subprocess.run(['git', 'clone', '--no-checkout', sys.argv[1], '/tmp/validate-code'], check=True, capture_output=True)
subprocess.run(['git', '-C', '/tmp/validate-code', 'checkout', sys.argv[2]], check=True, capture_output=True)
from pathlib import Path
assert Path('/tmp/validate-code/test_greeting.py').is_file()
sys.path.insert(0, '/tmp/validate-code')
from greeting import greet
assert greet() == 'Hello from PARA.'
if sys.argv[3] == 'multi_phase_lifecycle':
 from farewell import farewell
 assert farewell() == 'Goodbye from PARA.'
r = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-p', 'test_*.py'], cwd='/tmp/validate-code', capture_output=True, text=True)
print(json.dumps({'returncode': r.returncode, 'output': r.stdout + r.stderr}))
sys.exit(r.returncode)'''
            try:
                check = subprocess.run(['docker', 'run', '--rm', '--name', validator, '--network', 'none',
                    '--cap-drop=ALL', '--security-opt=no-new-privileges', '--memory', '512m', '--pids-limit', '64',
                    '--mount', f'type=bind,source={trusted},target=/fixture.git,readonly',
                    IMAGE, 'python3', '-c', validation_code, '/fixture.git', validation_head, args.case],
                    capture_output=True, text=True, timeout=30)
                dump(root / 'validation.json', {'returncode': check.returncode, 'stdout': check.stdout, 'stderr': check.stderr,
                    'isolation': 'fresh container, no network or credentials, read-only bare remote', 'base': initial['base'], 'head': validation_head})
            finally:
                docker('rm', '-f', validator, check=False)
        manifest['isolation_sha256'] = hashlib.sha256((root / 'isolation.txt').read_bytes()).hexdigest()
    except Exception as exc:
        manifest.update(elapsed_seconds=time.monotonic() - start, termination_reason='harness_error', error=type(exc).__name__ + ': ' + str(exc))
        raise
    finally:
        # Confirm all owned containers stopped even when setup/capture failed.
        cleanup_start = time.monotonic()
        cleanup_errors = []
        for container in (agent, worker, gateway, *([reviewer] if isolated else [])):
            try:
                stop_container(container)
            except Exception as exc:
                cleanup_errors.append(str(exc))
        for owned_network in ([review_net, network] if isolated else [network]):
            docker('network', 'rm', owned_network, check=False)
            remaining = docker('network', 'ls', '--filter', 'name=^' + owned_network + '$', '--format', '{{.Name}}', check=False)
            if remaining.returncode or remaining.stdout.strip():
                cleanup_errors.append('Could not confirm network removal: ' + owned_network)
        manifest['cleanup_seconds'] = time.monotonic() - cleanup_start
        if cleanup_errors:
            manifest.update(termination_reason='harness_error', error='Cleanup: ' + '; '.join(cleanup_errors))
        if isolated and (root / 'review-boundary.json').exists():
            boundary = json.loads((root / 'review-boundary.json').read_text())
            boundary['cleanup_confirmed'] = not cleanup_errors
            dump(root / 'review-boundary.json', boundary)
        if isolated:
            protected = [root / 'review-policy.json', root / 'review-boundary.json', *(root / 'review-evidence').rglob('*.json'), *(root / 'review-evidence').rglob('*.jsonl'), *(root / 'review-capsules').glob('review-*/manifest.json')]
            manifest['review_artifacts'] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
        dump(root / 'host.json', manifest)
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', required=True);p.add_argument('--out', required=True)
    p.add_argument('--revision', required=True);p.add_argument('--trial', type=int, required=True)
    p.add_argument('--probe', action='store_true');p.add_argument('--variant', type=int, default=0);p.add_argument('--model', default='claude-sonnet-5-5')
    p.add_argument('--isolated-review', action='store_true');p.add_argument('--capability-record')
    args = p.parse_args()
    if args.isolated_review and not args.capability_record:
        p.error('--isolated-review requires --capability-record')
    try:
        result = run(args)
        print(json.dumps({k: result.get(k) for k in ('skill_revision', 'elapsed_seconds', 'termination_reason', 'tool_calls', 'exit_code')}))
        return 0 if result.get('exit_code') == 0 and not result['termination_reason'] else 1
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(type(exc).__name__ + ': ' + str(exc), file=sys.stderr);return 2


if __name__ == '__main__':
    raise SystemExit(main())
