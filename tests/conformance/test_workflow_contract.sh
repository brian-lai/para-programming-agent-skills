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
assert '`simple-plan-binding.md`' in schema, 'schema must point to the detailed simple-plan contract'
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
binding=Path('skills/para-init/references/simple-plan-binding.md').read_text()
assert 'simple-plan-binding.md' in execute and 'before implementation' in execute, 'direct execute must load binding rules before implementation'
assert 'simple-plan-binding.md' in workflow and 'before execution' in workflow, 'workflow must load binding rules before execution'
assert 'simple-plan-binding.md' in archive and 'before any move or cleanup' in archive, 'archive must load binding rules before mutation'
assert 'If multiple plans remain ambiguous, ask before' in binding, 'ambiguous plan selection must stop before writes'
assert 'never overwrite the binding' in binding, 'a different active binding must be preserved'
assert '`execution.plan` before implementation' in binding, 'simple execution must bind before implementation'
assert 'source equals `execution.plan`' in binding, 'receipt must bind to selected simple plan'
assert 'one exact `active_context` match' in binding, 'simple plan binding must match one active plan'
assert 'exactly one receipt plan source equals' in workflow and '`execution.plan`' in workflow, 'workflow must verify receipt against selected plan'
assert 'never choose by array order' in binding, 'simple plan selection must not depend on active_context ordering'
assert {'malformed_metadata','ambiguous_checkout_identity'} <= {c['id'] for c in cases}
print('PASS documented evidence schema and acceptance matrix')
PY
