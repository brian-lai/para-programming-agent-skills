#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

clients=(
  ".tmp-claude"
  ".tmp-cursor"
  ".tmp-opencode"
  ".tmp-gemini"
  ".tmp-agents"
)

trap 'rm -rf .tmp-claude .tmp-cursor .tmp-opencode .tmp-gemini .tmp-agents' EXIT

skill_name() {
  awk '
    NR == 1 && $0 == "---" { in_fm = 1; next }
    in_fm && $0 == "---" { exit }
    in_fm && $1 == "name:" {
      sub(/^name:[[:space:]]*/, "")
      gsub(/^"|"$/, "")
      print
      exit
    }
  ' "$1"
}

verify_references_resolve() {
  local skill_file="$1"
  local skill_dir ref target
  skill_dir="$(dirname "$skill_file")"

  while IFS= read -r ref; do
    target="$skill_dir/$ref"
    if [ ! -e "$target" ]; then
      echo "FAIL unresolved reference $ref in $skill_file"
      exit 1
    fi
  done < <(grep -Eo '\.\./[^`)[:space:]]+' "$skill_file" | sort -u || true)
}

verify_skill_tree() {
  local skills_dir="$1"
  local skill_dir skill_file dir_name frontmatter_name

  for skill_dir in "$skills_dir"/*; do
    [ -d "$skill_dir" ] || continue
    skill_file="$skill_dir/SKILL.md"
    dir_name="$(basename "$skill_dir")"

    [ -f "$skill_file" ] || { echo "FAIL $dir_name missing SKILL.md"; exit 1; }

    frontmatter_name="$(skill_name "$skill_file")"
    [ "$frontmatter_name" = "$dir_name" ] || {
      echo "FAIL $skill_file name $frontmatter_name does not match directory $dir_name"
      exit 1
    }

    verify_references_resolve "$skill_file"
  done
}

verify_single_skill_fallbacks() {
  local skill_dir="$1"
  local skill_file="$skill_dir/SKILL.md"
  local ref

  while IFS= read -r ref; do
    if ! grep -Fq "If $ref is not available" "$skill_file"; then
      echo "FAIL $skill_file references $ref without single-skill fallback phrase"
      exit 1
    fi
  done < <(grep -Eo '\.\./para-[^`)[:space:]]+' "$skill_file" | sort -u || true)
}

for client in "${clients[@]}"; do
  mkdir -p "$client/skills"
  cp -R skills/. "$client/skills/"
  cp -R docs "$client/docs"
  verify_skill_tree "$client/skills"
done

for skill_dir in skills/*; do
  [ -d "$skill_dir" ] || continue
  verify_single_skill_fallbacks "$skill_dir"
done

echo "PASS multi-client layout compatibility"
