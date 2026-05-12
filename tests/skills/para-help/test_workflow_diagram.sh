#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-help/SKILL.md)
if echo "$body" | grep -q 'Research → Plan → Review → Execute → Review → Summarize → Archive'; then
  echo "PASS workflow diagram present"
else
  echo "FAIL missing workflow diagram"
  exit 1
fi
