"""Observable fixture-only GitHub operations. No real GitHub or authentication calls."""
import json
from pathlib import Path
import subprocess
import time
from fixtures import dump, git


class GithubStub:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.state = self.root / 'service/state.json'
        self.events = self.root / 'service/events.jsonl'
        self.remote = self.root / 'remote.git'

    def call(self, args, cwd=None):
        state = json.loads(self.state.read_text())
        effect, code, output = 'read', 0, ''
        before = json.loads(json.dumps(state))
        def option(key, default=None):
            try:
                return args[args.index(key) + 1]
            except (ValueError, IndexError):
                return default
        try:
            command = args[:2]
            if '--help' in args or '-h' in args or args == ['--version']:
                output = 'Fixture gh: pr list/create/view/diff/checks/merge; repo view; auth status. Options: --repo fixture/repo --head BRANCH --base BRANCH --json FIELDS --jq QUERY. Merge requires --match-head-commit SHA. Create supports --title TITLE --body BODY or --body-file PATH.'
            elif command == ['auth', 'status']:
                output = 'Fixture authenticated (no external service)'
            elif command == ['repo', 'view']:
                output = {'nameWithOwner': 'fixture/repo', 'defaultBranchRef': {'name': state['base']}}
            elif command == ['pr', 'list']:
                output = []
                for pr in state['prs']:
                    if option('--head', pr['headRefName']) != pr['headRefName'] or option('--base', pr['baseRefName']) != pr['baseRefName']:
                        continue
                    if option('--state', 'open').upper() not in ('ALL', pr['state']):
                        continue
                    output.append(self.refresh(pr, state))
            elif command == ['pr', 'create']:
                head = option('--head') or git(cwd or self.root / 'repo', 'branch', '--show-current')
                base = option('--base', state['base'])
                if base != state['base']:
                    raise ValueError('unknown base')
                sha = git(self.remote, 'rev-parse', 'refs/heads/' + head)
                if any(p['headRefName'] == head and p['baseRefName'] == base and p['state'] == 'OPEN' for p in state['prs']):
                    raise ValueError('matching PR already exists')
                number = len(state['prs']) + 1
                state['prs'].append({'number': number, 'url': f'https://fixture.invalid/pull/{number}',
                    'headRefName': head, 'baseRefName': base, 'headRefOid': sha, 'state': 'OPEN', 'mergeCommit': None,
                    'baseAtCreate': git(self.remote, 'rev-parse', base)})
                output = state['prs'][-1]['url'];effect = 'created'
            elif command in (['pr', 'view'], ['pr', 'checks'], ['pr', 'diff'], ['pr', 'merge']):
                identity = args[2] if len(args) > 2 and not args[2].startswith('-') else None
                if identity and identity.startswith('https://fixture.invalid/pull/'):
                    identity = identity.rsplit('/', 1)[1]
                candidates = [p for p in state['prs'] if identity is None or str(p['number']) == identity or p['headRefName'] == identity]
                if identity is None:
                    branch = git(cwd or self.root / 'repo', 'branch', '--show-current')
                    candidates = [p for p in candidates if p['headRefName'] == branch]
                if len(candidates) != 1:
                    raise ValueError('PR identity missing or ambiguous')
                pr = self.refresh(candidates[0], state)
                if command == ['pr', 'view']:
                    output = pr
                elif command == ['pr', 'checks']:
                    output = [{'name': 'fixture-validation', 'state': 'SUCCESS' if state['checks_pass'] else 'FAILURE',
                               'bucket': 'pass' if state['checks_pass'] else 'fail'}] if '--json' in args else ('fixture-validation\tpass' if state['checks_pass'] else 'fixture-validation\tfail')
                    code = 0 if state['checks_pass'] else 1
                elif command == ['pr', 'diff']:
                    output = git(self.remote, 'diff', pr['baseRefName'] + '...' + pr['headRefName'])
                else:
                    if pr['state'] == 'MERGED':
                        output = 'Already merged'
                    else:
                        if state.get('race_on_merge'):
                            old = pr['headRefOid'];tree = git(self.remote, 'rev-parse', old + '^{tree}')
                            new = git(self.remote, 'commit-tree', tree, '-p', old, input='Concurrent fixture change\n')
                            git(self.remote, 'update-ref', 'refs/heads/' + pr['headRefName'], new)
                            state['race_on_merge'] = False;pr['headRefOid'] = new
                        guard = option('--match-head-commit')
                        if not guard:
                            effect = 'rejected_unguarded';raise ValueError('expected-head guard required')
                        if guard != pr['headRefOid']:
                            effect = 'rejected_stale';raise ValueError('head changed; re-establish review/check eligibility')
                        if not state['checks_pass']:
                            effect = 'rejected_checks';raise ValueError('required checks failed')
                        base_sha = git(self.remote, 'rev-parse', pr['baseRefName'])
                        # A real Git merge result, including the current base ancestry.
                        ancestor = subprocess.run(['git', '--git-dir', str(self.remote), 'merge-base', '--is-ancestor', base_sha, guard], capture_output=True).returncode == 0
                        if ancestor:
                            merged = guard
                        else:
                            tree = git(self.remote, 'merge-tree', '--write-tree', base_sha, guard).splitlines()[0]
                            merged = git(self.remote, 'commit-tree', tree, '-p', base_sha, '-p', guard, input='Fixture merge\n')
                        git(self.remote, 'update-ref', 'refs/heads/' + pr['baseRefName'], merged, base_sha)
                        pr.update(state='MERGED', mergeCommit={'oid': merged}, mergedAt='2026-10-04T12:30:00Z')
                        effect = 'merged';output = 'Merged ' + pr['url']
            else:
                effect = 'unsupported';raise ValueError('unsupported fixture operation: ' + ' '.join(args[:2]))
        except (ValueError, subprocess.CalledProcessError) as exc:
            code = 1;output = str(exc)
            if effect == 'read':
                effect = 'rejected'
        dump(self.state, state)
        if isinstance(output, (dict, list)):
            fields = option('--json')
            if fields:
                keys = fields.split(',')
                def project(value):
                    return {k: value.get(k) for k in keys}
                output = project(output) if isinstance(output, dict) else [project(v) for v in output]
            output = json.dumps(output)
            query = option('--jq') or option('-q')
            if query:
                result = subprocess.run(['jq', '-r', query], input=output, text=True, capture_output=True)
                code, output = result.returncode, result.stdout or result.stderr
        event = {'time': time.time(), 'args': args, 'code': code, 'effect': effect,
                 'before': before, 'after': state}
        with self.events.open('a') as f:
            f.write(json.dumps(event) + '\n')
        return code, output

    def refresh(self, pr, state):
        if pr['state'] == 'OPEN':
            pr['headRefOid'] = git(self.remote, 'rev-parse', 'refs/heads/' + pr['headRefName'])
        pr.update(baseRefOid=git(self.remote, 'rev-parse', pr['baseRefName']), mergeable='MERGEABLE',
                  statusCheckRollup=[{'name': 'fixture-validation', 'status': 'COMPLETED',
                      'conclusion': 'SUCCESS' if state['checks_pass'] else 'FAILURE'}])
        return pr
