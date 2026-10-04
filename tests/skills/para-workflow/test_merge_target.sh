#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
s=Path('skills/para-workflow/SKILL.md').read_text()
r=Path('skills/para-review/SKILL.md').read_text()
assert '--match-head-commit' in s
assert 'reviewed head' in r and 'self-review' in r
assert 'queued' in s.lower()
print('PASS documented guarded merge and review identity')
PY
