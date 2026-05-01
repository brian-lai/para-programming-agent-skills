#!/usr/bin/env bash
# Asserts skills/para-init/SKILL.md body mentions:
#   - AGENTS.md (project file, Codex branding)
#   - ~/.agents/AGENTS.md (global methodology path)
set -euo pipefail
SKILL_MD="skills/para-init/SKILL.md"
[ -f "$SKILL_MD" ] || { echo "FAIL: $SKILL_MD not found"; exit 1; }

fail=0

if grep -q 'AGENTS\.md' "$SKILL_MD"; then
  echo "PASS body mentions AGENTS.md"
else
  echo "FAIL body does not mention AGENTS.md"
  fail=1
fi

if grep -q '~/\.agents/AGENTS\.md' "$SKILL_MD"; then
  echo "PASS body mentions ~/.agents/AGENTS.md"
else
  echo "FAIL body does not mention ~/.agents/AGENTS.md"
  fail=1
fi

exit "$fail"
