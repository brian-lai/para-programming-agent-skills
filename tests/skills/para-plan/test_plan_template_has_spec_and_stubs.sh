#!/usr/bin/env bash
# Structural contract only; behavioral evaluation is separate.
set -euo pipefail
python3 - <<'PYTEST'
from pathlib import Path
s=Path('skills/para-plan/assets/plan-template.md').read_text()
assert 'Existing contract' in s, 'Existing contract'
assert 'only when' in s, 'only when'
assert 'execution checkout' in s, 'execution checkout'
print('PASS planning contract')
PYTEST
