#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MARKETPLACE_JSON="$REPO_ROOT/.claude-plugin/marketplace.json"

jq -e '.plugins[0].source and .plugins[0].name' "$MARKETPLACE_JSON" >/dev/null

source="$(jq -r '.plugins[0].source' "$MARKETPLACE_JSON")"
name="$(jq -r '.plugins[0].name' "$MARKETPLACE_JSON")"

[ "$source" = "./" ] || { echo "FAIL expected first plugin source ./, got $source"; exit 1; }
[ "$name" = "para-skills" ] || { echo "FAIL expected first plugin name para-skills, got $name"; exit 1; }

echo "PASS claude marketplace metadata"
