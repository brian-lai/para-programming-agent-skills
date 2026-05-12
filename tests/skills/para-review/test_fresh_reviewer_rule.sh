#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-review/SKILL.md)
if echo "$body" | grep -Eq 'fresh subagent|fresh reviewer' && echo "$body" | grep -q 'never continue a previous reviewer'; then
  echo "PASS fresh reviewer rule present"
else
  echo "FAIL missing fresh reviewer rule"
  exit 1
fi
