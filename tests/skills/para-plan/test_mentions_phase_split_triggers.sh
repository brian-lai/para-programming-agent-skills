#!/usr/bin/env bash
# Structural contract only; behavioral evaluation is separate.
set -euo pipefail
python3 - <<'PYTEST'
from pathlib import Path
s=Path('skills/para-plan/SKILL.md').read_text()
assert 'cross-file refactoring' in s, 'cross-file refactoring'
assert 'architectural layers' in s, 'architectural layers'
assert 'selected base' in s, 'selected base'
assert 'already agreed' in s, 'already agreed'
print('PASS planning contract')
PYTEST
