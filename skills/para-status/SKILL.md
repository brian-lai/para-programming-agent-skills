---
name: para-status
description: Display the current state of PARA context and workflow progress. Detects no-context, idle, planning, executing, and summarized states with next-step guidance.
model: haiku
effort: low
---

Report workflow state and the next step without modifying files or removing worktrees.

```text
para-status
para-status --verbose
para-status --files
```

Resolve the primary context root using Git worktree metadata. Read its summary/JSON and reconcile branch, worktree and recorded PR evidence. Use `../para-init/references/context-schema.md` for field meanings.

If ../para-init/references/context-schema.md is not available in this install, inspect active_context, research_docs, completed_summaries, execution_branch, worktree_path and phased_execution. Preserve unknowns in the report rather than guessing completion.

## State Detection

Use the first applicable row; summary presence never overrides unfinished work.

| State | Evidence | Next step |
|---|---|---|
| No context | Primary context is absent | Use the `para-init` skill |
| Unresolved | Malformed metadata or ambiguous task/root | Report exact gap and recovery choice |
| Executing | Active unmerged task, including branch-only or per-phase execution; known workflow step pending | Resume with the `para-workflow` skill from verified evidence |
| Summarized | All work verified merged and summarized, cleanup remains | Use the `para-archive` skill |
| Planning | Unexecuted active plan exists | Review plan, then use the `para-workflow` skill |
| Research | research_docs exists without active work | Use the `para-plan` skill with relevant research |
| Idle | No active work or applicable research | Use the `para-check` skill or the `para-plan` skill |

Report current task/phase, plan, branch/worktree, PR/check/review/merge evidence when available, latest update and next action. `--verbose` adds relevant previews; `--files` lists context artifacts without loading their entire contents.

## Worktree health

- **Stale reference:** metadata points to a missing directory. Reconcile Git worktree registry and branch before suggesting recreation.
- **Orphaned worktree:** registered/disk worktree is not referenced by this task. Report it; do not remove unrelated work.
- A null worktree is valid for branch-only execution. Inspect phase entries as well as top-level metadata.
- If remote evidence is unavailable, distinguish recorded state from fresh verification. Do not call unverified work complete.
