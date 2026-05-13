---
name: para-workflow
description: Orchestrate the full PARA execution cycle across phases with automatic execute, PR creation, review, summarize, merge, and archive. Designed for multi-phase plans.
model: sonnet
effort: medium
---

Orchestrate the full PARA execution cycle across phases: execute -> PR -> review -> summarize -> archive -> next phase. Supports manual mode and autonomous (`--auto`) mode.

## Usage

```
$para-workflow                     # Run workflow for active plan, pausing at phase boundaries
$para-workflow --auto              # Fully autonomous, no pause between phases
$para-workflow --phase=N           # Start from a specific phase
$para-workflow --skip-review       # Skip Staff+ review loops
```

## Prerequisites

- `context/context.md` must exist with an active phased plan
- For simple non-phased plans, use `$para-execute` directly
- Git repository must be clean, or the user must confirm proceeding with dirty state

## Process Per Phase

For each phase in the plan, the workflow runs these steps in order:

### Step 1: Execute

Run `$para-execute --phase=N`.

- Creates a worktree and branch for the phase
- Extracts checklist items as todos
- Implements each todo following the TDD cycle (RED -> GREEN -> commit)
- Each checklist item text becomes the commit message

### Step 2: Create PR

Create a pull request for the phase branch. This step owns PR creation for workflow runs. `$para-summarize` in Step 4 detects that it is running inside the orchestrator and skips its standalone push/PR guidance.

- **PR title:** `para/{task-name} phase N: {phase title}`
- **PR body:** generated from:
  - Phase objective from sub-plan
  - Commit list with descriptions
  - Checklist of implementation steps, checked off
  - Link to plan file

### Step 3: Review

Run `$para-review --pr` unless `--skip-review` is specified.

- Staff+ reviewer reviews the PR
- Loop until approved or user override
- Respect the `$para-review` 5-round cap and convergence rules
- Apply fixes, create additional commits as needed, and push fixes to the PR branch

### Step 4: Summarize

Run `$para-summarize --phase=N`.

- Generate phase summary to `context/summaries/`
- Record what changed, rationale, key learnings, and tests
- Mark phase as completed in `context/context.md`
- Do not create a second PR; Step 2 already owns that

### Step 5: Merge

Merge the PR.

- **Default mode:** Pause and ask user "Ready to merge Phase N PR? (Y/n)"
- **`--auto` mode:** Merge automatically after Staff+ review approval
- Use `gh pr merge --merge --delete-branch`

### Step 6: Archive

Run `$para-archive` for cleanup.

- For mid-workflow, perform partial archive behavior: update `context/context.md` to reflect completed phase but keep remaining phases active
- For final phase, perform full archive: move context to archives and create fresh context

### Step 7: Next Phase

If more phases remain:

- **Default mode:** Pause and ask "Ready to start Phase {N+1}? (Y/n)"
- **`--auto` mode:** Proceed immediately
- Pull latest main with the merged phase
- Update `context/context.md` to reflect the next active phase
- Loop back to Step 1

## State Tracking

Track workflow progress in `context/context.md` metadata with a workflow state object. See `../para-init/references/context-schema.md` for the full field reference.

If ../para-init/references/context-schema.md is not available in this install, the minimal workflow state fields are: mode, current_step, current_phase, phases_completed, and started.

This enables resumability. If the workflow is interrupted, running `$para-workflow` again picks up from the current step of the current phase.

## Error Handling

- **Step failure:** If any step fails, such as tests failing, PR conflicts, or review non-convergence, pause and present the error with options to fix and continue, skip the current step, or abort.
- **Merge conflicts:** If the PR cannot be merged, pause and ask the user to resolve conflicts manually. After resolution, resume with `$para-workflow`.
- **Review non-convergence:** If Staff+ review hits the 5-round limit, escalate per `$para-review` convergence rules. The workflow pauses until the user decides.

## Completion

When all phases are complete:

1. Run full archive (`$para-archive`)
2. Display summary of all phases:
   - Total phases completed
   - Total commits across all phases
   - PRs merged with links
   - Staff+ review rounds per phase
3. Suggest next steps, such as tagging a release or updating documentation

## Notes

- The workflow command is an orchestrator; it delegates to `$para-execute`, `$para-review`, `$para-summarize`, and `$para-archive`
- `--auto` mode still requires Staff+ review approval as a quality gate unless `--skip-review` is also specified
- Each phase creates its own PR, enabling incremental review and merge
- The workflow is resumable; state is tracked in `context/context.md`
- For single-phase plans, the workflow still works but is equivalent to running the skills manually
