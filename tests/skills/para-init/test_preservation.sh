#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
s=Path('skills/para-init/SKILL.md').read_text()
for t in ['existing context', 'unknown fields', 'only missing', 'inspect', 'never overwrites existing']:
    assert t in s,t
s=Path('skills/para-init/assets/agents-full-template.md').read_text()
assert 'npm install' not in s and '80%+' not in s
print('PASS declared initialization preservation')
PY
