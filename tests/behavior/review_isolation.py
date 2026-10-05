"""Contracts for the isolated reviewer host (not an installed-skill dependency)."""


def role_definitions():
    return {
        'para-author': {
            'description': 'Author and orchestrate the fixture task.',
            'prompt': 'Carry out the task using its instructions. Delegate independent reviews to para-reviewer.',
            'tools': ['Agent(para-reviewer)', 'mcp__fixture__Bash', 'mcp__fixture__PrepareReview'],
        },
        'para-reviewer': {
            'description': 'Independently review a supplied artifact using the isolated review tool.',
            'prompt': 'Review the supplied target independently. Use only mcp__review__Bash; return evidence and the reviewed target. Do not delegate further.',
            'tools': ['mcp__review__Bash'],
            'disallowedTools': ['Agent', 'Task', 'Bash', 'Read', 'Write', 'Edit', 'mcp__fixture__Bash'],
        },
    }


def validate_review_capability(evidence):
    required = ('foreground_restricted', 'background_restricted', 'unknown_agent_rejected',
                'nested_delegation_rejected', 'writer_tool_rejected')
    if evidence.get('version') != 1 or any(evidence.get(key) is not True for key in required):
        raise ValueError('review role restrictions are not verified')


def assess_role_probe(events, api_events):
    """Inspect actual native dispatch results from the synthetic-model CLI probe."""
    calls, results = {}, {}
    for event in events:
        for part in event.get('message', {}).get('content', []):
            if part.get('type') == 'tool_use':
                calls[part['id']] = (event.get('parent_tool_use_id'), part)
            elif part.get('type') == 'tool_result':
                results[part['tool_use_id']] = (event.get('parent_tool_use_id'), part)

    def denied(role, label, name, phrase):
        identifier = 'toolu_probe_' + role + '_' + label
        parent = None if role == 'author' else 'toolu_probe_author_' + role
        call = calls.get(identifier);response = results.get(identifier)
        return bool(call and response and call[0] == response[0] == parent and call[1].get('name') == name
                    and response[1].get('is_error') is True and phrase in str(response[1].get('content')))

    def restricted(role):
        pools = [set(row.get('tools', [])) for row in api_events if row.get('role') == role]
        identifier = 'toolu_probe_' + role + '_allowed'
        call = calls.get(identifier);response = results.get(identifier)
        return bool(pools and all(pool == {'mcp__review__Bash'} for pool in pools) and call and response
                    and call[0] == response[0] == 'toolu_probe_author_' + role
                    and call[1].get('name') == 'mcp__review__Bash' and not response[1].get('is_error'))

    return {'version': 1,
            'foreground_restricted': restricted('foreground'), 'background_restricted': restricted('background'),
            'unknown_agent_rejected': denied('author', 'unknown', 'Agent', "Agent type 'general-purpose' not found"),
            'nested_delegation_rejected': all(denied(role, 'nested', 'Agent', 'No such tool available: Agent') for role in ('foreground', 'background')),
            'writer_tool_rejected': all(denied(role, 'writer', 'mcp__fixture__Bash', 'No such tool available: mcp__fixture__Bash') for role in ('foreground', 'background'))}


def validate_review_record(record):
    import re
    if not isinstance(record, dict) or not all(isinstance(record.get(key), str) and record[key] for key in ('review_id', 'native_task_id', 'target')):
        raise ValueError('missing review, native task or target identity')
    if not re.fullmatch('[0-9a-f]{40}', record['target']):
        raise ValueError('PR target must be a full commit identity')




import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from safe_git import directory, read_file, snapshot, git

PACKET_FILE_LIMIT = 2 * 1024 * 1024
PACKET_LIMIT = 16 * 1024 * 1024
CAPSULE_LIMIT = 64 * 1024 * 1024
TRIAL_CAPSULE_LIMIT = 512 * 1024 * 1024
SCRATCH_LIMIT = 256 * 1024 * 1024


