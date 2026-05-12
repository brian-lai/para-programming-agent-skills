#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-check/SKILL.md)
fail=0
for phrase in "code changes" "bug fixes" "features" "Read-only" "explanations" "navigation"; do
  if echo "$body" | grep -q "$phrase"; then echo "PASS found: $phrase"; else echo "FAIL missing: $phrase"; fail=1; fi
done
if echo "$body" | grep -q 'USE PARA WORKFLOW' && echo "$body" | grep -q 'SKIP PARA'; then echo "PASS verdict labels present"; else echo "FAIL missing verdict labels"; fail=1; fi
exit "$fail"
