---
name: para-archive
description: Archive completed plans and context, remove verified worktrees, and reset context while preserving summaries and recoverable state.
model: haiku
effort: low
---

Archive completed plans and context, and clean up verified completed work without losing pending tasks or user changes. Final archival is complete only when its receipt and task-worktree removals are verified.

```text
para-archive
para-archive --phase=N
para-archive --fresh
para-archive --seed
```

Read primary context and `../para-init/references/context-schema.md`. Resolve each target worktree/branch and verify its task identity. Required checks, committed/pushed work, verified merge and summary must exist. Unknown remote status or an open PR is unfinished work. Resolve the completed plan set from simple `active_context` execution evidence, or for phased work from `phased_execution.master_plan` and every phase plan belonging to the completed task. Do not archive unrelated active plans.

## Phase cleanup

With `--phase=N`, verify that phase is merged and summarized. Remove only its clean worktree using `git worktree remove`, then verify the exact path is absent from `git worktree list --porcelain` before pruning stale Git metadata. Record the removed path and verification time in that phase's cleanup evidence, then clear its active worktree path. Preserve master/pending plans, other worktrees, phase evidence and unknown fields. Reconcile an already-removed worktree as complete after identity verification. Do not move plans, reset context or perform final archive in this mode; reject --fresh/--seed combined with --phase. A caller must stop before advancing if phase cleanup is blocked or unverifiable.

## Final archive

1. Verify the whole simple/phased task is merged and summarized. An already fresh context with no active task is a no-op only when no archive is pending. Never treat summary presence as merge evidence. Inventory every task worktree from simple execution and all phase execution/cleanup evidence; do not let a missing or cleared `worktree_path` make this inventory vacuously empty.
2. Reserve a unique pair of destinations: `context/archives/YYYY-MM-DD-HHMMSS-context.md` and `context/archives/YYYY-MM-DD-HHMMSS-plans/` (add the same collision suffix to both). Persist `archive_target` and a source-to-destination `archive_plan_targets` manifest, including expected SHA-256 for each completed plan, before copying anything. Preserve each plan's path relative to the project root under the plan directory. On retry, reuse only reservations recorded for this task; accept an existing destination only when its content hash matches the recorded plan. Never overwrite another archive.
3. Copy every task plan to its reserved destination. Verify all hashes and that the master/phase references resolve. Rewrite the archived snapshot's task plan references (`active_context`, `phased_execution.master_plan`, and each relevant `phases[].plan`) to the archived paths and include an `archive_receipt` with status `pending`, the verified merge/summary evidence, plan source/destination/hash entries, and the complete task-worktree inventory. Save and reread the snapshot before removing source plans. On retry, reconcile partial copies from the persisted manifest; preserve sources until all destinations and the snapshot are verified.
4. Remove the completed plan sources only after their archived copies and snapshot references verify. Update the primary context references to the reserved archive paths while cleanup is pending so they remain resolvable. Remove only clean task worktrees, retaining recoverable branches; after each removal verify the exact path is absent from `git worktree list --porcelain` and record the result. Never force-remove a dirty worktree. Preserve dirty/unmerged task work and report it as a blocker; preserve unrelated worktrees and identify them separately. Prune stale metadata only after verified removals.
5. Once every inventoried task worktree is verified absent, update and reread the snapshot with `archive_receipt.status: complete`, the final task-worktree inventory, and completion time. Inventory paths must exactly match the union of simple/phase worktree paths and preserved `execution.cleanup.worktree_path` values; use `removed` or `already_absent` status only after verifying absence. Independently confirm the plan hashes and merge/summary references. Only then create fresh context using `../para-init/assets/context-template.md`, remove completed task plan paths from `active_context`, preserve unrelated active references and completed summary references by default, and clear old execution/workflow/archive reservation fields. `--fresh` omits carryover references; `--seed` also retains still-relevant research. If any operation fails, retain the primary context, reservation manifest and partial receipt for retry; do not claim final archival complete or reset context.
6. Return the snapshot and archived plan paths, removed task worktrees, preserved unrelated/dirty worktrees, receipt status and any blocker. The caller independently verifies the receipt and Git worktree list before reporting workflow completion.

If ../para-init/assets/context-template.md is not available in this install, create fresh context with active_context, completed_summaries and research_docs arrays, null worktree_path and current last_updated. Apply the selected carryover policy.

If ../para-init/references/context-schema.md is not available in this install, preserve unknown state and require observed merge/summary/clean-worktree evidence; never infer completion. Keep archive_target, archive_plan_targets and partial archive_receipt for interrupted archive recovery.

Archives and branches remain available for recovery. Inspect the saved snapshot before restoring context; do not overwrite active work. A removed worktree can be reattached with `git worktree add <path> <existing-branch>` after checking the destination.
