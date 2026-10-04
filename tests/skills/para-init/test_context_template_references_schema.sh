#!/usr/bin/env bash
# Generated context must not retain a path valid only inside the source template.
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
s=Path('skills/para-init/assets/context-template.md').read_text()
assert '../references/context-schema.md' not in s
assert 'para-init' in s and 'context-schema.md' in s
print('PASS generated context uses install-independent resource guidance')
PY
