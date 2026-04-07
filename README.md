# PARA-Programming Codex Plugin

Structured AI-assisted development workflow for OpenAI Codex.

**Research → Plan → Review → Execute → Review → Summarize → Archive**

## What is PARA-Programming?

PARA-Programming is a methodology for structured AI-assisted development that emphasizes planning, deliberate execution, and knowledge preservation. This plugin brings the PARA workflow to the OpenAI Codex ecosystem.

## Features

- **Deep Research** — Codebase exploration produces context-compressed research docs for better planning
- **Structured Planning** — Collaborative plan creation with self-review rounds, Staff+ engineering criteria, and phased plan support
- **Staff+ Review** — Independent reviewer with FAANG engineer persona reviews plans and PRs
- **Isolated Execution** — Git worktree isolation keeps your main branch clean while the agent works
- **Commit-Per-Todo** — Every checklist item becomes an atomic commit with TDD (red/green cycle)
- **Workflow Orchestration** — Automatic multi-phase execute → PR → review → summarize → merge cycle
- **Context Tracking** — Persistent `context/context.md` tracks active work, plans, and summaries
- **Phased Execution** — Break complex work into independently reviewable phases

## Skills

| Skill | Purpose |
|-------|---------|
| `/para-init` | Initialize PARA structure in a project |
| `/para-research <task>` | Deep codebase research before planning |
| `/para-plan <task>` | Create a planning document (collaborative, with self-review) |
| `/para-review --plan\|--pr` | Staff+ FAANG engineer review loop |
| `/para-execute` | Create worktree, extract todos, start execution |
| `/para-workflow` | Orchestrate full execute → review → summarize → archive cycle |
| `/para-status` | Check current workflow state |
| `/para-summarize` | Generate post-work summary |
| `/para-archive` | Archive context and start fresh |
| `/para-check` | Decision helper: should I use PARA for this? |
| `/para-help` | Show quick reference |

## Installation

### Option 1: Local Marketplace Entry

1. Copy the plugin to a local directory (e.g., `~/.codex/plugins/para-programming/`)
2. Add the marketplace entry to `~/.agents/plugins/marketplace.json`:

```json
{
  "name": "para-programming-plugins",
  "interface": {
    "displayName": "PARA-Programming Plugins"
  },
  "plugins": [
    {
      "name": "para-programming",
      "source": {
        "source": "local",
        "path": "./plugins/para-programming"
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

3. Restart Codex to load the plugin.

### Option 2: Install Script

```bash
./scripts/install.sh
```

See [INSTALL.md](INSTALL.md) for detailed instructions.

## Quick Start

```bash
# Initialize PARA in your project
/para-init

# Research the codebase (optional but recommended)
/para-research add user authentication

# Create a plan for your task
/para-plan add user authentication

# Review the plan
/para-review --plan

# Execute (or use /para-workflow for full automation)
/para-execute

# Review the implementation
/para-review --pr

# Summarize and archive
/para-summarize
/para-archive
```

## File Structure (Per Project)

```
context/
├── context.md       # Active session context
├── plans/           # YYYY-MM-DD-task-name.md
├── summaries/       # YYYY-MM-DD-task-name-summary.md
├── archives/        # YYYY-MM-DD-context.md
├── data/            # Input/output files, specs
└── servers/         # MCP tool wrappers
```

## Adapted From

This plugin is a Codex adaptation of the [PARA-Programming Plugin for Claude Code](https://github.com/brian-lai/para-programming-plugin). Key adaptations:

- `CLAUDE.md` → `AGENTS.md`
- `~/.claude/` → `~/.agents/`
- `/para:command` → `/para-command` (hyphenated for Codex compatibility)
- `commands/*.md` → `skills/*/SKILL.md` (Codex skill format)

## License

MIT
