#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
s=Path('skills/para-status/SKILL.md').read_text()
assert 'Stale reference' in s and 'missing directory' in s
assert 'Orphaned worktree' in s and 'do not remove' in s
print('PASS missing and unrelated worktree guidance')
PY
