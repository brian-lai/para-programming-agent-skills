#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-status/SKILL.md)
fail=0
for state in "No context" "Idle" "Planning" "Executing" "Summarized"; do
  if echo "$body" | grep -q "$state"; then echo "PASS state: $state"; else echo "FAIL missing state: $state"; fail=1; fi
done
if echo "$body" | grep -qi 'next step'; then echo "PASS next-step guidance present"; else echo "FAIL missing next-step guidance"; fail=1; fi
exit "$fail"
