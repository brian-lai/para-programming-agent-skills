---
name: para-help
description: Display the PARA-Programming quick-reference guide with all 11 skills and the Research→Plan→Review→Execute→Review→Summarize→Archive workflow.
model: haiku
effort: low
---

Display the PARA-Programming quick-reference guide.

## Usage

```
para-help
```

## Implementation

Determine how to render user-facing skill requests before displaying the reference:

1. Render a client selector only when the host is explicit in runtime/system context or the user names the client.
2. Do not infer the host from ~/.agents/skills or another shared discovery path.
3. For an unknown client, OpenCode, or Gemini CLI, use exact-name natural language such as: Use the `para-plan` skill to plan `<task>`.
4. Treat the forms below as presentation only. The canonical request remains `para-<skill> [arguments]`.
5. Preserve the exact `para-*` identifier on every line. Do not replace identifiers with generic labels such as “the plan review skill”.

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

Display the reference below. Keep the skill identifiers canonical. In the Typical Flow, render each request using the selected client form; when using natural language, include both the exact skill name and its intent/arguments.

For natural-language clients, render the Typical Flow with this exact request sequence:

```text
Use the `para-research` skill to research "Add user authentication".
Use the `para-plan` skill to plan "Add user authentication".
Use the `para-review` skill with `--plan`.
Use the `para-workflow` skill to complete the reviewed simple or phased plan.
```

---

# PARA-Programming Quick Reference

**Workflow:** Research → Plan → Review → Execute → Review → Summarize → Archive

Detailed lifecycle: Research → Plan → Review Plan → Execute → Prepare PR → Review PR → Summarize → Merge → Cleanup → Archive

## When to Use PARA

**Use PARA** if the task results in git changes: features, bug fixes, refactoring, config, migrations, tests, documentation edits, or complex debugging.

**Skip PARA** if the task is read-only or informational: questions, navigation, explanations, or state inspection.

## Skills

| Skill | Purpose |
|-------|---------|
| `para-init` | Initialize PARA structure in a project |
| `para-research <task>` | Deep codebase research before planning |
| `para-plan <task>` | Create a planning document through collaboration |
| `para-review --plan\|--pr` | Independent evidence-based plan/PR review |
| `para-execute` | Create worktree, extract todos, start execution |
| `para-workflow` | Orchestrate execute → PR → review → summarize → merge → archive |
| `para-summarize` | Generate post-work summary |
| `para-archive` | Archive context and start fresh |
| `para-status` | Check current workflow state |
| `para-check` | Decide whether a request needs PARA |
| `para-help` | Show this reference |

## Typical Flow

```
para-research Add user authentication
para-plan Add user authentication
para-review --plan
para-workflow           # simple or phased plan; use --auto for authorized continuation
```

## File Structure

```
context/
├── context.md       # Active session context
├── plans/           # YYYY-MM-DD-task-name.md
├── summaries/       # YYYY-MM-DD-task-name-summary.md
├── archives/        # YYYY-MM-DD-context.md
├── data/            # Input/output files, research docs
└── servers/         # MCP tool wrappers
```

## Tips

- Use the `para-status` skill to see where you are in the workflow
- Use the `para-check` skill if unsure whether a task needs PARA
- Optional human reference: `../../docs/METHODOLOGY.md`; load only when the user asks about the methodology

Direct skills perform their named operation only. Use the `para-workflow` skill to sequence the complete lifecycle, including PR preparation and verified merge.
