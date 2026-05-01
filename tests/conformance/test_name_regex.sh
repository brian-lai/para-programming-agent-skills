#!/usr/bin/env bash
# Asserts each SKILL.md `name:` field matches ^[a-z0-9]+(-[a-z0-9]+)*$
set -euo pipefail
STRICT="${STRICT:-1}"
fail=0
regex='^[a-z0-9]+(-[a-z0-9]+)*$'
for skill_md in skills/*/SKILL.md; do
  name=$(awk '/^---$/{c++; next} c==1 && /^name:/{sub(/^name:[[:space:]]*/, ""); print; exit}' "$skill_md")
  if echo "$name" | grep -qE "$regex"; then
    echo "PASS $name"
  else
    echo "FAIL $name: does not match $regex"
    fail=1
  fi
done
exit "$fail"
