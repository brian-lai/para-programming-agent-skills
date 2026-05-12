#!/usr/bin/env bash
set -euo pipefail
body=$(awk '/^---$/{c++; next} c>=2' skills/para-workflow/SKILL.md)
if echo "$body" | grep -q 'This step owns PR creation for workflow runs'; then
  echo "PASS workflow owns PR creation"
else
  echo "FAIL missing PR creation ownership phrase"
  exit 1
fi
