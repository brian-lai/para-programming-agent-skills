# PARA-Programming Agent Skills

Cross-client development workflows and file-based agent memory, packaged as Agent Skills.

**Research -> Plan -> Review -> Execute -> Review -> Summarize -> Archive**

## What Is This?

PARA-Programming combines a structured development workflow with a file-based agent memory system. It preserves plans, decisions, research, progress, and outcomes in readable project-local files. Skills consult that memory to guide execution and resume interrupted work across sessions and clients.

This repository packages the methodology as open-standard Agent Skills. The skill layout follows the emerging portable `SKILL.md` convention promoted by agentskills.io: each skill lives in its own directory, the directory basename matches frontmatter `name`, and assets/references stay beside the skill that owns them.

## How Agent Memory Works

Memory lives in the project's `context/` directory, using Markdown documents and structured progress metadata:

| Location | What it remembers |
|---|---|
| `context/context.md` | Active plan and research references, summary references, todos, blockers, and execution evidence |
| `context/plans/` | Agreed scope, decisions, acceptance criteria, and implementation steps |
| `context/data/` | Research findings and supporting evidence, including uncertainties and freshness notes |
| `context/summaries/` | Changes, outcomes, lessons, and remaining work |
| `context/archives/` | Recoverable snapshots of previous working context |

These records steer work: execution follows the active plan, review checks its requirements, workflow consults recorded evidence before advancing, and status identifies the next action.

Agents read the active index and retrieve supporting files as needed. Summaries retain outcomes and lessons. After verified completion, archival saves the working state and starts fresh context, retaining summary references by default. Detailed history stays available without loading it all into every task.

Resuming after a reset or client change requires the agent to load relevant records and recheck facts that may have changed, such as PR heads and merge status. A summary alone does not establish that work has merged.

See the [context contract](skills/para-init/references/context-schema.md) for fields and recovery rules, and the [methodology](docs/METHODOLOGY.md) for the lifecycle. [resources/AGENTS.md](resources/AGENTS.md) supplies the shared workflow guidance.

## Supported Clients

| Client | Status | Install path |
|--------|--------|--------------|
| OpenAI Codex | Supported out of the box | `scripts/install.sh` installs to `~/.agents/skills` and mirrors to `~/.codex/skills` |
| Gemini CLI | Supported out of the box | Uses the same `~/.agents/skills` install written by `scripts/install.sh` |
| Pi | Supported out of the box | Uses the same `~/.agents/skills` install written by `scripts/install.sh` |
| OpenCode | Supported out of the box | Uses the same `~/.agents/skills` install written by `scripts/install.sh` |
| Cursor | Supported out of the box | Uses the same `~/.agents/skills` install written by `scripts/install.sh` |
| Claude Code | Use the Claude plugin | Use `github.com/brian-lai/para-programming-plugin` |

For Claude Code, use the original PARA-Programming plugin: `https://github.com/brian-lai/para-programming-plugin`. This repository is the open-standard/Codex-oriented Agent Skills package.

### Invocation

The canonical request form is `para-<skill> [arguments]`. Client selectors are presentation syntax; if the client is unknown, name the skill and intent in natural language.

<!-- para-client-invocation-map:start -->
| Client | User-facing form |
|---|---|
| OpenAI Codex | `$para-<skill> [arguments]` |
| Cursor | `/para-<skill> [arguments]` |
| Pi, skill commands enabled | `/skill:para-<skill> [arguments]` |
| Pi, skill commands disabled | `natural-language` — `Use the para-<skill> skill <intent-and-arguments>.` |
| OpenCode | `natural-language` — `Use the para-<skill> skill <intent-and-arguments>.` |
| Gemini CLI | `natural-language` — `Use the para-<skill> skill <intent-and-arguments>.` |
| Unknown client | `natural-language` — `Use the para-<skill> skill <intent-and-arguments>.` |
<!-- para-client-invocation-map:end -->

### Management and discovery

Management commands list, reload, enable, or inspect skills; they are not portable workflow invocations. Use the client-specific skill manager or debug interface to verify discovery.

## Skills

| Skill | Purpose |
|-------|---------|
| `para-init` | Initialize PARA structure in a project |
| `para-research <task>` | Deep codebase research before planning |
| `para-plan <task>` | Create a planning document with self-review |
| `para-review --plan\|--pr` | Review a plan or PR with Staff+ criteria |
| `para-execute` | Create a worktree and execute one checklist item per commit |
| `para-workflow` | Orchestrate simple/phased execution, PR, review, summary, verified merge and archive |
| `para-status` | Check current workflow state |
| `para-summarize` | Generate a post-work summary |
| `para-archive` | Archive context and start fresh |
| `para-check` | Decide whether a request needs the PARA workflow |
| `para-help` | Show quick reference |

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

## Adapted From

These skills were generalized from the original `para-programming-plugin` command set and converted to portable Agent Skills:

- `CLAUDE.md` -> `AGENTS.md`
- `~/.claude/` -> `~/.agents/`
- Client-specific commands -> portable `para-command` skill identifiers
- `commands/*.md` -> `skills/para-*/SKILL.md`

## License

MIT
