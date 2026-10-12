#!/usr/bin/env bash
# Documentation/schema checks only; live compliance is evaluated separately.
set -euo pipefail
python3 - <<'PY'
import json,re
from pathlib import Path
schema=Path('skills/para-init/references/context-schema.md').read_text()
for key in ['execution.base','execution.pr','execution.review','execution.merge','archive_target']:
    assert f'`{key}`' in schema, f'missing evidence field {key}'
assert '`execution.plan`' in schema, 'missing simple-task plan binding'
assert 'match exactly one `active_context` entry' in schema, 'simple plan binding must match one active plan'
assert 'ask before writing context' in schema, 'ambiguous simple plan selection must stop before writes'
assert 'receipt plan source equal to the archived snapshot\'s `execution.plan`' in schema, 'receipt must bind to selected simple plan'
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
execute=Path('skills/para-execute/SKILL.md').read_text()
workflow=Path('skills/para-workflow/SKILL.md').read_text()
archive=Path('skills/para-archive/SKILL.md').read_text()
assert '`execution.plan`' in execute and 'Persist and reread' in execute, 'direct execute must bind plan before implementation'
assert 'ask before writing context' in execute, 'direct execute must stop on ambiguous plan selection'
assert 'do not overwrite its binding' in execute, 'direct execute must preserve a different active binding'
assert '`execution.plan`' in workflow and 'Persist and reread' in workflow, 'workflow must bind plan before execution'
assert 'exactly one receipt plan source equals' in workflow and '`execution.plan`' in workflow, 'workflow must verify receipt against selected plan'
assert 'do not overwrite its binding' in workflow, 'workflow must preserve a different active binding'
assert 'Never infer the plan from the whole active-plan array' in archive, 'archive must not guess the selected plan'
assert 'exactly one receipt plan source' in archive and '`execution.plan`' in archive, 'archive receipt must match simple plan binding'
assert {'malformed_metadata','ambiguous_checkout_identity'} <= {c['id'] for c in cases}
print('PASS documented evidence schema and acceptance matrix')
PY
