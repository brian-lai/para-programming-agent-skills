import json
import os
import unittest
from install_fixture import InstallFixture, snapshot


class Migration(InstallFixture):
    def test_modified_copies_backed_up(self):
        self.write(self.agents / 'skills/para-init/custom.txt', 'local memory')
        self.install()
        backups = self.backups('skills/para-init')
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / 'custom.txt').read_text(), 'local memory')
        self.assertTrue((self.agents / 'skills/para-init').is_symlink())

    def test_wrong_and_broken_symlinks_preserved_without_following(self):
        target = self.write(self.base / 'outside/keep', 'unrelated')
        (self.agents / 'skills').mkdir(parents=True)
        (self.agents / 'skills/para-init').symlink_to(target.parent)
        (self.agents / 'skills/para-plan').symlink_to(self.base / 'missing')
        self.install()
        self.assertEqual(target.read_text(), 'unrelated')
        for name in ('para-init', 'para-plan'):
            self.assertTrue(self.backups('skills/' + name)[0].is_symlink())
        self.assertEqual(os.readlink(self.backups('skills/para-plan')[0]), str(self.base / 'missing'))

    def test_unrelated_entries_and_global_guides_unchanged(self):
        paths = [root / name for root in (self.agents, self.codex)
                 for name in ('AGENTS.md', 'skills/unrelated/SKILL.md', 'docs/custom.md', 'resources/custom.md')]
        for p in paths:
            self.write(p, 'mine')
        self.install()
        for p in paths:
            self.assertEqual(p.read_text(), 'mine')

    def test_backups_outside_discovery(self):
        self.write(self.agents / 'skills/para-init/SKILL.md', 'old')
        self.install()
        self.assertEqual(len(self.backups('skills/para-init/SKILL.md')), 1)
        self.assertEqual(list((self.agents / 'skills').glob('*backup*')), [])

    def test_no_backup_collision(self):
        self.write(self.agents / 'docs/METHODOLOGY.md', 'first')
        self.install()
        (self.agents / 'docs/METHODOLOGY.md').unlink()
        self.write(self.agents / 'docs/METHODOLOGY.md', 'second')
        self.install()
        self.assertEqual({p.read_text() for p in self.backups('docs/METHODOLOGY.md')}, {'first', 'second'})

    def test_invalid_registry_writes_nothing(self):
        cases = ['bad json', '[]', '{"plugins":{}}',
                 json.dumps({'plugins': [self.registry_data()['plugins'][1]] * 2})]
        for text in cases:
            self.write(self.registry, text)
            before = snapshot(self.base)
            self.install(ok=False)
            self.assertEqual(snapshot(self.base), before)

    def test_multiple_registry_documents_write_nothing(self):
        for text in ('{"plugins":[]}\n{"plugins":[]}', '{"plugins":[]}\ntrue'):
            with self.subTest(registry=text):
                self.write(self.registry, text)
                self.write(self.agents / 'skills/para-init/local.txt', 'preserve local copy')
                before = snapshot(self.base)
                self.install(ok=False)
                self.assertEqual(snapshot(self.base), before)

    def test_missing_jq_writes_nothing(self):
        bin_dir = self.base / 'minimal-bin'
        bin_dir.mkdir()
        # Argument handling and dependency preflight must not need external utilities before jq.
        before = snapshot(self.base)
        self.install(ok=False, env=dict(self.env, PATH=str(bin_dir)))
        self.assertEqual(snapshot(self.base), before)

    def test_stale_marketplace_source_reconciled_and_fields_preserved(self):
        data = self.registry_data()
        self.seed_registry(data)
        self.install()
        data['plugins'][1]['source']['path'] = str(self.source)
        self.assertEqual(json.loads(self.registry.read_text()), data)
        old = json.loads(self.backups('plugins/marketplace.json')[0].read_text())
        self.assertEqual(old['plugins'][1]['source']['path'], '/old/path')

    def test_nonlocal_registration_rejected(self):
        self.seed_registry(self.registry_data({'source': 'remote', 'path': 'remote'}))
        before = snapshot(self.base)
        self.install(ok=False)
        self.assertEqual(snapshot(self.base), before)

    def test_registry_symlink_target_unchanged(self):
        target = self.write(self.base / 'registry-target', json.dumps(self.registry_data()))
        self.registry.parent.mkdir(parents=True)
        self.registry.symlink_to(target)
        before = target.read_bytes()
        self.install()
        self.assertFalse(self.registry.is_symlink())
        self.assertEqual(target.read_bytes(), before)
        self.assertTrue(self.backups('plugins/marketplace.json')[0].is_symlink())

    def test_registry_publication_failure_is_recoverable(self):
        for symlink in (False, True):
            with self.subTest(symlink=symlink):
                if self.registry.exists():
                    self.registry.unlink()
                self.seed_registry()
                target = self.base / 'external-registry'
                if symlink:
                    self.registry.rename(target)
                    self.registry.symlink_to(target)
                before = self.registry.read_bytes()
                env = self.fault('mv', 'for arg in "$@"; do\n  case "$arg" in */plugins/marketplace.json) exit 92;; esac\ndone\nexec @REAL@ "$@"')
                result = self.install(ok=False, env=env)
                self.assertTrue((self.agents / 'skills/para-init').is_symlink())
                self.assertEqual(self.registry.read_bytes(), before)
                self.assertIn(str(self.registry), result.stdout)
                self.assertTrue(self.backups('plugins/marketplace.json'))
                if symlink:
                    self.assertEqual(target.read_bytes(), before)
                self.install()

    def test_link_failure_preserves_recoverable_state_and_retry(self):
        old = self.write(self.agents / 'skills/para-init/custom', 'mine')
        env = self.fault('mv', 'for arg in "$@"; do\n case "$arg" in */skills/para-init) exit 93;; esac\ndone\nexec @REAL@ "$@"')
        result = self.install(ok=False, env=env)
        preserved = old.exists() or any((p / 'custom').read_text() == 'mine' for p in self.backups('skills/para-init'))
        self.assertTrue(preserved)
        self.assertIn('para-init', result.stdout)
        self.install()
        self.assertTrue((self.agents / 'skills/para-init').is_symlink())

    def test_interruption_after_backup_has_recovery_record(self):
        self.write(self.agents / 'skills/para-init/custom', 'mine')
        env = self.fault('mv', '@REAL@ "$@" || exit $?\nfor arg in "$@"; do\n case "$arg" in */para-install-backups/*/skills/para-init) kill -KILL "$PPID";; esac\ndone')
        self.install(ok=False, env=env)
        backups = self.backups('skills/para-init')
        self.assertEqual((backups[0] / 'custom').read_text(), 'mine')
        manifests = list((self.agents / 'para-install-backups').glob('*/manifest.jsonl'))
        records = [json.loads(line) for p in manifests for line in p.read_text().splitlines()]
        self.assertTrue(any(r.get('backup') == str(backups[0]) and r.get('destination') == str(self.agents / 'skills/para-init') for r in records))
        self.install()
        self.assertEqual((backups[0] / 'custom').read_text(), 'mine')

    def test_detected_destination_change_is_preserved(self):
        leaf = self.write(self.agents / 'skills/para-init', 'before')
        env = self.fault('ln', '@REAL@ "$@" || exit $?\nif [ "$1" = -s ] && [[ "$2" == */skills/para-init ]]; then printf changed > "$AGENTS_HOME/skills/para-init"; fi')
        self.install(ok=False, env=env)
        self.assertEqual(leaf.read_text(), 'changed')
        self.assertFalse(self.backups('skills/para-init'))

    def test_dry_run_preserves_existing_tree(self):
        self.write(self.agents / 'skills/para-init/custom', 'mine')
        self.seed_registry()
        before = snapshot(self.base)
        result = self.install('--dry-run')
        self.assertEqual(snapshot(self.base), before)
        self.assertIn('backup', result.stdout.lower())

    def test_stale_owned_link_reported_not_deleted(self):
        self.install()
        stale = self.agents / 'skills/para-old'
        stale.symlink_to(self.source / 'skills/para-old')
        result = self.install()
        self.assertTrue(stale.is_symlink())
        self.assertIn(str(stale), result.stdout)


if __name__ == '__main__':
    unittest.main()
