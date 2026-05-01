#!/usr/bin/env bash
# Runs all conformance tests and aggregates exit codes.
# Passes STRICT and other env vars through to individual tests.
# Also inspects child output: if a child exits 0 but printed "FAIL " lines
# (e.g. permissive-mode tests that report failures without exiting non-zero),
# the runner counts it as a failure.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fail=0

for test_script in "$SCRIPT_DIR"/test_*.sh; do
  echo "--- $(basename "$test_script") ---"
  output=$(bash "$test_script" 2>&1) && rc=0 || rc=$?
  echo "$output"
  if [ "$rc" -ne 0 ]; then
    echo "FAIL $(basename "$test_script") (exit $rc)"
    fail=1
  elif echo "$output" | grep -q '^FAIL '; then
    echo "FAIL $(basename "$test_script") (child reported FAIL lines while exiting 0 — treating as failure)"
    fail=1
  else
    echo "PASS $(basename "$test_script")"
  fi
  echo ""
done

if [ "$fail" -eq 0 ]; then
  echo "All conformance tests passed."
else
  echo "One or more conformance tests FAILED."
fi
exit "$fail"
