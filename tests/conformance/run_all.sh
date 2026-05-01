#!/usr/bin/env bash
# Runs all conformance tests + per-skill tests and aggregates exit codes.
# Passes STRICT and other env vars through to individual tests.
# Also inspects child output: if a child exits 0 but printed "FAIL " lines
# (e.g. permissive-mode tests that report failures without exiting non-zero),
# the runner counts it as a failure.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
fail=0

run_test() {
  local test_script="$1"
  local label="$2"
  echo "--- $label ---"
  local output rc
  output=$(bash "$test_script" 2>&1) && rc=0 || rc=$?
  echo "$output"
  if [ "$rc" -ne 0 ]; then
    echo "FAIL $label (exit $rc)"
    fail=1
  elif echo "$output" | grep -q '^FAIL '; then
    echo "FAIL $label (child reported FAIL lines while exiting 0 — treating as failure)"
    fail=1
  else
    echo "PASS $label"
  fi
  echo ""
}

cd "$REPO_ROOT"

# 1. Global conformance tests
for test_script in "$SCRIPT_DIR"/test_*.sh; do
  run_test "$test_script" "conformance/$(basename "$test_script")"
done

# 2. Per-skill tests under tests/skills/<skill>/test_*.sh
if [ -d "$REPO_ROOT/tests/skills" ]; then
  while IFS= read -r test_script; do
    rel="${test_script#$REPO_ROOT/tests/}"
    run_test "$test_script" "$rel"
  done < <(find "$REPO_ROOT/tests/skills" -type f -name 'test_*.sh' | sort)
fi

if [ "$fail" -eq 0 ]; then
  echo "All conformance tests passed."
else
  echo "One or more conformance tests FAILED."
fi
exit "$fail"
