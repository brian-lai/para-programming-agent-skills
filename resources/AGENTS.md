# Global PARA Workflow Guide

Project-specific conventions belong in the project's AGENTS.md. Skill requests below are natural-language instructions, not shell commands.

## Scope

All tracked implementation changes, including documentation/configuration fixes, go through plan → execution branch/worktree → PR → review → merge. Never commit directly to main. Respect explicit user instructions and existing authorization; do not infer a bypass from “quick fix.”

Read-only questions can be answered directly. Research, plans and progress files under context/ are workflow artifacts; creating them does not recursively require another implementation plan.

## Context

Primary checkout `context/context.md` records active plans, research, summary paths, todos and verified execution evidence. Preserve unrelated/unknown metadata. Source edits/tests/commits happen in the execution checkout. Resolve roots from Git worktree metadata, not a stale local context copy.

Use dated files in context/data, context/plans, context/summaries and context/archives. Keep only decision-relevant evidence active; retrieve supporting files when needed. Initialization preserves existing context and guidance.

## Lifecycle

Use the `para-research` skill when exploration is needed, then the `para-plan` skill to capture scope, contracts and validation. Use the `para-review` skill with `--plan` for independent review.

Use the `para-workflow` skill for either a simple or phased plan:

1. Execute behavior-sized todos in the identified execution checkout. Reuse existing contracts; create necessary stubs there. Observe meaningful failures before implementation when applicable, pass required checks, commit, then record completion and SHA.
2. Prepare/reuse the matching PR after pushing the execution branch.
3. Review requirements, diff and check evidence; bind the result to the reviewed head. An explicit override is distinct from independent approval.
4. Summarize actual committed changes and observed validation. A summary does not establish merge.
5. Verify authorization, current-head review eligibility and required checks; issue a guarded merge and confirm the remote result.
6. After each phase merge and summary, invoke `para-archive --phase=N` and verify its recorded worktree is absent before advancing; retain pending plans and unrelated work. Start dependent phases from a base containing predecessor merges. After all task merges/summaries, invoke final `para-archive` in the same workflow run. It must move completed plan files to the reserved archive location, save a recoverable context snapshot and remove every clean task worktree. Independently verify the task-bound archive receipt, archived plan hashes, fresh active references and Git worktree list before reporting completion. Dirty/unmerged task work or unverifiable cleanup leaves the workflow incomplete and recoverable.

Direct skills perform only their named operation. Workflow owns sequencing, PR preparation, retries and advancement. Auto mode carries the user's authorization through these transitions while retaining gates.

## Recovery

Before retrying an effect, reconcile actual Git/GitHub results. A changed head invalidates transferable approval; queued merge is pending. Never force-remove a dirty worktree, overwrite another archive, or replace unrelated context. Preserve recoverable branches, persist the plan archive mapping before moving files, and retain partial archive evidence until cleanup is verified.

The installed para-init skill's references/context-schema.md is the canonical field and transition contract. Missing evidence is unknown; it cannot authorize a destructive cleanup or falsely complete work.
