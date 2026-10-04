#!/usr/bin/env bash
set -euo pipefail
python3 - <<'CHECK'
from pathlib import Path
s=Path('skills/para-execute/SKILL.md').read_text()
assert s.index('RED') < s.index('GREEN') < s.index('Commit the change')
assert 'required checks' in s
for name in ['plan-template.md','phased-plan-sub-template.md']:
 t=Path('skills/para-plan/assets',name).read_text()
 assert 'stays red' not in t and "Won’t compile" not in t and "Won't compile" not in t
print('PASS documented green-commit contract')
CHECK
