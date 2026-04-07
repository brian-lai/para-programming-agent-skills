# PARA-Programming Codex Plugin

This document contains project-specific context only.

## CRITICAL (MUST FOLLOW RULES)
**Workflow Methodology:** Follow the global workflow guide at `~/.agents/AGENTS.md`

**Never commit directly to main.** All code changes — including small fixes, version bumps, and one-liners — must go through the full PARA workflow: plan → worktree branch → PR → review → merge. There is no such thing as "too small for a PR."

## About This Project

The PARA-Programming Codex Plugin is the OpenAI Codex adaptation of the PARA-Programming methodology for structured AI-assisted development workflows. It provides skills for managing planning documents, execution tracking, summaries, and context archival.

## Tech Stack

- **Runtime:** Codex plugin system
- **Format:** SKILL.md files with YAML frontmatter
- **Documentation:** Markdown

## Structure

```
para-programming-codex-plugin/
├── .codex-plugin/      # Plugin manifest
├── skills/             # Skill implementations (SKILL.md)
├── templates/          # File templates for plans, summaries, etc.
├── resources/          # Global AGENTS.md methodology file
├── examples/           # Marketplace entry example
├── hooks/              # Session hooks (if supported)
├── docs/               # Additional documentation
└── scripts/            # Installation helpers
```

## Key Files

- `.codex-plugin/plugin.json`: Plugin manifest with metadata and skill path
- `resources/AGENTS.md`: Global workflow methodology template
- `skills/*/SKILL.md`: Individual skill implementations

## Conventions

- All context files use `YYYY-MM-DD-` date prefixes for chronological sorting
- Skills follow `/para-<name>` hyphenated naming pattern
- Markdown is used for all documentation and context files
- AGENTS.md used instead of CLAUDE.md (Codex-native convention)

## Getting Started

```bash
# Install via marketplace entry
# Copy examples/marketplace-entry.json to ~/.agents/plugins/marketplace.json
# Restart Codex

# Initialize PARA structure in a project:
/para-init

# Create a plan:
/para-plan <task-description>

# Check workflow status:
/para-status
```
