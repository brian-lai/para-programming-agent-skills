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

Before advancing, persist and reread the completed step’s evidence in primary `context/context.md`: branch/base/commit, PR identity, review `{status,target,mode}`, then summary path. Record workflow mode/current_step/current_phase/started; preserve unrelated fields. Do not defer these writes until merge/archive. Reconcile actual Git/GitHub state and reuse verified effects, including direct skill results.

1. **Execute:** Use the `para-execute` skill for the selected task/phase. Wait for its commits and required validation.
2. **Prepare PR:** This step owns PR creation for workflow runs, both simple and phased. Push the execution branch. Query the selected repository/head/base for a matching PR; reuse it, create only if absent, and reconcile ambiguous responses before retrying. Record PR identity. Describe the problem, outcome, validation and plan objective in its body; do not link to local-only plan files as though published.
3. **Review:** Use the `para-review` skill with `--pr` and the PR identity. Apply supported fixes, rerun affected checks, push, and establish review eligibility for the resulting head. Respect its five-round/repeated-blocker limit. `--skip-review` records a user-requested skip against this target; it does not waive checks or merge authorization.
4. **Summarize:** Use the `para-summarize` skill for the task/phase. Record its summary path; a summary does not complete a phase.
5. **Merge:** In a separate tool call, parse the saved primary context JSON and verify PR identity, eligible review target/status/mode and summary against this task and current head. Require an explicit successful result: missing or stale records block merge, as do write/parse/check errors. Never append merge to a context-update or verification command. Confirm authorization and required checks. Submit `gh pr merge --match-head-commit <validated-sha>` with the repository-supported merge method. On head mismatch, reconcile and re-establish eligibility; never retry unguarded or bypass checks. Verify remote merge before marking completed. A queued merge stays pending.
6. **Cleanup:** For phased work, use the `para-archive` skill with `--phase=N`; keep pending plans active. Fetch the updated base including the verified merge, then advance. Once the whole simple/phased task is merged and summarized, use the `para-archive` skill once for final archive.

## Authorization and failures

Default mode asks before merge and before advancing to the next phase unless already authorized. `--auto` authorizes those transitions for this run; continue without redundant permission prompts. It does not waive review/check gates. Record explicit user overrides rather than inventing them.

A failed or uncertain step blocks its dependents. Fix recoverable errors within scope, reconcile conflicts and resume from verified state; ask only for unresolved authorization or design choices. Never use a generic skip to bypass a downstream invariant. Return phase results, merged PR links, validation and remaining blockers. Preserve pending work if interrupted.
