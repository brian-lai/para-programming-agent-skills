import os
import shutil
import unittest
from install_fixture import InstallFixture, snapshot


class Links(InstallFixture):
    def test_fresh_links_resolve(self):
        self.install()
        for root in (self.agents, self.codex):
            for path in (self.source / 'skills').iterdir():
                link = root / 'skills' / path.name
                self.assertTrue(link.is_symlink(), link)
                self.assertEqual(link.resolve(), path)
            self.assertEqual((root / 'resources/AGENTS.md').resolve(), self.source / 'resources/AGENTS.md')
            self.assertEqual((root / 'docs/METHODOLOGY.md').resolve(), self.source / 'docs/METHODOLOGY.md')

    def test_source_edit_and_new_asset_visible_without_reinstall(self):
        self.install()
        for name in ('skills/para-init/SKILL.md', 'skills/para-init/assets/new.md',
                     'docs/METHODOLOGY.md', 'resources/AGENTS.md'):
            self.write(self.source / name, 'new content')
            for root in (self.agents, self.codex):
                self.assertEqual((root / name).read_text(), 'new content')

    def test_source_tree_unchanged(self):
        before = snapshot(self.source)
        self.install()
        self.assertEqual(snapshot(self.source), before)

    def test_correct_links_are_noops(self):
        self.install()
        before = snapshot(self.base)
        result = self.install()
        self.assertEqual(snapshot(self.base), before)
        self.assertIn('unchanged', result.stdout)

    def test_correct_leaf_links_not_rejected_as_source_writes(self):
        self.install()
        self.install('--dry-run')

    def test_paths_with_spaces(self):
        self.agents = self.base / 'agents with spaces'
        self.env['AGENTS_HOME'] = str(self.agents)
        self.install()
        self.assertTrue((self.agents / 'skills/para-plan').is_symlink())

    def test_symlinked_config_parent(self):
        target = self.base / 'config/codex'
        target.mkdir(parents=True)
        self.codex.symlink_to(target)
        self.install()
        self.assertTrue(self.codex.is_symlink())
        self.assertEqual((target / 'skills/para-plan').resolve(), self.source / 'skills/para-plan')

    def test_same_physical_roots_deduplicate(self):
        self.agents.mkdir()
        self.codex.symlink_to(self.agents)
        self.install()
        self.assertFalse((self.agents / 'para-install-backups').exists())
        self.install()

    def test_unsafe_overlap_rejected(self):
        cases = [self.source, self.source / 'nested', self.agents / 'skills/para-init']
        for root in cases:
            with self.subTest(root=root):
                before = snapshot(self.base)
                self.install(ok=False, env=dict(self.env, CODEX_HOME=str(root)))
                self.assertEqual(snapshot(self.base), before)

    def test_symlinked_container_into_source_rejected(self):
        self.agents.mkdir()
        (self.agents / 'skills').symlink_to(self.source / 'skills')
        before = snapshot(self.base)
        self.install(ok=False)
        self.assertEqual(snapshot(self.base), before)

    def test_linked_worktree_source_rejected(self):
        self.git('add', '.', cwd=self.source)
        self.git('commit', '-qm', 'fixture', cwd=self.source)
        worktree = self.base / 'disposable'
        self.git('worktree', 'add', '-qb', 'disposable', str(worktree), cwd=self.source)
        before = snapshot(self.base)
        self.install(source=worktree, ok=False)
        self.assertEqual(snapshot(self.base), before)

    def test_invalid_container_rejected(self):
        self.write(self.codex / 'resources', 'file blocks directory')
        before = snapshot(self.base)
        self.install(ok=False)
        self.assertEqual(snapshot(self.base), before)

    def test_source_checkout_under_install_root(self):
        # Documented clones inside ~/.codex/plugins are safe when writes are siblings.
        nested = self.codex / 'plugins/para-programming'
        nested.parent.mkdir(parents=True)
        self.source.rename(nested)
        self.source = nested
        self.install()
        self.assertEqual((self.codex / 'skills/para-init').resolve(), nested / 'skills/para-init')

    def test_help_and_unknown_argument(self):
        self.install('--help')
        self.install('--unknown', ok=False)
        self.assertFalse(self.agents.exists())


if __name__ == '__main__':
    unittest.main()
