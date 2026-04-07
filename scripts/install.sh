#!/bin/bash
#
# PARA-Programming Codex Plugin - Marketplace Registration Helper
#
# Adds the plugin entry to ~/.agents/plugins/marketplace.json
# Requires: jq (for JSON manipulation)
# Idempotent: skips if entry already exists
#

set -e

PLUGIN_NAME="para-programming"
MARKETPLACE_DIR="$HOME/.agents/plugins"
MARKETPLACE_FILE="$MARKETPLACE_DIR/marketplace.json"
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "PARA-Programming Codex Plugin - Install"
echo "========================================"
echo ""

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
    echo "No changes made."
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
echo "Done! Plugin registered at: $MARKETPLACE_FILE"
echo "Plugin source: $PLUGIN_DIR"
echo ""
echo "Restart Codex to load the plugin, then run:"
echo "  /para-init"
