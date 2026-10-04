#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
import json,os,subprocess,tempfile
from pathlib import Path
script=str(Path('tests/conformance/test_context_budget.sh').resolve())
m=json.loads(Path('tests/fixtures/skill-context-budget.json').read_text())
with tempfile.TemporaryDirectory(prefix='para-budget-') as d:
    root=Path(d)
    for p in {p for s in m['scenarios'].values() for p in s['paths']}:
        dest=root/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(Path(p).read_bytes())
    env=dict(os.environ,PARA_BUDGET_ROOT=str(root))
    assert subprocess.run(['bash',script],env=env,capture_output=True).returncode==0
    p=root/'resources/AGENTS.md';p.write_bytes(p.read_bytes()+b'X'*40000)
    assert subprocess.run(['bash',script],env=env,capture_output=True).returncode!=0,'growth was accepted'
    s=m['scenarios']['simple_plan'];s['paths'].remove(s['required_resources'][0])
    manifest=root/'omitted.json';manifest.write_text(json.dumps(m));env.pop('PARA_BUDGET_ROOT');env['PARA_BUDGET_MANIFEST']=str(manifest)
    assert subprocess.run(['bash',script],env=env,capture_output=True).returncode!=0,'omitted reference accepted'
print('PASS growth and omitted mandatory-resource sensitivity')
PY
