#!/usr/bin/env python3
"""Run one real Claude CLI trial inside Docker with fixture-only mounts and model-only egress."""
import argparse
import hashlib
import io
import json
import os
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

SOURCE = Path(__file__).resolve().parents[1]
IMAGE = 'para-skill-eval:claude-2.1.289'


def docker(*args, check=True):
    return subprocess.run(['docker', *args], capture_output=True, text=True, check=check)


def capture_and_stop(command, path, limits, agent):
    try:
        return run_bounded(command, path, limits['wall_seconds'], limits['tool_calls'])
    finally:
        # Stop the container itself, not only its attached Docker client.
        docker('rm', '-f', agent, check=False)


def run(args):
    if not os.environ.get('ANTHROPIC_BASE_URL', '').startswith('https://'):
        raise ValueError('Set the authorized HTTPS model endpoint before running trials')
    if args.case not in SUPPORTED:
        raise ValueError('case lacks validated live fixture/grader coverage')
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
    (root / 'transcript.jsonl').touch()
    (root / 'service').chmod(0o777)
    for p in (root / 'service').iterdir():
        p.chmod(0o666)
    name = 'para-eval-' + uuid.uuid4().hex[:12]
    network, gateway, agent = name + '-net', name + '-gateway', name + '-agent'
    limits = {'wall_seconds': 1800 if args.case == 'multi_phase_lifecycle' else 1200 if args.case == 'simple_workflow_lifecycle' else 600,
              'tool_calls': 300 if args.case == 'multi_phase_lifecycle' else 200 if args.case == 'simple_workflow_lifecycle' else 100}
    harness_files = sorted(p for p in (SOURCE / 'tests/behavior').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    harness_files += [SOURCE / 'scripts' / name for name in ('run-skill-trial.py', 'evaluate-skills.py', 'measure-skill-context.py')]
    harness_hash = hashlib.sha256(b''.join(p.read_bytes() for p in harness_files)).hexdigest()
    settings = {'limits': limits, 'effort': 'low', 'model': args.model, 'safe_mode': True,
                'isolation': 'docker-internal-network-model-connect-proxy', 'harness_sha256': harness_hash,
                'skill_loading': 'explicit body/resource reads; metadata model hints not applied', 'image': docker('image', 'inspect', IMAGE, '--format', '{{.Id}}').stdout.strip()}
    manifest = {'host': 'claude-code', 'host_version': '2.1.289', 'model': args.model, 'settings': settings,
                'skill_revision': revision, 'trial': args.trial, 'case_version': initial['case_version'],
                'evidence_kind': 'native_agent', 'elapsed_seconds': 0, 'termination_reason': 'harness_error',
                'installed_resources': {str(p.relative_to(skills)): hashlib.sha256(p.read_bytes()).hexdigest() for p in skills.rglob('*') if p.is_file()}}
    base = ['run', '--rm', '--name', agent, '--network', network, '--cap-drop=ALL', '--security-opt=no-new-privileges',
            '--pids-limit', '256', '--memory', '2g', '--cpus', '2',
            '--mount', f'type=bind,source={root / "repo"},target={root / "repo"}',
            '--mount', f'type=bind,source={root / "remote.git"},target={root / "remote.git"}',
            '--mount', f'type=bind,source={skills},target=/opt/para-instructions,readonly',
            '--mount', f'type=bind,source={SOURCE / "tests/behavior/host/gh"},target=/usr/local/bin/gh,readonly',
            '--workdir', str(root / 'repo'), '-e', 'ANTHROPIC_BASE_URL', '-e', 'ANTHROPIC_AUTH_TOKEN',
            '-e', 'ANTHROPIC_API_KEY', '-e', 'HTTPS_PROXY=http://gateway:8080', '-e', 'HTTP_PROXY=http://gateway:8080',
            '-e', 'NO_PROXY=gateway,localhost,127.0.0.1', '-e', 'CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1', IMAGE]
    start = time.monotonic()
    try:
        docker('network', 'create', '--internal', network)
        docker('run', '-d', '--name', gateway, '--user', '1001', '--network', 'bridge', '--cap-drop=ALL',
               '--security-opt=no-new-privileges',
               '--mount', f'type=bind,source={root / "repo"},target={root / "repo"},readonly',
               '--mount', f'type=bind,source={root / "remote.git"},target={root / "remote.git"}',
               '--mount', f'type=bind,source={root / "service"},target={root / "service"}',
               '--mount', f'type=bind,source={root / "transcript.jsonl"},target={root / "transcript.jsonl"},readonly',
               '--mount', f'type=bind,source={SOURCE / "tests/behavior"},target=/harness,readonly',
               '-e', 'ANTHROPIC_BASE_URL', IMAGE, 'python3', '/harness/host/gateway.py', str(root))
        docker('network', 'connect', '--alias', 'gateway', network, gateway)
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
        preflight = docker(*base, 'python3', '-c', probe)
        if 'ISOLATION_OK' not in preflight.stdout:
            raise ValueError('isolation preflight failed')
        (root / 'isolation.txt').write_text(preflight.stdout)
        methodology = (skills / 'resources/AGENTS.md').read_text()
        system = methodology + '\nEvaluation environment: The primary checkout is ' + str(root / 'repo') + '. '
        system += 'All PARA skills are under /opt/para-instructions/skills. Read the named SKILL.md and applicable resources to carry out requests. '
        system += 'Use the configured model for all subagents. Skills are instructions, not shell commands. '
        system += 'The gh command is a local substitute; all Git remotes are local fixtures. No services outside this fixture are needed. '
        system += 'Native skills discovery and frontmatter model switching are disabled in this fixed-model evaluation. '
        prompt = 'Use an independent Agent subagent to return HOST_OK, then report whether delegation succeeded. Do not change files.' if args.probe else initial['prompt']
        manifest['evidence_kind'] = 'host_capability_probe' if args.probe else 'native_agent'
        command = ['docker', *base, 'claude', '--safe-mode', '--setting-sources', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
                   '--tools', 'Task,Bash,Read,Edit,Write', '--no-session-persistence', '--dangerously-skip-permissions', '--model', args.model, '--effort', 'low',
                   '--print', '--output-format', 'stream-json', '--verbose', '--forward-subagent-text',
                   '--append-system-prompt', system, prompt]
        observed = capture_and_stop(command, root / 'transcript.jsonl', limits, agent)
        manifest.update(observed)
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
        # Names are generated by this invocation; never stop unrelated containers.
        docker('rm', '-f', agent, check=False);docker('rm', '-f', gateway, check=False)
        docker('network', 'rm', network, check=False)
        dump(root / 'host.json', manifest)
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', required=True);p.add_argument('--out', required=True)
    p.add_argument('--revision', required=True);p.add_argument('--trial', type=int, required=True)
    p.add_argument('--probe', action='store_true');p.add_argument('--variant', type=int, default=0);p.add_argument('--model', default='claude-sonnet-5-5')
    args = p.parse_args()
    try:
        result = run(args)
        print(json.dumps({k: result.get(k) for k in ('skill_revision', 'elapsed_seconds', 'termination_reason', 'tool_calls', 'exit_code')}))
        return 0 if result.get('exit_code') == 0 and not result['termination_reason'] else 1
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(type(exc).__name__ + ': ' + str(exc), file=sys.stderr);return 2


if __name__ == '__main__':
    raise SystemExit(main())
