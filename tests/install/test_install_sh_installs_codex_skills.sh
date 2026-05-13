#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
tmp_home="$(mktemp -d)"
trap 'rm -rf "$tmp_home"' EXIT

HOME="$tmp_home" bash "$REPO_ROOT/scripts/install.sh" >/dev/null

for skill in para-init para-plan para-execute para-help; do
  if [ ! -f "$tmp_home/.codex/skills/$skill/SKILL.md" ]; then
    echo "FAIL missing installed skill $skill"
    exit 1
  fi
done

if [ ! -f "$tmp_home/.codex/docs/METHODOLOGY.md" ]; then
  echo "FAIL missing installed methodology docs"
  exit 1
fi

if [ ! -f "$tmp_home/.codex/skills/para-init/resources/AGENTS.md" ]; then
  echo "FAIL missing installed para-init resources"
  exit 1
fi

if ! jq -e '.plugins[] | select(.name == "para-programming")' "$tmp_home/.agents/plugins/marketplace.json" >/dev/null; then
  echo "FAIL missing marketplace registration"
  exit 1
fi

echo "PASS install script installs Codex skills and support files"
