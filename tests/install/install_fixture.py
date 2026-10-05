"""Disposable installer contract fixtures; Python is a test dependency only."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]


def snapshot(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if '.git' in path.relative_to(root).parts:
            continue
        key = str(path.relative_to(root))
        if path.is_symlink():
            result[key] = ('link', os.readlink(path))
        elif path.is_file():
            result[key] = ('file', hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mode)
        elif path.is_dir():
            result[key] = ('dir',)
    return result


class InstallFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='para install ')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.source = self.base / 'source checkout'
        self.source.mkdir()
        for name in ('skills', 'docs', 'resources', 'scripts'):
            shutil.copytree(REPO / name, self.source / name)
        self.git('init', '-q', str(self.source))
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        self.agents = self.base / 'agents'
        self.codex = self.base / 'codex'
        self.env.update(HOME=str(self.base), AGENTS_HOME=str(self.agents), CODEX_HOME=str(self.codex))
        self.registry = self.agents / 'plugins/marketplace.json'

    def git(self, *args, cwd=None):
        env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        env.update(GIT_AUTHOR_NAME='Fixture', GIT_AUTHOR_EMAIL='fixture@example.test',
                   GIT_COMMITTER_NAME='Fixture', GIT_COMMITTER_EMAIL='fixture@example.test')
        return subprocess.run(['git', '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null', *args], cwd=cwd, env=env, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def install(self, *args, ok=True, env=None, source=None):
        result = subprocess.run(['/bin/bash', str((source or self.source) / 'scripts/install.sh'), *args],
                                env=env or self.env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def registry_data(self, source=None):
        return {'custom': {'keep': True}, 'plugins': [
            {'name': 'other', 'source': {'source': 'remote', 'path': 'untouched'}},
            {'name': 'para-programming', 'source': source or {'source': 'local', 'path': '/old/path'},
             'custom': 'preserved', 'policy': {'installation': 'AVAILABLE'}}]}

    def seed_registry(self, data=None):
        self.write(self.registry, json.dumps(data or self.registry_data()))

    def backups(self, relative):
        return [run / relative for run in (self.agents / 'para-install-backups').glob('*')
                if os.path.lexists(run / relative)]

    def fault(self, command, body):
        wrapper = self.base / 'fault-bin' / command
        real = shutil.which(command)
        self.write(wrapper, '#!/bin/bash\n' + body.replace('@REAL@', json.dumps(real)) + '\n')
        wrapper.chmod(0o755)
        return dict(self.env, PATH=str(wrapper.parent) + os.pathsep + self.env['PATH'])
