#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
tmp_home="$(mktemp -d)"
trap 'rm -rf "$tmp_home"' EXIT

# Exercise the current payload from a disposable primary checkout, never a live install.
INSTALL_SOURCE="$tmp_home/source"
mkdir -p "$INSTALL_SOURCE"
cp -R "$REPO_ROOT/skills" "$REPO_ROOT/docs" "$REPO_ROOT/resources" "$REPO_ROOT/scripts" "$INSTALL_SOURCE/"
git init -q "$INSTALL_SOURCE"

AGENTS_HOME="$tmp_home/.agents" CODEX_HOME="$tmp_home/.codex" HOME="$tmp_home" bash "$INSTALL_SOURCE/scripts/install.sh" --dry-run >/dev/null

if [ -e "$tmp_home/.agents" ]; then
  echo "FAIL dry-run wrote to HOME"
  exit 1
fi

if [ -e "$tmp_home/.codex" ]; then
  echo "FAIL dry-run wrote to CODEX_HOME"
  exit 1
fi

echo "PASS install dry-run made no HOME writes"
