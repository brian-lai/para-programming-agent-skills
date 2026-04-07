# Installation Guide

## Prerequisites

- [OpenAI Codex](https://codex.openai.com/) installed and configured
- Git installed

## Installation

### Option 1: Local Plugin Installation

1. **Clone the plugin repository:**

   ```bash
   git clone https://github.com/brian-lai/para-programming-codex-plugin.git ~/.codex/plugins/para-programming
   ```

2. **Register the plugin in your marketplace file:**

   Create or update `~/.agents/plugins/marketplace.json`:

   ```json
   {
     "name": "personal-plugins",
     "interface": {
       "displayName": "Personal Plugins"
     },
     "plugins": [
       {
         "name": "para-programming",
         "source": {
           "source": "local",
           "path": "~/.codex/plugins/para-programming"
         },
         "policy": {
           "installation": "AVAILABLE",
           "authentication": "ON_INSTALL"
         },
         "category": "Productivity"
       }
     ]
   }
   ```

3. **Restart Codex** to load the plugin.

### Option 2: Automated Install Script

```bash
# From the plugin directory:
./scripts/install.sh
```

The script will:
- Create `~/.agents/plugins/` if it doesn't exist
- Add the plugin entry to `~/.agents/plugins/marketplace.json`
- Skip if the entry already exists (idempotent)

**Requires:** `jq` for JSON manipulation. If `jq` is not installed, the script prints manual instructions.

### Option 3: Repo-Level Installation

To make the plugin available for a specific repository:

1. Copy the plugin to `./plugins/para-programming/` in your repo
2. Create `.agents/plugins/marketplace.json` in your repo root:

   ```json
   {
     "name": "repo-plugins",
     "interface": {
       "displayName": "Repository Plugins"
     },
     "plugins": [
       {
         "name": "para-programming",
         "source": {
           "source": "local",
           "path": "./plugins/para-programming"
         },
         "policy": {
           "installation": "INSTALLED_BY_DEFAULT",
           "authentication": "ON_INSTALL"
         },
         "category": "Productivity"
       }
     ]
   }
   ```

3. Restart Codex.

## Post-Installation

After installation, initialize PARA in your project:

```bash
/para-init
```

This creates:
- `context/` directory structure
- `AGENTS.md` project-specific context file
- `~/.agents/AGENTS.md` global methodology (if missing)

## Session Hook (Manual Setup)

Codex does not currently have a built-in hook lifecycle system equivalent to Claude Code's `hooks.json`. If a hook system becomes available in the future, a session start hook can be configured to display PARA status on startup.

For now, run `/para-status` at the beginning of each session to see your current workflow state.

## Uninstallation

1. Remove the plugin entry from `~/.agents/plugins/marketplace.json`
2. Delete the plugin directory: `rm -rf ~/.codex/plugins/para-programming`
3. Restart Codex

## Troubleshooting

### Plugin not loading
- Verify the path in `marketplace.json` points to the correct location
- Ensure the `.codex-plugin/plugin.json` file exists in the plugin directory
- Restart Codex after making changes

### Skills not available
- Check that the `"skills": "./skills/"` path in `plugin.json` is correct
- Verify each skill has a `SKILL.md` file with valid YAML frontmatter
