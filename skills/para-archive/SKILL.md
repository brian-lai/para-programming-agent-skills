---
name: para-archive
description: Archive the current context to create a clean slate for the next task. Removes worktrees, resets context/context.md, preserves summaries.
model: haiku
effort: low
---

Clean up verified completed work without losing pending tasks or user changes.

```text
para-archive
para-archive --phase=N
para-archive --fresh
para-archive --seed
```

Read primary context and `../para-init/references/context-schema.md`. Resolve each target worktree/branch and verify its task identity. Required checks, committed/pushed work, verified merge and summary must exist. Unknown remote status or an open PR is unfinished work.

## Phase cleanup

With `--phase=N`, verify that phase is merged and summarized. Remove only its clean worktree using `git worktree remove`, then prune stale Git metadata. Preserve master/pending plans, other worktrees, phase evidence and unknown fields. Clear only the removed phase's active worktree path. Reconcile an already-removed worktree as complete after identity verification. Do not reset context or perform final archive in this mode; reject --fresh/--seed combined with --phase.

## Final archive

1. Verify the whole simple/phased task is merged and summarized. An already fresh context with no active task is a no-op. Never treat summary presence as merge evidence.
2. Check recorded worktrees for user changes; do NOT force-remove. Preserve dirty work and report the blocker. Remove only verified task worktrees, retaining recoverable branches; prune afterward.
3. Reserve an unused `context/archives/YYYY-MM-DD-HHMMSS-context.md` (add a suffix on collision) in archive_target. Save a snapshot before resetting context. On retry, reuse the recorded destination only after verifying it belongs to this task; never overwrite another archive.
4. Create fresh context using `../para-init/assets/context-template.md`. Preserve completed summary references by default. `--fresh` omits carryover references; `--seed` also retains still-relevant research. Remove old execution/workflow/archive_target fields from fresh context.
5. Report archived path, removed worktrees, carried references and any remaining blocker. The caller controls subsequent work.

If ../para-init/assets/context-template.md is not available in this install, create fresh context with active_context, completed_summaries and research_docs arrays, null worktree_path and current last_updated. Apply the selected carryover policy.

If ../para-init/references/context-schema.md is not available in this install, preserve unknown state and require observed merge/summary/clean-worktree evidence; never infer completion. Keep archive_target for interrupted archive recovery.

Archives and branches remain available for recovery. Inspect the saved snapshot before restoring context; do not overwrite active work. A removed worktree can be reattached with `git worktree add <path> <existing-branch>` after checking the destination.
