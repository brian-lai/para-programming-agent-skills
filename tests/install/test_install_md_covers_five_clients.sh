#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DOC="$REPO_ROOT/INSTALL.md"

for heading in "Claude Code" "OpenAI Codex" "OpenCode" "Cursor" "Gemini"; do
  grep -q "^## $heading$" "$DOC" || { echo "FAIL INSTALL.md missing ## $heading"; exit 1; }
done

heading_count="$(grep -c '^## ' "$DOC")"
[ "$heading_count" -ge 5 ] || { echo "FAIL INSTALL.md has $heading_count second-level headings, expected at least 5"; exit 1; }

echo "PASS install guide covers five clients"
