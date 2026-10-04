---
name: para-execute
description: Execute the active plan by creating an isolated git worktree and tracking todos. Supports simple and phased plans with TDD-first commit-per-todo discipline.
model: sonnet
effort: medium
---

Implement the active plan in an isolated checkout. Direct execution returns implementation results; use the `para-workflow` skill to prepare a PR and complete the lifecycle.

## Usage

```text
para-execute
para-execute --phase=N
para-execute --no-worktree
```

## Prepare

1. Read the active plan and relevant contract/research from the primary checkout's `context/context.md`. Resolve the context root using Git worktree metadata, not a possibly stale worktree-local copy. Ask only when task/root identity is ambiguous.
2. For phased work, resolve the requested/current phase and verify prerequisite merges are included in the selected base. For simple plans, reject `--phase` rather than inventing phases.
3. Resolve the repository remote and base branch; fetch it and record its starting SHA. Preserve unrelated dirty files. Reuse an existing matching branch/worktree after checking identity; otherwise create `.para-worktrees/{task-name}` on `para/{task-name}` from the resolved base (append `-phase-N` for phases).
4. With `--no-worktree`, create/reuse the execution branch in the current checkout only when switching preserves existing work. Ensure `.para-worktrees/` is ignored before creating a worktree.
5. Extract only Implementation Steps checkboxes as todos. Preserve metadata and record branch/path/base evidence. No active plan: recommend the `para-plan` skill. Missing or ambiguous steps/contracts: resolve the gap before implementing.

See `../para-init/references/context-schema.md` for root resolution, fields and lifecycle evidence.

If ../para-init/references/context-schema.md is not available in this install, preserve existing metadata and record active plan, branch/worktree, base, commit/check evidence and timestamp. Do not infer verified merge or review from missing fields.

## Commit per todo

The checkbox text from the plan IS the commit message: use it verbatim, with formatting cleanup if needed. Each todo is a behavior-sized change including its relevant tests.

1. Reuse the existing contract or plan specification. Create necessary stubs only in the execution checkout; never replace working code with stubs just to satisfy a template.
2. For testable behavior, write the meaningful test and observe its intended failure (RED). Record the command/result; existing passing tests do not establish RED.
3. Implement the change (GREEN), then run required checks and relevant regression coverage. No intentionally failing required suite crosses a commit/merge boundary.
4. Commit the change with the checkbox text after checks pass. Do not create an empty initialization commit.
5. Mark the todo complete only after the commit succeeds; record its SHA and validation in primary context. If a context write failed after commit, inspect history and reconcile rather than committing twice.

For documentation/configuration with no meaningful behavioral test, use structural/manual validation and record that choice. Future acceptance coverage belongs in pending plan work, not a failing required suite. Stop dependent work on failed checks/commit; fix recoverable failures within scope. Reconcile changed context before writing and retain unrelated fields.

Return commits, validation and remaining gaps to the caller. Do not push/create a PR or implicitly invoke review, merge or archive.
