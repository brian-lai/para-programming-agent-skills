#!/usr/bin/env bash
# Asserts para-plan contains concrete phase-split triggers.
set -euo pipefail
SKILL_MD="skills/para-plan/SKILL.md"
body=$(awk '/^---$/{c++; next} c>=2' "$SKILL_MD")
fail=0

for phrase in \
  "More than 5 files with cross-file refactoring" \
  "2 or more architectural layers" \
  'merged to `main`'; do
  if echo "$body" | grep -qF "$phrase"; then
    echo "PASS found: $phrase"
  else
    echo "FAIL missing: $phrase"
    fail=1
  fi
done

exit "$fail"
