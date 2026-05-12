#!/usr/bin/env bash
# Asserts para-plan documents the review/self-review cap.
set -euo pipefail
SKILL_MD="skills/para-plan/SKILL.md"
body=$(awk '/^---$/{c++; next} c>=2' "$SKILL_MD")

if echo "$body" | grep -Eq '5-round|five-round'; then
  echo "PASS review cap mentioned"
else
  echo "FAIL missing 5-round review cap"
  exit 1
fi
