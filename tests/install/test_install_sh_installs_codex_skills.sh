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

export AGENTS_HOME="$tmp_home/.agents" CODEX_HOME="$tmp_home/.codex"
mkdir -p "$AGENTS_HOME" "$CODEX_HOME"
printf 'custom user guidance\n' > "$AGENTS_HOME/AGENTS.md"
printf 'custom compatibility guidance\n' > "$CODEX_HOME/AGENTS.md"
cp "$AGENTS_HOME/AGENTS.md" "$tmp_home/user-guide"
cp "$CODEX_HOME/AGENTS.md" "$tmp_home/compat-guide"
cp "$REPO_ROOT/resources/AGENTS.md" "$tmp_home/source-guide"

output="$(HOME="$tmp_home" bash "$INSTALL_SOURCE/scripts/install.sh")"

if echo "$output" | grep -Fq 'Use the para-init skill to initialize PARA in a project.' &&
   echo "$output" | grep -Fq 'Use /skills to browse installed skills.'; then
  echo "PASS install output uses portable para-init guidance"
else
  echo "FAIL install output missing portable para-init or /skills management guidance"
  exit 1
fi

for skill in para-init para-plan para-execute para-help; do
  if [ ! -f "$tmp_home/.agents/skills/$skill/SKILL.md" ]; then
    echo "FAIL missing installed user skill $skill"
    exit 1
  fi

  if [ ! -f "$tmp_home/.codex/skills/$skill/SKILL.md" ]; then
    echo "FAIL missing compatibility skill mirror $skill"
    exit 1
  fi
done

if [ ! -f "$tmp_home/.agents/docs/METHODOLOGY.md" ]; then
  echo "FAIL missing installed user methodology docs"
  exit 1
fi

if [ ! -f "$tmp_home/.codex/docs/METHODOLOGY.md" ]; then
  echo "FAIL missing compatibility methodology docs mirror"
  exit 1
fi

if [ ! -f "$tmp_home/.agents/resources/AGENTS.md" ]; then
  echo "FAIL missing installed user para-init resources"
  exit 1
fi

if [ ! -f "$tmp_home/.codex/resources/AGENTS.md" ]; then
  echo "FAIL missing compatibility para-init resources mirror"
  exit 1
fi

if ! jq -e '.plugins[] | select(.name == "para-programming")' "$tmp_home/.agents/plugins/marketplace.json" >/dev/null; then
  echo "FAIL missing marketplace registration"
  exit 1
fi

reinstall_output="$(HOME="$tmp_home" bash "$INSTALL_SOURCE/scripts/install.sh")"
if echo "$reinstall_output" | grep -Fq 'Use the para-init skill to initialize PARA in a project.' &&
   echo "$reinstall_output" | grep -Fq 'Use /skills to browse installed skills.'; then
  echo "PASS idempotent install output preserves portable guidance"
else
  echo "FAIL idempotent install output missing portable guidance"
  exit 1
fi

echo "PASS install script installs Codex skills and support files"

for root in "$AGENTS_HOME" "$CODEX_HOME"; do
  cmp "$root/skills/para-init/../../resources/AGENTS.md" "$tmp_home/source-guide"
  [ ! -e "$root/skills/para-init/resources" ]
done
cmp "$AGENTS_HOME/AGENTS.md" "$tmp_home/user-guide"
cmp "$CODEX_HOME/AGENTS.md" "$tmp_home/compat-guide"
cmp "$REPO_ROOT/resources/AGENTS.md" "$tmp_home/source-guide"
[ ! -e "$REPO_ROOT/skills/para-init/resources" ]
grep -Fq '../../resources/AGENTS.md' "$REPO_ROOT/skills/para-init/SKILL.md"
grep -Fq 'missing optional guidance' "$REPO_ROOT/skills/para-init/SKILL.md"
echo "PASS shared resources resolve without source or global guidance changes"
