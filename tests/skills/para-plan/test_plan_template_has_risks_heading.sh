#!/usr/bin/env bash
# Asserts the simple plan template uses ## Risks, not the old heading.
set -euo pipefail
TEMPLATE="skills/para-plan/assets/plan-template.md"
[ -f "$TEMPLATE" ] || { echo "FAIL: $TEMPLATE not found"; exit 1; }

risks_count=$(grep -c '^## Risks$' "$TEMPLATE" || true)
old_count=$(grep -c '^## Risks & Edge Cases' "$TEMPLATE" || true)
fail=0

if [ "$risks_count" -eq 1 ]; then
  echo "PASS exactly one ## Risks"
else
  echo "FAIL expected one ## Risks, found $risks_count"
  fail=1
fi

if [ "$old_count" -eq 0 ]; then
  echo "PASS old Risks & Edge Cases heading absent"
else
  echo "FAIL old Risks & Edge Cases heading still present"
  fail=1
fi

exit "$fail"
