#!/usr/bin/env bash
# Documentation length is not evidence of quality. Check the published contract link.
set -euo pipefail
python3 - <<'PY'
import re
from pathlib import Path
p=Path('docs/METHODOLOGY.md');s=p.read_text()
links=re.findall(r'\]\(([^)]+)\)',s)
assert any('context-schema.md' in x for x in links)
for x in links:
 if not x.startswith('http'): assert (p.parent/x).exists(),x
print('PASS methodology links resolve')
PY
