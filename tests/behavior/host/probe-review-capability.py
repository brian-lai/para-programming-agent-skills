#!/usr/bin/env python3
"""Explicit native role probe with inert MCP tools; not a behavioral task trial."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_isolation import role_definitions, assess_role_probe, validate_review_capability
from comparison import run_bounded

SOURCE = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('trial_runner', SOURCE / 'scripts/run-skill-trial.py')
runner = importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


def run(destination, synthetic=False):
    root = Path(destination).resolve();root.mkdir(parents=True, exist_ok=False)
    if not synthetic and not os.environ.get('ANTHROPIC_BASE_URL', '').startswith('https://'):
        raise ValueError('authorized model endpoint is required')
    stem = 'para-role-probe-' + uuid.uuid4().hex[:10]
    net, gateway, collector = stem + '-net', stem + '-gateway', stem + '-collector'
    security = ['--cap-drop=ALL', '--security-opt=no-new-privileges', '--pids-limit', '128', '--memory', '1g']
    roles = role_definitions()
    (root / 'roles.json').write_text(json.dumps(roles, indent=2))
    mcp = {'mcpServers': {name: {'command': 'python3', 'args': ['/role-probe.py', name]} for name in ('fixture', 'review')}}
    prompt = '''This is a capability probe, not repository work. The MCP tools are inert and do not run commands.
1. Call mcp__fixture__Bash with command AUTHOR_CONTROL.
2. Attempt an Agent of subagent_type general-purpose once; record the actual rejection if disallowed.
3. Start a foreground para-reviewer. Its prompt must request a mcp__review__Bash call with command FOREGROUND_CONTROL, then actual attempts to invoke mcp__fixture__Bash with command FORBIDDEN_WRITER and Agent with subagent_type para-reviewer. Request actual tool calls even if the tools are absent, to test enforcement. Do not treat a prose claim as an observed rejection.
4. Start a background para-reviewer with the same requests, using command BACKGROUND_CONTROL for its allowed tool. Wait for completion.
Report which attempts were actually denied and which could not be attempted. Do not claim verified enforcement from compliance alone.'''
    result = {'evidence_kind': 'native_host_synthetic_model' if synthetic else 'host_capability_probe', 'host_version': '2.1.289', 'roles': roles,
              'model': 'claude-sonnet-5-5', 'status': 'incomplete',
              'image_id': runner.docker('image', 'inspect', runner.IMAGE, '--format', '{{.Id}}').stdout.strip()}
    try:
        runner.docker('network', 'create', '--internal', net)
        if synthetic:
            root.chmod(0o777)
            runner.docker('run', '-d', '--name', gateway, '--network', net, '--network-alias', 'model-probe', *security,
                '--mount', f'type=bind,source={SOURCE / "tests/behavior/host/role-probe-model.py"},target=/probe-model.py,readonly',
                '--mount', f'type=bind,source={root},target=/evidence', runner.IMAGE, 'python3', '/probe-model.py')
            auth = ['-e', 'ANTHROPIC_BASE_URL=http://model-probe:8080', '-e', 'ANTHROPIC_AUTH_TOKEN=probe-not-a-secret',
                    '-e', 'NO_PROXY=model-probe,localhost,127.0.0.1']
        else:
            runner.docker('run', '-d', '--name', gateway, '--network', 'bridge', *security,
                '--mount', f'type=bind,source={SOURCE / "tests/behavior"},target=/harness,readonly',
                '-e', 'ANTHROPIC_BASE_URL', runner.IMAGE, 'python3', '/harness/host/gateway.py', '/tmp/probe')
            runner.docker('network', 'connect', '--alias', 'gateway', net, gateway)
            auth = ['-e', 'ANTHROPIC_BASE_URL', '-e', 'ANTHROPIC_AUTH_TOKEN', '-e', 'ANTHROPIC_API_KEY',
                    '-e', 'HTTPS_PROXY=http://gateway:8080', '-e', 'HTTP_PROXY=http://gateway:8080',
                    '-e', 'NO_PROXY=gateway,localhost,127.0.0.1']
        command = ['docker', 'run', '--rm', '--name', collector, '--network', net, *security,
            '--mount', f'type=bind,source={SOURCE / "tests/behavior/host/role-probe-mcp.py"},target=/role-probe.py,readonly',
            *auth,
            '-e', 'CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-5-5', '-e', 'CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1',
            '-e', 'CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1', '-e', 'CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1',
            runner.IMAGE, 'claude', '--disable-slash-commands', '--setting-sources', '',
            '--strict-mcp-config', '--mcp-config', json.dumps(mcp), '--tools', 'Task',
            '--agents', json.dumps(roles), '--agent', 'para-author',
            '--allowedTools', 'mcp__fixture__Bash', 'mcp__review__Bash',
            '--no-session-persistence', '--dangerously-skip-permissions', '--model', 'claude-sonnet-5-5',
            '--effort', 'low', '--print', '--output-format', 'stream-json', '--verbose', '--forward-subagent-text', prompt]
        result.update(run_bounded(command, root / 'transcript.jsonl', 180, 40))
        result['status'] = 'captured' if result['exit_code'] == 0 else 'host_error'
        if synthetic and result['exit_code'] == 0 and not result.get('termination_reason'):
            native = [json.loads(line) for line in (root / 'transcript.jsonl').read_text().splitlines()]
            requests = [json.loads(line) for line in (root / 'model-events.jsonl').read_text().splitlines()]
            result['capability'] = assess_role_probe(native, requests)
            validate_review_capability(result['capability'])
            result['status'] = 'verified'

    finally:
        cleanup_errors = []
        for name in (collector, gateway):
            try:
                runner.stop_container(name)
            except Exception as exc:
                cleanup_errors.append(type(exc).__name__ + ': ' + str(exc))
        runner.docker('network', 'rm', net, check=False)
        if cleanup_errors:
            result.update(status='cleanup_failed', cleanup_errors=cleanup_errors)
        (root / 'probe.json').write_text(json.dumps(result, indent=2) + '\n')
        if cleanup_errors:
            raise RuntimeError('Could not confirm probe cleanup')
    print(json.dumps({'out': str(root), 'status': result['status'], 'exit_code': result.get('exit_code')}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('--out', required=True);p.add_argument('--synthetic-model', action='store_true')
    args = p.parse_args();run(args.out, args.synthetic_model)
