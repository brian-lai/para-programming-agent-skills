#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-help/SKILL.md)
fail=0
for skill in '$para-init' '$para-research' '$para-plan' '$para-review' '$para-execute' '$para-workflow' '$para-summarize' '$para-archive' '$para-status' '$para-check' '$para-help'; do
  if echo "$body" | grep -q -- "$skill"; then echo "PASS listed: $skill"; else echo "FAIL missing: $skill"; fail=1; fi
done
count=$(echo "$body" | grep -o '\$para-[a-z-]*' | wc -l | tr -d ' ')
if [ "$count" -ge 11 ]; then echo "PASS \$para- invocation count $count"; else echo "FAIL \$para- invocation count $count"; fail=1; fi
exit "$fail"
