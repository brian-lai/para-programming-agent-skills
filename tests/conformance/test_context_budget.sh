#!/usr/bin/env bash
# Static declared loading paths; live transcripts measure actual reads.
set -euo pipefail
python3 - <<'PY'
import json,os
from pathlib import Path
root=Path(os.environ.get('PARA_BUDGET_ROOT','.'))
m=json.loads(Path(os.environ.get('PARA_BUDGET_MANIFEST','tests/fixtures/skill-context-budget.json')).read_text())
b=json.loads(Path('tests/fixtures/skill-context-baseline.json').read_text())
assert m['scenarios'].keys()==b['scenarios'].keys(), 'missing scenario'
for name,s in m['scenarios'].items():
    assert set(s['required_resources']) <= set(s['paths']), f'{name}: mandatory resource omitted'
    assert len(s['paths']) == len(set(s['paths'])), 'duplicate path'
    total=sum(len((root/p).read_bytes()) for p in s['paths'])
    assert total<=b['scenarios'][name]['bytes'], f'{name}: context growth ({total})'
    print(f'PASS {name}: {total} / {b["scenarios"][name]["bytes"]} bytes')
PY
