#!/usr/bin/env bash
# Portable skills must leave model and effort selection to the active host.
set -euo pipefail
command -v yq >/dev/null 2>&1 || { echo "FAIL: yq required"; exit 1; }

fail=0
count=0
while IFS= read -r skill_md; do
  count=$((count + 1))
  skill_name=$(basename "$(dirname "$skill_md")")
  frontmatter=$(awk '/^---$/{c++; if (c==2) exit; next} c==1' "$skill_md")
  model=$(printf '%s\n' "$frontmatter" | yq 'has("model")')
  effort=$(printf '%s\n' "$frontmatter" | yq 'has("effort")')
  metadata_model=$(printf '%s\n' "$frontmatter" | yq '(.metadata // {}) | has("model")')
  metadata_effort=$(printf '%s\n' "$frontmatter" | yq '(.metadata // {}) | has("effort")')
  if [ "$model" = "true" ] || [ "$effort" = "true" ] || [ "$metadata_model" = "true" ] || [ "$metadata_effort" = "true" ]; then
    echo "FAIL $skill_md declares provider-specific model or effort routing"
    fail=1
  else
    echo "PASS $skill_name has no model or effort routing"
  fi
done < <(find skills -mindepth 2 -maxdepth 2 -type f -name SKILL.md | sort)

if [ "$count" -eq 0 ]; then
  echo "FAIL: no skill files found"
  exit 1
fi
exit "$fail"
