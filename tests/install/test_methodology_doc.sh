#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DOC="$REPO_ROOT/docs/METHODOLOGY.md"

[ -f "$DOC" ] || { echo "FAIL docs/METHODOLOGY.md missing"; exit 1; }

line_count="$(wc -l < "$DOC" | tr -d ' ')"
[ "$line_count" -ge 300 ] || { echo "FAIL docs/METHODOLOGY.md has $line_count lines, expected at least 300"; exit 1; }

echo "PASS methodology doc depth"
