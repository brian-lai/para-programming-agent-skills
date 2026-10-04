---
name: para-workflow
description: Orchestrate simple or phased plans through execution, PR preparation, review, summary, merge and archival, with resumable evidence and optional auto mode.
model: sonnet
effort: medium
---

Run the lifecycle for an active simple or phased plan: execute → prepare PR → review → summarize → merge → cleanup. Use the same procedure for one task or each phase.

## Usage

```text
para-workflow
para-workflow --auto
para-workflow --phase=N
para-workflow --skip-review
```

Read primary `context/context.md`, the active plan and `../para-init/references/context-schema.md`. Resolve any ambiguous task/root before writing. A simple plan uses top-level execution evidence and null current_phase, without synthetic phases; reject `--phase` for it. For phased work verify predecessor merges before starting the selected phase.

If ../para-init/references/context-schema.md is not available in this install, preserve context and record plan/branch/base, PR identity, reviewed head, summary and verified merge evidence. Missing evidence is unknown, never completion; stop dependent operations when it cannot be recovered.

## Run or resume

Record mode/current_step/current_phase/started and reconcile actual Git/GitHub state before each side effect. Preserve unrelated fields. Reuse already verified effects, including work completed through a directly invoked skill.

1. **Execute:** Use the `para-execute` skill for the selected task/phase. Wait for its commits and required validation.
2. **Prepare PR:** This step owns PR creation for workflow runs, both simple and phased. Push the execution branch. Query the selected repository/head/base for a matching PR; reuse it, create only if absent, and reconcile ambiguous responses before retrying. Record PR identity. Describe the problem, outcome, validation and plan objective in its body; do not link to local-only plan files as though published.
3. **Review:** Use the `para-review` skill with `--pr` and the PR identity. Apply supported fixes, rerun affected checks, push, and establish review eligibility for the resulting head. Respect its five-round/repeated-blocker limit. `--skip-review` records a user-requested skip against this target; it does not waive checks or merge authorization.
4. **Summarize:** Use the `para-summarize` skill for the task/phase. Record its summary path; a summary does not complete a phase.
5. **Merge:** Confirm authorization, required checks and eligible review for the current PR head. Submit the guarded merge described in the context contract and verify remote merge before marking completed. A queued merge stays pending.
6. **Cleanup:** For phased work, use the `para-archive` skill with `--phase=N`; keep pending plans active. Fetch the updated base including the verified merge, then advance. Once the whole simple/phased task is merged and summarized, use the `para-archive` skill once for final archive.

## Authorization and failures

Default mode asks before merge and before advancing to the next phase unless already authorized. `--auto` authorizes those transitions for this run; continue without redundant permission prompts. It does not waive review/check gates. Record explicit user overrides rather than inventing them.

A failed or uncertain step blocks its dependents. Fix recoverable errors within scope, reconcile conflicts and resume from verified state; ask only for unresolved authorization or design choices. Never use a generic skip to bypass a downstream invariant. Return phase results, merged PR links, validation and remaining blockers. Preserve pending work if interrupted.
