#!/usr/bin/env bash
# Asserts each SKILL.md body (after frontmatter) is <= 500 lines.
set -euo pipefail
fail=0
for skill_md in skills/*/SKILL.md; do
  body_lines=$(awk '/^---$/{c++; next} c>=2' "$skill_md" | wc -l | tr -d ' ')
  if [ "$body_lines" -le 500 ]; then
    echo "PASS $(basename "$(dirname "$skill_md")"): ${body_lines} body lines"
  else
    echo "FAIL $(basename "$(dirname "$skill_md")"): ${body_lines} body lines (must be <= 500)"
    fail=1
  fi
done
exit "$fail"
