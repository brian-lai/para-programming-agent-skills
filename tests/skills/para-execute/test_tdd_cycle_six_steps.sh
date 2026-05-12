#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-execute/SKILL.md)
fail=0
for phrase in "RED" "GREEN" "commit with the checklist item text as the commit message"; do
  if echo "$body" | grep -qF "$phrase"; then echo "PASS found: $phrase"; else echo "FAIL missing: $phrase"; fail=1; fi
done
exit "$fail"
