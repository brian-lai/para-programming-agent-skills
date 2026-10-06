import json
import os
import unittest
from install_fixture import InstallFixture, REPO, snapshot


class PullUpdates(InstallFixture):
    def publish_fixture(self):
        self.git('add', '.', cwd=self.source)
        self.git('commit', '-qm', 'initial payload', cwd=self.source)
        self.git('branch', '-M', 'main', cwd=self.source)
        remote = self.base / 'remote.git'
        self.git('clone', '--bare', str(self.source), str(remote))
        self.publisher = self.source
        self.git('remote', 'add', 'origin', str(remote), cwd=self.publisher)
        self.source = self.base / 'permanent clone'
        self.git('clone', str(remote), str(self.source))

    def publish_updates(self):
        self.git('add', '.', cwd=self.publisher)
        self.git('commit', '-qm', 'update payload', cwd=self.publisher)
        self.git('push', 'origin', 'main', cwd=self.publisher)
        self.git('pull', '--ff-only', cwd=self.source)

    def test_pull_updates_installed_skill_without_reinstall(self):
        self.publish_fixture()
        self.install()  # The only installer invocation in this scenario.
        installed_before = [snapshot(root) for root in (self.agents, self.codex)]
        paths = ('skills/para-init/SKILL.md', 'skills/para-init/assets/new.md',
                 'docs/METHODOLOGY.md', 'resources/AGENTS.md')
        for path in paths:
            self.write(self.publisher / path, 'content from next commit: ' + path)
        self.publish_updates()
        for root, before in zip((self.agents, self.codex), installed_before):
            self.assertEqual(snapshot(root), before, 'installed link identities/registry must not change')
            for path in paths:
                self.assertEqual((root / path).read_bytes(), (self.publisher / path).read_bytes())

    def test_new_top_level_skill_needs_link_refresh(self):
        self.publish_fixture()
        self.install()
        self.write(self.publisher / 'skills/para-new/SKILL.md', '---\nname: para-new\n---\nNew skill')
        self.publish_updates()
        for root in (self.agents, self.codex):
            self.assertFalse((root / 'skills/para-new').exists())
        self.install()
        for root in (self.agents, self.codex):
            self.assertEqual((root / 'skills/para-new').resolve(), self.source / 'skills/para-new')

    def test_moved_checkout_repair_preserves_backups(self):
        self.write(self.agents / 'skills/para-init/local.txt', 'keep original copy')
        self.install()
        old_backups = self.backups('skills/para-init')
        old_source = self.source
        self.source = self.base / 'new permanent location'
        old_source.rename(self.source)
        # An old target that reappears must not be traversed or modified on repair.
        sentinel = self.write(old_source / 'skills/para-init/SKILL.md', 'unrelated old location')
        self.install()
        for root in (self.agents, self.codex):
            self.assertEqual((root / 'skills/para-init').resolve(), self.source / 'skills/para-init')
        self.assertEqual(sentinel.read_text(), 'unrelated old location')
        self.assertEqual((old_backups[0] / 'local.txt').read_text(), 'keep original copy')
        replaced_links = [p for p in self.backups('skills/para-init') if p.is_symlink()]
        self.assertTrue(any(os.readlink(p) == str(old_source / 'skills/para-init') for p in replaced_links))
        para = next(p for p in json.loads(self.registry.read_text())['plugins'] if p['name'] == 'para-programming')
        self.assertEqual(para['source']['path'], str(self.source))

    def test_documented_symlink_contract(self):
        for name in ('README.md', 'INSTALL.md'):
            text = (REPO / name).read_text()
            self.assertIn('git pull --ff-only', text)
            self.assertIn('para-install-backups', text)
            self.assertIn('AGENTS.md', text)
        guide = (REPO / 'INSTALL.md').read_text()
        self.assertNotIn('cp -R ~/.agents/skills/para-*', guide)
        self.assertNotIn('installer copies', guide)


if __name__ == '__main__':
    unittest.main()
