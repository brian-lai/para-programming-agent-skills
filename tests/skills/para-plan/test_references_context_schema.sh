#!/usr/bin/env bash
# Asserts para-plan references the canonical context schema and includes
# a partial-install fallback note.
set -euo pipefail
SKILL_MD="skills/para-plan/SKILL.md"
SCHEMA="skills/para-init/references/context-schema.md"
body=$(awk '/^---$/{c++; next} c>=2' "$SKILL_MD")
fail=0

if echo "$body" | grep -q '../para-init/references/context-schema.md'; then
  echo "PASS SKILL.md body references ../para-init/references/context-schema.md"
else
  echo "FAIL SKILL.md body does not reference ../para-init/references/context-schema.md"
  fail=1
fi

if [ -f "$SCHEMA" ]; then
  echo "PASS $SCHEMA exists"
else
  echo "FAIL $SCHEMA does not exist"
  fail=1
fi

if echo "$body" | grep -q 'If ../para-init/references/context-schema.md is not available'; then
  echo "PASS fallback note present"
else
  echo "FAIL missing fallback note for unavailable context schema"
  fail=1
fi

exit "$fail"
