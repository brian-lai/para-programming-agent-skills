#!/usr/bin/env bash
# Asserts skills/para-init/SKILL.md body references references/context-schema.md
# and that the file exists.
set -euo pipefail
SKILL_MD="skills/para-init/SKILL.md"
SCHEMA="skills/para-init/references/context-schema.md"
fail=0

if grep -q 'references/context-schema.md' "$SKILL_MD"; then
  echo "PASS SKILL.md references references/context-schema.md"
else
  echo "FAIL SKILL.md does not reference references/context-schema.md"
  fail=1
fi

if [ -f "$SCHEMA" ]; then
  echo "PASS $SCHEMA exists"
else
  echo "FAIL $SCHEMA does not exist"
  fail=1
fi

exit "$fail"
