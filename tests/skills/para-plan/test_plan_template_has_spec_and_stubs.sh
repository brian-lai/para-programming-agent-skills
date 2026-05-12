#!/usr/bin/env bash
# Asserts the simple plan template has exactly one Spec and one Stubs section.
set -euo pipefail
TEMPLATE="skills/para-plan/assets/plan-template.md"
[ -f "$TEMPLATE" ] || { echo "FAIL: $TEMPLATE not found"; exit 1; }

spec_count=$(grep -c '^## Spec$' "$TEMPLATE" || true)
stubs_count=$(grep -c '^## Stubs$' "$TEMPLATE" || true)
fail=0

if [ "$spec_count" -eq 1 ]; then
  echo "PASS exactly one ## Spec"
else
  echo "FAIL expected one ## Spec, found $spec_count"
  fail=1
fi

if [ "$stubs_count" -eq 1 ]; then
  echo "PASS exactly one ## Stubs"
else
  echo "FAIL expected one ## Stubs, found $stubs_count"
  fail=1
fi

exit "$fail"
