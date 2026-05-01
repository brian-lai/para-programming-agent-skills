#!/usr/bin/env bash
# Asserts skills/para-init/SKILL.md body (not frontmatter) references
# references/context-schema.md, and that the file exists.
set -euo pipefail
SKILL_MD="skills/para-init/SKILL.md"
SCHEMA="skills/para-init/references/context-schema.md"
fail=0

# Extract body only — skip the first two --- frontmatter delimiters
body=$(awk '/^---$/{c++; next} c>=2' "$SKILL_MD")

if echo "$body" | grep -q 'references/context-schema.md'; then
  echo "PASS SKILL.md body references references/context-schema.md"
else
  echo "FAIL SKILL.md body does not reference references/context-schema.md"
  fail=1
fi

if [ -f "$SCHEMA" ]; then
  echo "PASS $SCHEMA exists"
else
  echo "FAIL $SCHEMA does not exist"
  fail=1
fi

exit "$fail"
