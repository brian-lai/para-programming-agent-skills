#!/usr/bin/env bash
set -euo pipefail
command -v yq >/dev/null 2>&1 || { echo "FAIL: yq required"; exit 1; }

SKILL_MD="skills/para-execute/SKILL.md"
frontmatter=$(awk '/^---$/{c++; if (c==2) exit; next} c==1' "$SKILL_MD")
name=$(echo "$frontmatter" | yq '.name // ""')
desc=$(echo "$frontmatter" | yq '.description // ""')
model=$(echo "$frontmatter" | yq '.model // ""')
effort=$(echo "$frontmatter" | yq '.effort // ""')
meta_model=$(echo "$frontmatter" | yq '.metadata.model // ""')
fail=0

[ "$name" = "para-execute" ] && echo "PASS name=para-execute" || { echo "FAIL name=$name"; fail=1; }
desc_bytes=$(printf '%s' "$desc" | wc -c | tr -d ' ')
if [ "$desc_bytes" -ge 1 ] && [ "$desc_bytes" -le 1024 ]; then echo "PASS description ($desc_bytes bytes)"; else echo "FAIL description length $desc_bytes"; fail=1; fi
[ "$model" = "sonnet" ] && echo "PASS top-level model=sonnet" || { echo "FAIL model=$model"; fail=1; }
[ "$effort" = "medium" ] && echo "PASS top-level effort=medium" || { echo "FAIL effort=$effort"; fail=1; }
[ -z "$meta_model" ] && echo "PASS metadata.model absent" || { echo "FAIL metadata.model=$meta_model"; fail=1; }
exit "$fail"
