#!/usr/bin/env bash
set -euo pipefail
count=$(grep -c -- '--branch=name' skills/para-execute/SKILL.md || true)
if [ "$count" -eq 0 ]; then
  echo "PASS --branch=name absent"
else
  echo "FAIL --branch=name found $count time(s)"
  exit 1
fi
