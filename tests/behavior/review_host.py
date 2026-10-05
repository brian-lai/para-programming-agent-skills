"""Trusted Docker boundary configuration; no model-selected mounts or routing."""
import json
import time


def worker_arguments(root, source, image, name, network):
    return ['run', '-d', '--name', name, '--user', '1001', '--network', network,
        '--network-alias', 'review-worker', '--read-only', '--cap-drop=ALL',
        '--security-opt=no-new-privileges', '--pids-limit', '64', '--memory', '512m', '--cpus', '1',
        '--tmpfs', '/tmp:rw,noexec,nosuid,size=268435456,uid=1001,gid=1001',
        '--mount', f'type=bind,source={root / "review-capsules"},target=/review-capsules,readonly',
        '--mount', f'type=bind,source={root / "instructions"},target=/opt/para-instructions,readonly',
        '--mount', f'type=bind,source={source / "tests/behavior/host/worker.py"},target=/worker.py,readonly',
        '--mount', f'type=bind,source={source / "tests/behavior/host/review-worker.py"},target=/review-worker.py,readonly',
        '--workdir', '/tmp', image, 'python3', '/review-worker.py']


def validate_worker(info, network, root, source):
    config, host = info['Config'], info['HostConfig']
    expected = {'/review-capsules': str(root / 'review-capsules'), '/opt/para-instructions': str(root / 'instructions'),
        '/worker.py': str(source / 'tests/behavior/host/worker.py'), '/review-worker.py': str(source / 'tests/behavior/host/review-worker.py')}
    mounts = info['Mounts']
    if ({m['Destination']: m['Source'] for m in mounts if m.get('Type', 'bind') == 'bind'} != expected
            or any(m['RW'] for m in mounts if m['Destination'] != '/tmp')
            or any(m['Destination'] not in {*expected, '/tmp'} for m in mounts)
            or set(info['NetworkSettings']['Networks']) != {network}
            or config['User'] != '1001' or not host['ReadonlyRootfs']
            or host.get('CapDrop') != ['ALL'] or host.get('SecurityOpt') != ['no-new-privileges']
            or host.get('Memory') != 536870912 or host.get('PidsLimit') != 64
            or host.get('Tmpfs') != {'/tmp': 'rw,noexec,nosuid,size=268435456,uid=1001,gid=1001'}
            or any(e.split('=', 1)[0].startswith(('ANTHROPIC_', 'HTTP_PROXY', 'HTTPS_PROXY')) for e in config.get('Env', []))):
        raise ValueError('review worker boundary differs from required configuration')


def ready(docker, container, port):
    code = f'import socket; socket.create_connection(("127.0.0.1", {port}), timeout=1).close()'
    end = time.monotonic() + 10
    while time.monotonic() < end:
        result = docker('exec', container, 'python3', '-c', code, check=False)
        if result.returncode == 0:
            return
        time.sleep(.1)
    raise ValueError('worker readiness timed out: ' + container)


def preflight(docker, reviewer, network, author_network, root, source, forbidden):
    info = json.loads(docker('inspect', reviewer).stdout)[0]
    validate_worker(info, network, root, source)
    networks = [json.loads(docker('network', 'inspect', n).stdout)[0] for n in (network, author_network)]
    if not all(n['Internal'] for n in networks):
        raise ValueError('review and author networks must be internal')
    # Test direct addresses as well as aliases: DNS separation alone is insufficient.
    code = '''import json, subprocess, sys
probe = 'import socket,sys;socket.create_connection((sys.argv[1],int(sys.argv[2])),timeout=.5).close()'
for host, port in json.loads(sys.argv[1]):
 try:
  result = subprocess.run([sys.executable, '-c', probe, host, str(port)], capture_output=True, timeout=2)
 except subprocess.TimeoutExpired: continue  # Bound DNS resolution too.
 if result.returncode == 0:
  raise SystemExit('Unexpected reviewer network access: ' + host)
print('REVIEW_NETWORK_OK')'''
    addresses = [['gateway', 8080], ['worker', 8090], ['1.1.1.1', 443], *forbidden]
    result = docker('exec', reviewer, 'python3', '-c', code, json.dumps(addresses))
    if 'REVIEW_NETWORK_OK' not in result.stdout:
        raise ValueError('review network probe failed')
    return {'version': 1, 'status': 'verified', 'container': reviewer, 'network': network,
            'mounts': info['Mounts'], 'host_config': {k: info['HostConfig'][k] for k in ('ReadonlyRootfs', 'CapDrop', 'SecurityOpt', 'Memory', 'PidsLimit', 'Tmpfs')},
            'networks': list(info['NetworkSettings']['Networks']), 'blocked_addresses': addresses}
