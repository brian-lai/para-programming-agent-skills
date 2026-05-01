#!/usr/bin/env bash
# Runs conformance tests for the para-programming-agent-skills repository.
# Usage: scripts/validate-skills.sh [--strict]
#
# By default, name/dir mismatch test is permissive (reports FAILs but exits 0).
# Pass --strict or set STRICT=1 to enable the full gate.
#
# Note: This script does NOT invoke tests/e2e/multi-client-layout-compat.sh.
# The E2E test has its own invocation path and is wired into CI in phase 7.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

for arg in "$@"; do
  case "$arg" in
    --strict) export STRICT=1 ;;
  esac
done

command -v yq >/dev/null 2>&1 || { echo "ERROR: yq required — install via 'brew install yq' (mikefarah/yq v4+)"; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "ERROR: jq required — install via 'brew install jq'"; exit 1; }
command -v shellcheck >/dev/null 2>&1 || echo "WARN: shellcheck not found — skipping shell lint"

cd "$REPO_ROOT"
bash "$REPO_ROOT/tests/conformance/run_all.sh"
