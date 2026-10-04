#!/usr/bin/env bash
# Structural contract only; behavioral evaluation is separate.
set -euo pipefail
python3 - <<'PYTEST'
from pathlib import Path
s=Path('skills/para-plan/SKILL.md').read_text()
assert 'Inspect existing research' in s, 'Inspect existing research'
assert 'material unresolved choices' in s, 'material unresolved choices'
assert 'recheck affected parts' in s, 'recheck affected parts'
assert 'more than 3 substantive changes' not in s, 'more than 3 substantive changes'
assert 'before doing anything else' not in s, 'before doing anything else'
print('PASS planning contract')
PYTEST
