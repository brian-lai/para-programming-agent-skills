#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
s=Path('skills/para-summarize/SKILL.md').read_text()
assert 'standalone' in s.lower()
assert 'gh pr create' not in s and 'git push' not in s
assert 'merge-base' in s and 'summary path' in s
print('PASS standalone report scope and committed-diff guidance')
PY
