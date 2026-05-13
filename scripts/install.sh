#!/bin/bash
#
# PARA-Programming Codex Plugin - Install Helper
#
# Installs skills into ~/.codex/skills and adds the plugin entry to
# ~/.agents/plugins/marketplace.json.
# Requires: jq (for marketplace JSON manipulation)
# Idempotent: refreshes direct skill files and skips marketplace registration
# when the entry already exists.
#

set -e

PLUGIN_NAME="para-programming"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CODEX_SKILLS_DIR="$CODEX_HOME/skills"
CODEX_DOCS_DIR="$CODEX_HOME/docs"
CODEX_PARA_INIT_RESOURCES_DIR="$CODEX_SKILLS_DIR/para-init/resources"
MARKETPLACE_DIR="$HOME/.agents/plugins"
MARKETPLACE_FILE="$MARKETPLACE_DIR/marketplace.json"
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRY_RUN=0

for arg in "$@"; do
    case "$arg" in
        --dry-run)
            DRY_RUN=1
            ;;
        -h|--help)
            echo "Usage: $0 [--dry-run]"
            exit 0
            ;;
        *)
            echo "Error: unknown argument: $arg"
            echo "Usage: $0 [--dry-run]"
            exit 1
            ;;
    esac
done

echo "PARA-Programming Codex Plugin - Install"
echo "========================================"
echo ""

if [ "$DRY_RUN" -eq 1 ]; then
    echo "Dry run: would install skills into $CODEX_SKILLS_DIR"
    echo "Dry run: would install methodology docs into $CODEX_DOCS_DIR"
    echo "Dry run: would install para-init resources into $CODEX_PARA_INIT_RESOURCES_DIR"
    echo "Dry run: would register '$PLUGIN_NAME' in $MARKETPLACE_FILE"
    echo "Dry run: plugin source would be $PLUGIN_DIR"
    echo "Dry run: no filesystem changes made"
    exit 0
fi

echo "Installing PARA skills into $CODEX_SKILLS_DIR..."
mkdir -p "$CODEX_SKILLS_DIR"
cp -R "$PLUGIN_DIR/skills/." "$CODEX_SKILLS_DIR/"

echo "Installing methodology docs into $CODEX_DOCS_DIR..."
mkdir -p "$CODEX_DOCS_DIR"
cp -R "$PLUGIN_DIR/docs/." "$CODEX_DOCS_DIR/"

echo "Installing para-init resources into $CODEX_PARA_INIT_RESOURCES_DIR..."
mkdir -p "$CODEX_PARA_INIT_RESOURCES_DIR"
cp "$PLUGIN_DIR/resources/AGENTS.md" "$CODEX_PARA_INIT_RESOURCES_DIR/AGENTS.md"

# Check for jq
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed."
    echo ""
    echo "Install jq:"
    echo "  macOS:  brew install jq"
    echo "  Ubuntu: sudo apt-get install jq"
    echo "  Other:  https://jqlang.github.io/jq/download/"
    echo ""
    echo "Or manually add this entry to $MARKETPLACE_FILE:"
    echo ""
    echo '  {
    "name": "para-programming",
    "source": {
      "source": "local",
      "path": "'"$PLUGIN_DIR"'"
    },
    "policy": {
      "installation": "AVAILABLE",
      "authentication": "ON_INSTALL"
    },
    "category": "Productivity"
  }'
    exit 1
fi

# Create directory if missing
if [ ! -d "$MARKETPLACE_DIR" ]; then
    echo "Creating $MARKETPLACE_DIR..."
    mkdir -p "$MARKETPLACE_DIR"
fi

# Create marketplace.json if missing
if [ ! -f "$MARKETPLACE_FILE" ]; then
    echo "Creating $MARKETPLACE_FILE..."
    cat > "$MARKETPLACE_FILE" <<JSONEOF
{
  "name": "personal-plugins",
  "interface": {
    "displayName": "Personal Plugins"
  },
  "plugins": []
}
JSONEOF
fi

# Check if entry already exists
if jq -e ".plugins[] | select(.name == \"$PLUGIN_NAME\")" "$MARKETPLACE_FILE" > /dev/null 2>&1; then
    echo "Plugin '$PLUGIN_NAME' is already registered in $MARKETPLACE_FILE"
    echo "Direct Codex skills were refreshed."
    exit 0
fi

# Add plugin entry
echo "Adding '$PLUGIN_NAME' to $MARKETPLACE_FILE..."
TEMP_FILE=$(mktemp)
trap 'rm -f "$TEMP_FILE"' EXIT
jq --arg name "$PLUGIN_NAME" \
   --arg path "$PLUGIN_DIR" \
   '.plugins += [{
     "name": $name,
     "source": {
       "source": "local",
       "path": $path
     },
     "policy": {
       "installation": "AVAILABLE",
       "authentication": "ON_INSTALL"
     },
     "category": "Productivity"
   }]' "$MARKETPLACE_FILE" > "$TEMP_FILE" && mv "$TEMP_FILE" "$MARKETPLACE_FILE"

echo ""
echo "Done! PARA skills installed at: $CODEX_SKILLS_DIR"
echo "Plugin registered at: $MARKETPLACE_FILE"
echo "Plugin source: $PLUGIN_DIR"
echo ""
echo "Restart Codex to load the plugin, then run:"
echo "  /para-init"
