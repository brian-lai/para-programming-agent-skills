#!/usr/bin/env bash
# Asserts each SKILL.md `description:` field is 1–1024 bytes.
set -euo pipefail
fail=0
for skill_md in skills/*/SKILL.md; do
  desc=$(awk '/^---$/{c++; next} c==1 && /^description:/{sub(/^description:[[:space:]]*/, ""); print; exit}' "$skill_md")
  bytes=$(printf '%s' "$desc" | wc -c | tr -d ' ')
  if [ "$bytes" -ge 1 ] && [ "$bytes" -le 1024 ]; then
    echo "PASS $(basename "$(dirname "$skill_md")"): ${bytes} bytes"
  else
    echo "FAIL $(basename "$(dirname "$skill_md")"): description is ${bytes} bytes (must be 1–1024)"
    fail=1
  fi
done
exit "$fail"
