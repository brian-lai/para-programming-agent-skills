#!/usr/bin/env bash
# Runs all conformance tests and aggregates exit codes.
# Passes STRICT and other env vars through to individual tests.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fail=0

for test_script in "$SCRIPT_DIR"/test_*.sh; do
  echo "--- $(basename "$test_script") ---"
  if bash "$test_script"; then
    echo "PASS $(basename "$test_script")"
  else
    echo "FAIL $(basename "$test_script")"
    fail=1
  fi
  echo ""
done

if [ "$fail" -eq 0 ]; then
  echo "All conformance tests passed."
else
  echo "One or more conformance tests FAILED."
fi
exit "$fail"
