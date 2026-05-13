---
name: para-help
description: Display the PARA-Programming quick-reference guide with all 11 skills and the Research→Plan→Review→Execute→Review→Summarize→Archive workflow.
model: haiku
effort: low
---

Display the PARA-Programming quick-reference guide.

## Usage

```
$para-help
```

## Implementation

Display the following:

---

# PARA-Programming Quick Reference

**Workflow:** Research → Plan → Review → Execute → Review → Summarize → Archive

Detailed workflow: Research → Plan → Review Plan → Execute → Review PR → Summarize → Archive

## When to Use PARA

**Use PARA** if the task results in git changes: features, bug fixes, refactoring, config, migrations, tests, documentation edits, or complex debugging.

**Skip PARA** if the task is read-only or informational: questions, navigation, explanations, or state inspection.

## Skills

| Skill | Purpose |
|-------|---------|
| `$para-init` | Initialize PARA structure in a project |
| `$para-research <task>` | Deep codebase research before planning |
| `$para-plan <task>` | Create a planning document through collaboration |
| `$para-review --plan\|--pr` | Staff+ review loop for plans and PRs |
| `$para-execute` | Create worktree, extract todos, start execution |
| `$para-workflow` | Orchestrate execute → PR → review → summarize → archive |
| `$para-summarize` | Generate post-work summary |
| `$para-archive` | Archive context and start fresh |
| `$para-status` | Check current workflow state |
| `$para-check` | Decide whether a request needs PARA |
| `$para-help` | Show this reference |

## Typical Flow

```
$para-research Add user authentication
$para-plan Add user authentication
$para-review --plan
$para-workflow           # or manually:
  $para-execute          #   -> Creates worktree, implements with TDD
  $para-review --pr      #   -> Staff+ review loop
  $para-summarize        #   -> Generate summary
  $para-archive          #   -> Clean up worktree
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

- Run `$para-status` to see where you are in the workflow
- Run `$para-check` if unsure whether a task needs PARA
- Full methodology details are in `../../docs/METHODOLOGY.md`
