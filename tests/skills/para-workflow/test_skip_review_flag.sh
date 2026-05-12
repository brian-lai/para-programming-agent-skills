#!/usr/bin/env bash
set -euo pipefail
if grep -q -- '--skip-review' skills/para-workflow/SKILL.md; then
  echo "PASS --skip-review documented"
else
  echo "FAIL --skip-review missing"
  exit 1
fi
