#!/usr/bin/env bash
# Asserts CHANGELOG.md has a 3.0.0 section entry.
set -euo pipefail
if grep -q '## \[3\.0\.0' CHANGELOG.md; then
  echo "PASS CHANGELOG has 3.0.0 entry"
  exit 0
else
  echo "FAIL CHANGELOG missing 3.0.0 entry"
  exit 1
fi
