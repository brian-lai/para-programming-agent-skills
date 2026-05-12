#!/usr/bin/env bash
# Asserts para-plan documents checklist-as-commit atomicity.
set -euo pipefail
SKILL_MD="skills/para-plan/SKILL.md"
body=$(awk '/^---$/{c++; next} c>=2' "$SKILL_MD")
fail=0

for phrase in "Checklist = commit" "commit message" "atomic -- one logical change per item"; do
  if echo "$body" | grep -qF "$phrase"; then
    echo "PASS found: $phrase"
  else
    echo "FAIL missing: $phrase"
    fail=1
  fi
done

exit "$fail"
