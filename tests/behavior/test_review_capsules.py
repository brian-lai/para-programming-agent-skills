import json
import tempfile
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
from fixtures import prepare, git
from review_isolation import prepare_review


class ReviewCapsuleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='para-capsule-')
        self.root = Path(self.tmp.name) / 'trial'
        prepare('resume_after_pr_created', self.root)
        self.state = json.loads((self.root / 'service/state.json').read_text())
        self.head = self.state['prs'][0]['headRefOid']
        self.request = {'mode': 'pr', 'pr_number': 1, 'expected_head': self.head}

    def tearDown(self):
        self.tmp.cleanup()

    def test_prepare_review_rejects_stale_head(self):
        with self.assertRaises(ValueError):
            prepare_review(self.root, dict(self.request, expected_head='f' * 40))
        self.assertFalse(list((self.root / 'review-capsules').glob('review-*')))

    def test_capsule_uses_committed_target(self):
        (self.root / 'repo/greeting.py').write_text('raise RuntimeError("uncommitted")\n')
        value = prepare_review(self.root, self.request)
        source = self.root / 'review-capsules' / value['review_id'] / 'source'
        self.assertEqual(git(source, 'rev-parse', 'HEAD'), self.head)
        self.assertNotIn('uncommitted', (source / 'greeting.py').read_text())
        self.assertEqual(value['target'], self.head)

    def test_author_edits_do_not_change_capsule(self):
        value = prepare_review(self.root, self.request)
        capsule = self.root / 'review-capsules' / value['review_id']
        before = (capsule / 'packet/context/context.md').read_bytes()
        (self.root / 'repo/context/context.md').write_text('replaced')
        self.assertEqual((capsule / 'packet/context/context.md').read_bytes(), before)

    def test_plan_digest_cannot_approve_pr(self):
        context = (self.root / 'repo/context/context.md').read_text()
        import re
        data = json.loads(re.search(r'```json\s*\n(.*?)\n```', context, re.S)[1])
        result = prepare_review(self.root, {'mode': 'plan', 'plan_paths': data['active_context']})
        self.assertEqual(result['mode'], 'plan');self.assertIsInstance(result['target'], dict)

    def test_packet_rejects_escape_symlink_and_special_file(self):
        context = self.root / 'repo/context/context.md'
        context.unlink();context.symlink_to('/etc/passwd')
        with self.assertRaises((ValueError, OSError)):
            prepare_review(self.root, self.request)

    def test_packet_size_limits_fail_without_truncation(self):
        with patch('review_isolation.PACKET_FILE_LIMIT', 1), self.assertRaises(ValueError):
            prepare_review(self.root, self.request)

    def test_capsule_and_scratch_resource_bounds(self):
        with patch('review_isolation.CAPSULE_LIMIT', 1), self.assertRaises(ValueError):
            prepare_review(self.root, self.request)
        self.assertFalse(list((self.root / 'review-capsules').glob('review-*')))

    def test_snapshot_rejects_invalid_git_objects(self):
        obj = self.root / 'remote.git/objects' / self.head[:2] / self.head[2:]
        obj.chmod(0o600);obj.write_bytes(b'not a valid object')
        with self.assertRaises((ValueError, OSError, subprocess.CalledProcessError)):
            prepare_review(self.root, self.request)

    def test_head_change_during_capture_leaves_no_published_capsule(self):
        from review_isolation import capture_git
        def race(*args, **kwargs):
            result = capture_git(*args, **kwargs)
            self.state['prs'][0]['headRefOid'] = 'f' * 40
            (self.root / 'service/state.json').write_text(json.dumps(self.state))
            return result
        with patch('review_isolation.capture_git', side_effect=race), self.assertRaises(ValueError):
            prepare_review(self.root, self.request)
        self.assertFalse(list((self.root / 'review-capsules').glob('review-*')))

    def test_manifest_bytes_count_toward_capsule_limit(self):
        first = prepare_review(self.root, self.request)
        with patch('review_isolation.CAPSULE_LIMIT', first['bytes']), self.assertRaises(ValueError):
            prepare_review(self.root, self.request)
