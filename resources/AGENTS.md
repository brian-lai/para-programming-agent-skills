# Global PARA Workflow Guide

Project-specific conventions belong in the project's AGENTS.md. Skill requests below are natural-language instructions, not shell commands.

## Scope

All tracked implementation changes, including documentation/configuration fixes, go through plan → execution branch/worktree → PR → review → merge. Never commit directly to main. Respect explicit user instructions and existing authorization; do not infer a bypass from “quick fix.”

Read-only questions can be answered directly. Research, plans and progress files under context/ are workflow artifacts; creating them does not recursively require another implementation plan.

## Context

Primary checkout `context/context.md` records active plans, research, summary paths, todos and verified execution evidence. Preserve unrelated/unknown metadata. Source edits/tests/commits happen in the execution checkout. Resolve roots from Git worktree metadata, not a stale local context copy.

Use dated files in context/data, context/plans, context/summaries and context/archives. Keep decision-relevant evidence active; retrieve supporting files when needed. Handoffs must work without planner conversation; preserve settled decisions, validation and material prerequisites. Initialization preserves existing context and guidance.

## Lifecycle

Use `para-research` when needed, then `para-plan` and independent `para-review --plan` before execution. Use `para-workflow` for simple or phased work. It owns execute → PR → current-head review → summary → authorized guarded merge → archive. Commit validated todos; verify the remote merge. After each phase merge and summary, clean and verify that phase before advancing. After all task merges and summaries, archive all completed plans plus context and verify the receipt, hashes, fresh references and removed task worktrees. Dirty, unmerged or unverifiable work blocks completion. The `para-init` simple-plan-binding reference defines simple plan selection and receipt identity.

Direct skills perform only their named operation. Auto mode carries the user's authorization through workflow transitions without skipping review or required checks.

## Recovery

Before retrying, reconcile Git/GitHub state; a changed head needs fresh eligibility and a queued merge remains pending. Preserve dirty/unmerged work, unrelated context and recoverable branches. Never force-remove a dirty worktree or overwrite an archive. Missing evidence is unknown and cannot authorize cleanup or completion.

The installed para-init skill's references/context-schema.md is the canonical field and transition contract. Missing evidence is unknown; it cannot authorize a destructive cleanup or falsely complete work.
