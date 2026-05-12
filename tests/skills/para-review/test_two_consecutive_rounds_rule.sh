#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-review/SKILL.md)
if echo "$body" | grep -q 'two consecutive rounds produce the same MUST FIX issues'; then
  echo "PASS repeated-MUST-FIX convergence rule present"
else
  echo "FAIL missing repeated-MUST-FIX convergence rule"
  exit 1
fi
