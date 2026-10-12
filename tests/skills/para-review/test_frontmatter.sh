#!/usr/bin/env bash
# Asserts required portable Agent Skills frontmatter for para-review.
set -euo pipefail
command -v yq >/dev/null 2>&1 || { echo "FAIL: yq required"; exit 1; }

SKILL_MD="skills/para-review/SKILL.md"
[ -f "$SKILL_MD" ] || { echo "FAIL: $SKILL_MD not found"; exit 1; }
frontmatter=$(awk '/^---$/{c++; if (c==2) exit; next} c==1' "$SKILL_MD")
name=$(printf '%s\n' "$frontmatter" | yq '.name // ""')
desc=$(printf '%s\n' "$frontmatter" | yq '.description // ""')
fail=0
[ "$name" = "para-review" ] && echo "PASS name=para-review" || { echo "FAIL name=$name"; fail=1; }
desc_bytes=$(printf '%s' "$desc" | wc -c | tr -d ' ')
if [ "$desc_bytes" -ge 1 ] && [ "$desc_bytes" -le 1024 ]; then
  echo "PASS description ($desc_bytes bytes)"
else
  echo "FAIL description length $desc_bytes"
  fail=1
fi
exit "$fail"
