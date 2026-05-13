---
name: para-status
description: Display the current state of PARA context and workflow progress. Detects no-context, idle, planning, executing, and summarized states with next-step guidance.
model: haiku
effort: low
---

Display the current state of PARA context and workflow progress.

## Usage

```
$para-status
$para-status --verbose         # Include file contents preview
$para-status --files           # List all context files
```

## What It Does

1. Reads and parses `context/context.md`
2. Displays current work summary, active plans, and completed summaries
3. Shows worktree status: path, branch, and existence
4. Detects stale and orphaned worktrees
5. Detects workflow state and suggests the next step

See `../para-init/references/context-schema.md` for field meanings.

If ../para-init/references/context-schema.md is not available in this install, the minimal fields needed are: `active_context`, `completed_summaries`, `research_docs`, `worktree_path`, `phased_execution`, and `last_updated`.

## Output Format

```
PARA Status

Current Work:
   Implementing user authentication system

Active Plans:
   context/plans/2025-11-24-user-auth.md

Worktree:
   Path: .para-worktrees/user-auth
   Branch: para/user-auth
   Status: active

Completed Summaries:
   context/summaries/2025-11-23-api-setup-summary.md

Last Updated: 2025-11-24T14:30:00Z

Next Action:
   Continue executing the plan, or run $para-summarize when complete
```

## State Detection

| State | Detection | Next step |
|---|---|---|
| **No context** | `context/context.md` does not exist | Run `$para-init` |
| **Idle** | Context exists, no active plans, no active worktree | Run `$para-plan <task>` or `$para-check` |
| **Planning** | `active_context` contains plan or research docs, no worktree path | Review plan, then run `$para-review --plan` or `$para-execute` |
| **Executing** | `worktree_path` is set and worktree exists | Continue todos, then run `$para-review --pr` and `$para-summarize` |
| **Summarized** | Completed summary exists and no active work remains | Run `$para-archive` |

## Worktree Health Checks

- **Active:** `worktree_path` in metadata, directory exists, branch is valid
- **Stale reference:** `worktree_path` in metadata but directory does not exist -- warn: "Worktree referenced in context.md but directory missing. Run `$para-execute` to recreate or update context.md."
- **Orphaned worktree:** Directory exists in `.para-worktrees/` but is not referenced in `context/context.md` -- warn: "Orphaned worktree found at `.para-worktrees/{name}`. Run `git worktree remove` to clean up or update context.md."
- **No worktree:** No `worktree_path` in metadata -- normal for No context, Idle, Planning, or legacy `--no-worktree` execution

## Implementation

1. Check if `context/context.md` exists
2. Parse JSON metadata from the fenced block
3. Read the human-readable summary section
4. Check worktree state against metadata
5. Check git status for uncommitted changes
6. Determine state and print next-step guidance
