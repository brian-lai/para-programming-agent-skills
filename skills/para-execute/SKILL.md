---
name: para-execute
description: Execute the active plan by creating an isolated git worktree and tracking todos. Supports simple and phased plans with TDD-first commit-per-todo discipline.
model: sonnet
effort: medium
---

Execute the active plan by creating an isolated git worktree and tracking todos. Supports both simple and phased plans.

## Usage

```
/para-execute                    # Auto-detect plan; prompts for phase if phased
/para-execute --phase=N          # Execute specific phase
/para-execute --no-worktree      # Skip worktree creation; fall back to git checkout -b
```

## What It Does

1. Read the active plan from `context/context.md`
2. Detect simple vs phased plan based on context metadata
3. For phased plans, determine which phase to execute, prompt if not specified, and verify previous phases are completed
4. Fetch latest and create an isolated git worktree: `git fetch origin main && git worktree add .para-worktrees/{task-name} -b para/{task-name} origin/main` (or `para/{task-name}-phase-N`)
5. Extract checkbox items (`- [ ] ...`) from the plan's Implementation Steps section as todos. The checkbox text becomes both the todo item and the eventual commit message.
6. Update `context/context.md` with the todo list and worktree path. This file lives in the main working tree.
7. Make an empty initial commit in the worktree: `git -C .para-worktrees/{task-name} commit --allow-empty -m "chore: Initialize execution context for {task-name}"`
8. Execute each todo using the Commit-Per-Todo Rule below.

### `--no-worktree` Escape Hatch

When `--no-worktree` is specified, fall back to branch-based behavior: `git checkout -b para/{task-name}`. This still creates a branch, but it switches the current working directory to that branch instead of creating a separate worktree. Use this only for single-developer workflows where keeping the main working tree on its current branch is not important.

## Prerequisites

- `context/context.md` must exist with an active plan
- If no active plan, error: "No active plan found. Run `/para-plan` first."
- If dirty git state, warn user and offer to continue or stash first
- Check `.gitignore` for `.para-worktrees/`; if missing, warn and suggest running `/para-init`
- If target worktree directory already exists, ask whether to continue in it, remove and recreate, or cancel
- If target branch already exists but no worktree, use `git worktree add .para-worktrees/{task-name} para/{task-name}` without `-b`

## Context Update

Replace `context/context.md` with execution tracking content:

- Current work summary with branch, worktree, and plan path
- To-do list extracted from plan checkboxes
- Progress notes
- JSON metadata with `active_context`, `completed_summaries`, `execution_branch`, `worktree_path`, `execution_started`, and `last_updated`

For phased plans, add phased execution metadata with phase statuses and `current_phase: N`. The branch becomes `para/{task-name}-phase-N`, the worktree becomes `.para-worktrees/{task-name}-phase-N`, and both master and phase plans are listed in `active_context`.

See `../para-init/references/context-schema.md` for the full field reference.

If ../para-init/references/context-schema.md is not available in this install, the minimal fields needed are: `active_context` (string[]), `completed_summaries` (string[]), `execution_branch` (string), `worktree_path` (string), `execution_started` (ISO 8601 string), and `last_updated` (ISO 8601 string). Phased plans also need a phase list with `phase`, `plan`, `status`, `branch`, and `worktree_path`.

## Commit-Per-Todo Rule (Spec-Driven TDD)

**Committing after each todo is mandatory. The checkbox text from the plan IS the commit message -- use it verbatim (or lightly cleaned up for git conventions). Each todo follows a spec-first, tests-first cycle.**

Before starting any todo, verify that the active plan references a spec file (`context/data/*-spec.yaml` or equivalent contract). If missing, prompt the user to create the spec before proceeding.

The agent works inside the worktree directory (`.para-worktrees/{task-name}/`). All file edits, test runs, and git operations happen within this directory, keeping the main working tree untouched.

> **Design note -- context/context.md lives in main tree:** `context/context.md` is intentionally kept in the main working tree, not the worktree, so it remains accessible regardless of which worktree is active. All PARA commands read from and write to the main working tree's `context/` directory. This is why the initial commit on each branch is an empty commit: there are no worktree-local files to commit at that point.

For each todo:

1. **Confirm spec + stubs exist** -- locate the stub source file(s) for this step. If stubs are missing, create them from the spec before writing tests.
2. **Write tests first (RED)** -- based on the plan's `Tests:` annotation and the spec. Tests import the stub and assert expected behavior.
3. **Implement (GREEN)** -- replace stub bodies with real logic to make the tests pass.
4. **Verify the full suite** -- run the relevant full test suite to confirm there are no regressions.
5. **Mark complete** -- mark the todo `[x]` in `context/context.md` in the main working tree.
6. **Stage and commit** -- stage changes in the worktree, then commit with the checklist item text as the commit message.

The final step must commit with the checklist item text as the commit message.

If a todo has no meaningful automated tests, such as config, documentation, or template updates, note this in the commit and skip the RED/GREEN steps.

When all todos are complete, suggest running `/para-review --pr` for independent Staff+ review before merging. Then run `/para-summarize`.

## Edge Cases

- **No implementation steps in plan:** Prompt user to provide todos manually.
- **Multiple active plans:** Ask user which one to execute.
- **Worktree directory already exists:** Ask whether to continue in the existing worktree, remove and recreate, or cancel.
- **Branch exists but no worktree:** Use `git worktree add` without `-b` to attach to the existing branch.
- **Stale worktree:** Warn user, offer to recreate or clean up metadata.
- **`.para-worktrees/` not in .gitignore:** Warn and suggest running `/para-init`.
- **If a todo is too large:** Break it into smaller sub-items before implementing.
- **User runs command from inside worktree:** Detect missing `context/context.md` relative to cwd and warn that commands should be run from the main working tree.

## Notes

- Worktree isolation keeps the main working tree on its current branch while the agent works in `.para-worktrees/`
- Branch naming follows `para/{task-name}` for easy identification
- For phased plans, each phase branches from `main` after previous phases are merged
- Run `/para-status` anytime to see current progress and worktree state
