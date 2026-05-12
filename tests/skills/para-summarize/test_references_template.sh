#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-summarize/SKILL.md)
fail=0
if echo "$body" | grep -q 'assets/summary-template.md'; then echo "PASS template reference present"; else echo "FAIL missing template reference"; fail=1; fi
if [ -f skills/para-summarize/assets/summary-template.md ]; then echo "PASS summary template exists"; else echo "FAIL summary template missing"; fail=1; fi
exit "$fail"
