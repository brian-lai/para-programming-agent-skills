#!/usr/bin/env bash
set -euo pipefail
python3 - <<'CHECK'
from pathlib import Path
s=Path('skills/para-execute/SKILL.md').read_text()
assert '--allow-empty' not in s
assert s.index('Commit the change') < s.index('Mark the todo')
assert 'preserve' in s.lower()
print('PASS documented commit-before-completion contract')
CHECK
