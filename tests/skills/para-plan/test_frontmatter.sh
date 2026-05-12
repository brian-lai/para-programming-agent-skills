#!/usr/bin/env bash
# Asserts skills/para-plan/SKILL.md frontmatter has:
#   name: para-plan
#   description: (1-1024 bytes)
#   top-level model: opus
#   top-level effort: high
# AND that metadata.model is absent (catches regression to nested form).
set -euo pipefail
command -v yq >/dev/null 2>&1 || { echo "FAIL: yq required"; exit 1; }

SKILL_MD="skills/para-plan/SKILL.md"
[ -f "$SKILL_MD" ] || { echo "FAIL: $SKILL_MD not found"; exit 1; }

frontmatter=$(awk '/^---$/{c++; if (c==2) exit; next} c==1' "$SKILL_MD")

name=$(echo "$frontmatter" | yq '.name // ""')
desc=$(echo "$frontmatter" | yq '.description // ""')
model=$(echo "$frontmatter" | yq '.model // ""')
effort=$(echo "$frontmatter" | yq '.effort // ""')
meta_model=$(echo "$frontmatter" | yq '.metadata.model // ""')

fail=0

if [ "$name" = "para-plan" ]; then
  echo "PASS name=para-plan"
else
  echo "FAIL name=$name (expected para-plan)"
  fail=1
fi

desc_bytes=$(printf '%s' "$desc" | wc -c | tr -d ' ')
if [ "$desc_bytes" -ge 1 ] && [ "$desc_bytes" -le 1024 ]; then
  echo "PASS description ($desc_bytes bytes)"
else
  echo "FAIL description length $desc_bytes (need 1-1024)"
  fail=1
fi

if [ "$model" = "opus" ]; then
  echo "PASS top-level model=opus"
else
  echo "FAIL model=$model (expected opus at top level, NOT under metadata)"
  fail=1
fi

if [ "$effort" = "high" ]; then
  echo "PASS top-level effort=high"
else
  echo "FAIL effort=$effort (expected high at top level)"
  fail=1
fi

if [ -z "$meta_model" ]; then
  echo "PASS metadata.model absent (correct placement)"
else
  echo "FAIL metadata.model=$meta_model — should be at top level, not nested"
  fail=1
fi

exit "$fail"
