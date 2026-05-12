#!/usr/bin/env bash
# Asserts para-research references its bundled research template.
set -euo pipefail
SKILL_MD="skills/para-research/SKILL.md"
TEMPLATE="skills/para-research/assets/research-template.md"
body=$(awk '/^---$/{c++; next} c>=2' "$SKILL_MD")
fail=0

if echo "$body" | grep -q 'assets/research-template.md'; then
  echo "PASS SKILL.md body references assets/research-template.md"
else
  echo "FAIL SKILL.md body does not reference assets/research-template.md"
  fail=1
fi

if [ -f "$TEMPLATE" ]; then
  echo "PASS $TEMPLATE exists"
else
  echo "FAIL $TEMPLATE does not exist"
  fail=1
fi

exit "$fail"
