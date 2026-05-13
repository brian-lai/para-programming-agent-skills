# PARA-Programming Agent Skills

Cross-client Agent Skills package for the PARA-Programming methodology.

**Research -> Plan -> Review -> Execute -> Review -> Summarize -> Archive**

## What Is This?

PARA-Programming is a structured workflow for AI-assisted development. It keeps plans, research, execution state, reviews, summaries, and archives in a project-local `context/` directory so long-running work can survive context resets and client changes.

This repository packages the methodology as open-standard Agent Skills. The skill layout follows the emerging portable `SKILL.md` convention promoted by agentskills.io: each skill lives in its own directory, the directory basename matches frontmatter `name`, and assets/references stay beside the skill that owns them.

## Supported Clients

| Client | Status | Install path | Invocation |
|--------|--------|--------------|------------|
| OpenAI Codex | Supported out of the box | `scripts/install.sh` installs to `~/.agents/skills` and mirrors to `~/.codex/skills` | `$para-init` or `/skills` |
| Gemini CLI | Supported out of the box | Uses the same `~/.agents/skills` install written by `scripts/install.sh` | Auto-activation or `/skills list` |
| Pi | Supported out of the box | Uses the same `~/.agents/skills` install written by `scripts/install.sh` | Auto-activation or `/skill:para-init` when skill commands are enabled |
| Claude Code | Use the Claude plugin | Use `github.com/brian-lai/para-programming-plugin` | Claude plugin commands |
| OpenCode | Manual/experimental | Copy or symlink `skills/` into the client skills path | Client-specific |
| Cursor | Manual/experimental | Copy or symlink `skills/` into the client skills path | Client-specific |

For Claude Code, use the original PARA-Programming plugin: `https://github.com/brian-lai/para-programming-plugin`. This repository is the open-standard/Codex-oriented Agent Skills package.

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

See [INSTALL.md](INSTALL.md) for client-specific installation paths and support notes.

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
