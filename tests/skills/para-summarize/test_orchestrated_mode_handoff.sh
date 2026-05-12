#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-summarize/SKILL.md)
if echo "$body" | grep -q 'invoked as Step 4 of /para-workflow' && echo "$body" | grep -qi 'skip.*PR'; then
  echo "PASS orchestrated handoff documented"
else
  echo "FAIL missing orchestrated handoff"
  exit 1
fi
