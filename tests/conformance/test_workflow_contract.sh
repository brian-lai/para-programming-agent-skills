#!/usr/bin/env bash
# Documentation/schema checks only; live compliance is evaluated separately.
set -euo pipefail
python3 - <<'PY'
import json,re
from pathlib import Path
schema=Path('skills/para-init/references/context-schema.md').read_text()
for key in ['execution.base','execution.pr','execution.review','execution.merge','archive_target']:
    assert f'`{key}`' in schema, f'missing evidence field {key}'
for raw in re.findall(r'```json\n(.*?)\n```',schema,re.S):
    value=json.loads(raw)
    assert isinstance(value['active_context'],list)
    assert isinstance(value['completed_summaries'],list)
cases=json.loads(Path('tests/fixtures/workflow-cases.json').read_text())['cases']
assert len({c['id'] for c in cases})==len(cases)
assert len({c['assertion_id'] for c in cases})==len(cases)
assert all(c['initial_condition'] and c['expected_outcome'] for c in cases)
assert 'Proceed to the next workflow step' not in Path('skills/para-review/SKILL.md').read_text()
assert '**Work Complete:**' not in Path('skills/para-summarize/assets/summary-template.md').read_text()
assert {'malformed_metadata','ambiguous_checkout_identity'} <= {c['id'] for c in cases}
print('PASS documented evidence schema and acceptance matrix')
PY
