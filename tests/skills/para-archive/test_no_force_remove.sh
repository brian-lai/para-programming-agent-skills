#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-archive/SKILL.md)
if echo "$body" | grep -q 'do NOT force-remove'; then
  echo "PASS force-remove warning present"
else
  echo "FAIL missing force-remove warning"
  exit 1
fi
