#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-summarize/SKILL.md)
if echo "$body" | grep -qi 'standalone' && echo "$body" | grep -q 'git .*push' && echo "$body" | grep -q 'gh pr create'; then
  echo "PASS standalone PR flow documented"
else
  echo "FAIL missing standalone PR flow"
  exit 1
fi
