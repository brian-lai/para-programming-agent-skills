#!/usr/bin/env bash
# Asserts each skill dir name matches its SKILL.md frontmatter `name:` field.
# Default: permissive (exits 0, prints FAIL lines for visibility).
# STRICT=1: exits 1 if any mismatch found.
set -euo pipefail
STRICT="${STRICT:-0}"
fail=0
for skill_md in skills/*/SKILL.md; do
  dir=$(basename "$(dirname "$skill_md")")
  name=$(awk '/^---$/{c++; next} c==1 && /^name:/{sub(/^name:[[:space:]]*/, ""); print; exit}' "$skill_md")
  if [ "$dir" = "$name" ]; then
    echo "PASS $dir"
  else
    echo "FAIL $dir: name=$name but dir=$dir"
    fail=1
  fi
done
[ "$STRICT" = "1" ] && exit "$fail" || exit 0
