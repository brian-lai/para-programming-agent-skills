#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-workflow/SKILL.md)
fail=0
if echo "$body" | grep -q '../para-init/references/context-schema.md'; then echo "PASS schema reference present"; else echo "FAIL missing schema reference"; fail=1; fi
if echo "$body" | grep -q 'If ../para-init/references/context-schema.md is not available'; then echo "PASS fallback note present"; else echo "FAIL missing fallback note"; fail=1; fi
if echo "$body" | grep -q '"workflow"'; then echo "FAIL inline workflow JSON literal present"; fail=1; else echo "PASS no inline workflow JSON literal"; fi
exit "$fail"
