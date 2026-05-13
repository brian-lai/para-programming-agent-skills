# PARA-Programming Agent Skills

Cross-client Agent Skills package for the PARA-Programming methodology.

**Research -> Plan -> Review -> Execute -> Review -> Summarize -> Archive**

## What Is This?

PARA-Programming is a structured workflow for AI-assisted development. It keeps plans, research, execution state, reviews, summaries, and archives in a project-local `context/` directory so long-running work can survive context resets and client changes.

This repository packages the methodology as open-standard Agent Skills for Claude Code, OpenAI Codex, OpenCode, Cursor, and Gemini CLI. The skill layout follows the emerging portable `SKILL.md` convention promoted by agentskills.io: each skill lives in its own directory, the directory basename matches frontmatter `name`, and assets/references stay beside the skill that owns them.

## Skills

| Skill | Purpose |
|-------|---------|
| `$para-init` | Initialize PARA structure in a project |
| `$para-research <task>` | Deep codebase research before planning |
| `$para-plan <task>` | Create a planning document with self-review |
| `$para-review --plan\|--pr` | Review a plan or PR with Staff+ criteria |
| `$para-execute` | Create a worktree and execute one checklist item per commit |
| `$para-workflow` | Orchestrate execute, review, summarize, and merge across phases |
| `$para-status` | Check current workflow state |
| `$para-summarize` | Generate a post-work summary |
| `$para-archive` | Archive context and start fresh |
| `$para-check` | Decide whether a request needs the PARA workflow |
| `$para-help` | Show quick reference |

## Installation

See [INSTALL.md](INSTALL.md) for client-specific installation paths:

- Claude Code
- OpenAI Codex
- OpenCode
- Cursor
- Gemini

For Codex local skill installation from a checkout:

```bash
./scripts/install.sh
```

The installer follows the current Codex Skills guide by installing user skills into `~/.agents/skills`. It also mirrors into `~/.codex/skills` for older local runtimes.

Preview the install without writes:

```bash
./scripts/install.sh --dry-run
```

## Project Context

The workflow creates project-local context files:

```text
context/
├── context.md
├── plans/
├── summaries/
├── archives/
├── data/
└── servers/
```

`resources/AGENTS.md` contains the global PARA workflow methodology template. `docs/METHODOLOGY.md` explains the rationale and lifecycle in detail.

## Adapted From

These skills were generalized from the original `para-programming-plugin` command set and converted to portable Agent Skills:

- `CLAUDE.md` -> `AGENTS.md`
- `~/.claude/` -> `~/.agents/`
- `/para:command` -> `$para-command` skill mention
- `commands/*.md` -> `skills/para-*/SKILL.md`

## License

MIT