def regular_bytes(root, relative, limit):
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or any(x in ('..', '.') for x in path.parts):
        raise ValueError('invalid packet path')
    with directory(root) as base:
        parent = os.dup(base)
        try:
            for part in path.parts[:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
                os.close(parent);parent = child
            return read_file(parent, path.parts[-1], limit)
        finally:
            os.close(parent)


def decode_context(raw):
    match = re.search(rb'```json\s*\n(.*?)\n```', raw, re.S)
    data = json.loads(match[1]) if match else None
    if not isinstance(data, dict):
        raise ValueError('invalid primary context')
    return data


def trusted_git(source, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null', GIT_ATTR_NOSYSTEM='1', GIT_TERMINAL_PROMPT='0')
    return subprocess.run(['git', '-C', str(source), '-c', 'core.hooksPath=/dev/null',
        '-c', 'core.fsmonitor=false', '-c', 'protocol.allow=never', *args],
        env=env, capture_output=True, check=True, timeout=30).stdout


def file_manifest(root):
    values = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('capsule contains a symlink')
        if path.is_file():
            values[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise ValueError('capsule contains a special file')
    return values


def capture_git(remote, source, head, base, limit):
    source.mkdir();(source / '.git').mkdir()
    snapshot(remote, source / '.git', max_bytes=limit)
    trusted_git(source, 'fsck', '--strict', '--no-reflogs')
    for target in (head, base):
        trusted_git(source, 'cat-file', '-e', target + '^{commit}')
    tree = trusted_git(source, 'ls-tree', '-rlz', head)
    size = 0
    for entry in tree.split(b'\0'):
        if not entry:
            continue
        info, _ = entry.split(b'\t', 1)
        mode, kind, _, length = info.split()
        if kind != b'blob' or mode == b'120000':
            raise ValueError('unsupported source symlink or submodule')
        size += int(length)
        if size > limit:
            raise ValueError('expanded source exceeds capsule limit')
    trusted_git(source, 'checkout', '--detach', head)
    return file_manifest(source)


def _identity(root, request):
    state = json.loads((root / 'service/state.json').read_text())
    if request.get('mode') == 'pr':
        number = request.get('pr_number');head = request.get('expected_head')
        if type(number) is not int or number < 1 or not isinstance(head, str) or not re.fullmatch('[0-9a-f]{40}', head):
            raise ValueError('invalid PR target')
        prs = [p for p in state['prs'] if p['number'] == number]
        if len(prs) != 1 or prs[0]['state'] != 'OPEN' or prs[0]['headRefOid'] != head:
            raise ValueError('unknown, closed or stale PR')
        pr = prs[0]
        # Resolve actual remote refs too: service metadata alone is not a target.
        actual = git(root / 'remote.git', 'rev-parse', 'refs/heads/' + pr['headRefName'])
        if actual != head:
            raise ValueError('PR head disagrees with actual remote')
        base = git(root / 'remote.git', 'rev-parse', 'refs/heads/' + pr['baseRefName'])
        return head, base
    if request.get('mode') == 'plan':
        base = git(root / 'remote.git', 'rev-parse', 'refs/heads/' + state['base'])
        return base, base
    raise ValueError('unsupported review mode')


def prepare_review(service_root, request):
    started = time.monotonic()
    root = Path(service_root).resolve()
    if not isinstance(request, dict):
        raise ValueError('request must be an object')
    expected_keys = {'mode', 'pr_number', 'expected_head'} if request.get('mode') == 'pr' else {'mode', 'plan_paths'}
    if set(request) != expected_keys:
        raise ValueError('unknown or missing request fields')
    head, base = _identity(root, request)
    raw = regular_bytes(root / 'repo', 'context/context.md', PACKET_FILE_LIMIT)
    ctx = decode_context(raw)
    plans = ctx.get('active_context', [])
    if not isinstance(plans, list) or not all(isinstance(p, str) and p.startswith('context/plans/') for p in plans):
        raise ValueError('invalid active plan identities')
    selected = request.get('plan_paths', plans)
    if not isinstance(selected, list) or not selected or len(selected) > 63 or not all(p in plans for p in selected):
        raise ValueError('review must include valid active plans')
    packet = {'context/context.md': raw}
    for path in dict.fromkeys(selected):
        packet[path] = regular_bytes(root / 'repo', path, PACKET_FILE_LIMIT)
    if len(packet) > 64 or sum(map(len, packet.values())) > PACKET_LIMIT:
        raise ValueError('packet exceeds limits')
    digests = {p: hashlib.sha256(v).hexdigest() for p, v in packet.items()}
    published = root / 'review-capsules';published.mkdir(exist_ok=True)
    current_size = sum(p.stat().st_size for p in published.rglob('*') if p.is_file())
    if current_size >= TRIAL_CAPSULE_LIMIT:
        raise ValueError('trial capsule limit reached')
    staging = Path(tempfile.mkdtemp(prefix='.preparing-', dir=published))
    try:
        for path, content in packet.items():
            out = staging / 'packet' / path;out.parent.mkdir(parents=True, exist_ok=True);out.write_bytes(content)
        capture_git(root / 'remote.git', staging / 'source', head, base, CAPSULE_LIMIT - sum(map(len, packet.values())))
        if _identity(root, request) != (head, base):
            raise ValueError('review target changed during capture')
        for path, content in packet.items():
            if regular_bytes(root / 'repo', path, PACKET_FILE_LIMIT) != content:
                raise ValueError('review packet changed during capture')
        files = file_manifest(staging)
        size = sum(p.stat().st_size for p in staging.rglob('*') if p.is_file())
        if size > CAPSULE_LIMIT or current_size + size > TRIAL_CAPSULE_LIMIT:
            raise ValueError('capsule byte limit exceeded')
        review_id = 'review-' + uuid.uuid4().hex
        manifest = {'version': 1, 'review_id': review_id, 'mode': request['mode'],
            'target': head if request['mode'] == 'pr' else {p: digests[p] for p in selected},
            'pr_number': request.get('pr_number'), 'source_head': head, 'base_sha': base,
            'capsule_digest': hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest(),
            'context_digest': digests['context/context.md'], 'packet_digests': digests, 'files': files,
            'capsule_path': '/review-capsules/' + review_id, 'bytes': size, 'preparation_seconds': time.monotonic() - started}
        manifest['manifest_digest'] = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
        encoded = (json.dumps(manifest, indent=2) + '\n').encode()
        if size + len(encoded) > CAPSULE_LIMIT or current_size + size + len(encoded) > TRIAL_CAPSULE_LIMIT:
            raise ValueError('capsule including manifest exceeds byte limit')
        (staging / 'manifest.json').write_bytes(encoded)
        staging.rename(published / review_id)
        return {key: value for key, value in manifest.items() if key != 'files'}
    finally:
        if staging.exists():
            shutil.rmtree(staging)
