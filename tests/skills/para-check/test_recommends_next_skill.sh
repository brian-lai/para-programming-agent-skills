#!/usr/bin/env bash
set -euo pipefail
if grep -q '/para-plan' skills/para-check/SKILL.md; then
  echo "PASS /para-plan recommendation present"
else
  echo "FAIL missing /para-plan recommendation"
  exit 1
fi
