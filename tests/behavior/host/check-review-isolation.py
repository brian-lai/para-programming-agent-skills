#!/usr/bin/env python3
"""Explicit credentials-free acceptance probe of the actual review container boundary."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import uuid
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fixtures import prepare, git
from review_isolation import prepare_review, file_manifest
from review_host import worker_arguments, ready, preflight

SOURCE = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('runner', SOURCE / 'scripts/run-skill-trial.py')
runner = importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


def probe_review_isolation(destination):
    root = Path(destination).resolve()
    prepare('resume_after_pr_created', root)
    (root / 'instructions').mkdir()
    state = json.loads((root / 'service/state.json').read_text())
    head = state['prs'][0]['headRefOid']
    git(root / 'remote.git', 'update-ref', 'refs/heads/para/task-phase-1', head)
    capsule = prepare_review(root, {'mode': 'pr', 'pr_number': 1, 'expected_head': head})
    # Host-created fixture readability; production publisher and worker share uid 1001.
    for p in (root / 'review-capsules').rglob('*'):
        p.chmod(0o755 if p.is_dir() else 0o644)
    before = {name: file_manifest(root / name) for name in ('repo', 'remote.git', 'review-capsules')}
    stem = 'para-isolation-' + uuid.uuid4().hex[:10]
    author_net, review_net, author, reviewer = [stem + x for x in ('-author-net', '-review-net', '-author', '-reviewer')]
    result = {'version': 1, 'status': 'incomplete', 'review_id': capsule['review_id'], 'checks': {}}
    try:
        for n in (author_net, review_net):
            runner.docker('network', 'create', '--internal', n)
        runner.docker('run', '-d', '--name', author, '--network', author_net, '--network-alias', 'worker',
            '--cap-drop=ALL', '--security-opt=no-new-privileges', '--memory', '256m',
            runner.IMAGE, 'python3', '-m', 'http.server', '8090')
        ready(runner.docker, author, 8090)
        runner.docker(*worker_arguments(root, SOURCE, runner.IMAGE, reviewer, review_net))
        ready(runner.docker, reviewer, 8091)
        address = json.loads(runner.docker('inspect', author).stdout)[0]['NetworkSettings']['Networks'][author_net]['IPAddress']
        result['boundary'] = preflight(runner.docker, reviewer, review_net, author_net, root, SOURCE, [[address, 8090]])
        def command(label, code, expected=0, timeout=10):
            request = {'review_id': capsule['review_id'], 'command': code, 'timeout': timeout}
            client = '''import json,urllib.request,sys
r=urllib.request.Request('http://localhost:8091/execute',data=sys.argv[1].encode(),headers={'Content-Type':'application/json'})
print(urllib.request.urlopen(r,timeout=20).read().decode())'''
            response = json.loads(runner.docker('exec', reviewer, 'python3', '-c', client, json.dumps(request)).stdout)
            result['checks'][label] = response
            if (response['exit_code'] != 0 if expected == 'denied' else response['exit_code'] == expected):
                return response
            raise ValueError(label + ' unexpected result: ' + str(response))
        command('checkout_task', 'git checkout -q --detach para/task', 'denied')
        command('checkout_phase', 'git checkout -q --detach para/task-phase-1', 'denied')
        command('direct_write', 'echo mutation >> greeting.py', 'denied')
        command('python_write_restore', "python3 -c \"from pathlib import Path;p=Path('greeting.py');s=p.read_text();p.write_text('mutation');p.write_text(s)\"", 'denied')
        command('config_write', 'git config core.hooksPath /tmp/hooks', 'denied')
        command('hook_write', 'mkdir -p .git/hooks && echo mutation > .git/hooks/pre-commit', 'denied')
        command('alternate_write', 'mkdir -p .git/objects/info && echo /tmp/objects > .git/objects/info/alternates', 'denied')
        command('symlink_write', 'ln -s /tmp/escape .git/escape', 'denied')
        command('source_read', 'git rev-parse HEAD && git diff ' + capsule['base_sha'] + ' HEAD && cat greeting.py')
        command('scratch_tests', 'cp -R . /tmp/review-test && cd /tmp/review-test && python3 -m unittest discover -p "test_*.py"')
        absent = [str(root / 'repo'), str(root / 'remote.git'), '/var/run/docker.sock', '/review-evidence', '/harness']
        code = "import os;from pathlib import Path;assert not any(Path(p).exists() for p in " + repr(absent) + ");assert not any(k.startswith('ANTHROPIC_') for k in os.environ)"
        import shlex
        command('author_paths_and_credentials_absent', 'python3 -c ' + shlex.quote(code))
        command('scratch_symlink_escape', 'ln -s ' + shlex.quote(str(root / 'repo')) + ' /tmp/author-link && cat /tmp/author-link/greeting.py', 'denied')
        command('timeout_descendants', 'sleep 60 & wait', 124, timeout=1)
        command('no_surviving_child', "python3 -c \"from pathlib import Path;assert not any(p.read_bytes().startswith(b'sleep\\0') for p in Path('/proc').glob('[0-9]*/cmdline'))\"")
        command('scratch_quota', 'python3 -c "open(\'/tmp/too-large\',\'wb\').write(b\'x\' * (257*1024*1024))"', 'denied')
        command('root_read_only', 'touch /home/trial/mutation', 'denied')
        after = {name: file_manifest(root / name) for name in before}
        if before != after:
            raise ValueError('author state or capsule changed')
        result.update(status='verified', protected_files_unchanged=True)
    finally:
        errors = []
        for c in (reviewer, author):
            try:
                runner.stop_container(c)
            except Exception as exc:
                errors.append(str(exc))
        for n in (review_net, author_net):
            removed = runner.docker('network', 'rm', n, check=False)
            if removed.returncode:
                errors.append('could not remove ' + n)
        result['cleanup_confirmed'] = not errors
        if errors:
            result.update(status='cleanup_failed', cleanup_errors=errors)
        (root / 'probe.json').write_text(json.dumps(result, indent=2) + '\n')
        if errors:
            raise RuntimeError('acceptance probe cleanup failed')
    print(json.dumps({'status': result['status'], 'checks': len(result['checks']), 'out': str(root)}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('--out', required=True)
    probe_review_isolation(p.parse_args().out)
