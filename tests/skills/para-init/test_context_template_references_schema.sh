#!/usr/bin/env bash
# Asserts skills/para-init/assets/context-template.md contains pointer to
# ../references/context-schema.md (schema lookup from template location).
set -euo pipefail
TEMPLATE="skills/para-init/assets/context-template.md"
[ -f "$TEMPLATE" ] || { echo "FAIL: $TEMPLATE not found"; exit 1; }

if grep -q '\.\./references/context-schema\.md' "$TEMPLATE"; then
  echo "PASS $TEMPLATE references ../references/context-schema.md"
  exit 0
else
  echo "FAIL $TEMPLATE does not reference ../references/context-schema.md"
  exit 1
fi
