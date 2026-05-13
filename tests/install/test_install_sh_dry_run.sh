#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
tmp_home="$(mktemp -d)"
trap 'rm -rf "$tmp_home"' EXIT

HOME="$tmp_home" bash "$REPO_ROOT/scripts/install.sh" --dry-run >/dev/null

if [ -e "$tmp_home/.agents" ]; then
  echo "FAIL dry-run wrote to HOME"
  exit 1
fi

echo "PASS install dry-run made no HOME writes"
