#!/usr/bin/env bash
# Asserts skills/para-init/SKILL.md body (not frontmatter) mentions:
#   - AGENTS.md (project file, Codex branding)
#   - ~/.agents/AGENTS.md (global methodology path)
set -euo pipefail
SKILL_MD="skills/para-init/SKILL.md"
[ -f "$SKILL_MD" ] || { echo "FAIL: $SKILL_MD not found"; exit 1; }

fail=0

# Extract body only — skip the first two --- frontmatter delimiters so
# frontmatter description text can't trivially satisfy these assertions.
body=$(awk '/^---$/{c++; next} c>=2' "$SKILL_MD")

if echo "$body" | grep -q 'AGENTS\.md'; then
  echo "PASS body mentions AGENTS.md"
else
  echo "FAIL body does not mention AGENTS.md"
  fail=1
fi

if echo "$body" | grep -q '~/\.agents/AGENTS\.md'; then
  echo "PASS body mentions ~/.agents/AGENTS.md"
else
  echo "FAIL body does not mention ~/.agents/AGENTS.md"
  fail=1
fi

exit "$fail"
