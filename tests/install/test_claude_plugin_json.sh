#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PLUGIN_JSON="$REPO_ROOT/.claude-plugin/plugin.json"

jq -e '.name and .version and .description and .license' "$PLUGIN_JSON" >/dev/null

name="$(jq -r '.name' "$PLUGIN_JSON")"
version="$(jq -r '.version' "$PLUGIN_JSON")"

[ "$name" = "para-skills" ] || { echo "FAIL expected .name para-skills, got $name"; exit 1; }
[[ "$version" =~ ^3\.0\.0$ ]] || { echo "FAIL expected .version 3.0.0, got $version"; exit 1; }

echo "PASS claude plugin metadata"
