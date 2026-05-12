#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-archive/SKILL.md)
if echo "$body" | grep -q '../para-init/assets/context-template.md'; then
  echo "PASS context-template seed reference present"
else
  echo "FAIL missing context-template seed reference"
  exit 1
fi
