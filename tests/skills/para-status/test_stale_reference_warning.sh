#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-status/SKILL.md)
if echo "$body" | grep -q 'Worktree referenced in context.md but directory missing'; then
  echo "PASS stale-reference warning present"
else
  echo "FAIL missing stale-reference warning"
  exit 1
fi
