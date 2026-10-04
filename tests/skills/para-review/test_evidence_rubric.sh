#!/usr/bin/env bash
# Tests the declared review contract, not reviewer judgment.
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
s=Path('skills/para-review/SKILL.md').read_text()
for term in ['trigger', 'violated requirement', 'impact', 'evidence', 'issue ledger', 'self-review', 'target']:
    assert term in s, term
assert 'FAANG' not in s
print('PASS review evidence rubric')
PY
