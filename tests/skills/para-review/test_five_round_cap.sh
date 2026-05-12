#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-review/SKILL.md)
if echo "$body" | grep -Eq '5-round|five-round' && echo "$body" | grep -qi 'convergence'; then
  echo "PASS 5-round convergence cap present"
else
  echo "FAIL missing 5-round convergence cap"
  exit 1
fi
