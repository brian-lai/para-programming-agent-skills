#!/usr/bin/env bash
# Verifies:
# 1. Every path referenced inline in SKILL.md bodies (assets/, references/, docs/, ../)
#    resolves to a real file.
# 2. Cross-skill (../) references appearing in a SKILL.md body are registered in the
#    spec yaml's cross_skill_references.paths list.
#
# Note: The spec registry may list future entries (phases 2–6 add them).
# This test only checks references that currently appear in SKILL.md bodies —
# not all registry entries. That keeps the test honestly red/green per phase.
set -euo pipefail

command -v yq >/dev/null 2>&1 || { echo "FAIL: yq required — install via 'brew install yq' (mikefarah/yq v4+)"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SPEC="$SCRIPT_DIR/spec.yaml"
if [ ! -f "$SPEC" ]; then
  echo "FAIL: spec file not found at $SPEC"
  exit 1
fi
REGISTRY_FILE=$(mktemp)
trap 'rm -f "$REGISTRY_FILE"' EXIT
fail=0

# Build registry as "from|to" lines in a temp file (bash 3-compat, no assoc arrays)
count=$(yq '.cross_skill_references.paths | length' "$SPEC")
for i in $(seq 0 $((count-1))); do
  reg_from=$(yq ".cross_skill_references.paths[$i].from" "$SPEC")
  reg_to=$(yq ".cross_skill_references.paths[$i].to" "$SPEC")
  echo "${reg_from}|${reg_to}" >> "$REGISTRY_FILE"
done

for skill_md in skills/*/SKILL.md; do
  skill_dir=$(dirname "$skill_md")
  body=$(awk '/^---$/{c++; next} c>=2' "$skill_md")

  while IFS= read -r ref; do
    resolved="${skill_dir}/${ref}"
    if [ ! -f "$resolved" ]; then
      echo "FAIL $skill_md → $ref (resolved=$resolved does not exist)"
      fail=1
    else
      # For cross-skill refs (start with ../), verify registry entry exists
      if echo "$ref" | grep -q '^\.\./'; then
        key="${skill_md}|${ref}"
        if grep -qF "$key" "$REGISTRY_FILE"; then
          echo "PASS $skill_md → $ref (in registry)"
        else
          echo "FAIL $skill_md → $ref is a cross-skill ref not in the spec registry"
          fail=1
        fi
      else
        echo "PASS $skill_md → $ref"
      fi
    fi
  done < <(echo "$body" | grep -oE '(assets|references|\.\.|docs)/[A-Za-z0-9_./\-]+\.(md|yaml|sh|json)' | sort -u)
done

exit "$fail"
