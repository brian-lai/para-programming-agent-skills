#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PLUGIN_JSON="$REPO_ROOT/.codex-plugin/plugin.json"

name="$(jq -r '.name' "$PLUGIN_JSON")"
skills="$(jq -r '.skills' "$PLUGIN_JSON")"
version="$(jq -r '.version' "$PLUGIN_JSON")"

[ "$name" = "para-programming" ] || { echo "FAIL expected .name para-programming, got $name"; exit 1; }
[ "$skills" = "./skills/" ] || { echo "FAIL expected .skills ./skills/, got $skills"; exit 1; }
[[ "$version" =~ ^3\.[0-9]+\.[0-9]+$ ]] || { echo "FAIL expected semver >= 3.0.0 without prerelease, got $version"; exit 1; }

echo "PASS codex plugin metadata"
