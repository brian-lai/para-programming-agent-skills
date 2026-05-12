#!/usr/bin/env bash
# Asserts para-plan documents conditional Round 3 self-review.
set -euo pipefail
SKILL_MD="skills/para-plan/SKILL.md"
body=$(awk '/^---$/{c++; next} c>=2' "$SKILL_MD")
fail=0

for phrase in "Round 3 (conditional)" "more than 3 substantive changes"; do
  if echo "$body" | grep -qF "$phrase"; then
    echo "PASS found: $phrase"
  else
    echo "FAIL missing: $phrase"
    fail=1
  fi
done

exit "$fail"
