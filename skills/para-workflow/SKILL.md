---
name: para-workflow
description: Orchestrate simple or phased plans through execution, PR preparation, review, summary, merge and archival, with resumable evidence and optional auto mode.
---

Run the lifecycle for an active simple or phased plan: execute → prepare PR → review → summarize → merge → archive and cleanup. A successful merge does not complete the workflow until final archival and eligible task-worktree cleanup are verified.

## Usage

```text
para-workflow
para-workflow --auto
para-workflow --phase=N
para-workflow --skip-review
```

Read primary `context/context.md`, the selected plan and `../para-init/references/context-schema.md`. Resolve any ambiguous task/root before writing. For a simple task, apply `../para-init/references/simple-plan-binding.md`, persist/reread `execution.plan` before execution, and require `para-execute` to verify it before implementation. If ../para-init/references/simple-plan-binding.md is not available in this install, stop simple execution until an exact binding is reconciled. A simple plan uses top-level execution evidence and null current_phase, without synthetic phases; reject `--phase` for it. Phased work uses its explicit master/phase plan records and verifies predecessor merges before starting the selected phase.

If ../para-init/references/context-schema.md is not available in this install, preserve context and record plan/branch/base, PR identity, reviewed head, summary and verified merge evidence. Missing evidence is unknown, never completion; stop dependent operations when it cannot be recovered.

## Run or resume

Before advancing, persist and reread the completed step’s evidence in primary `context/context.md`: for simple tasks preserve `execution.plan`; then branch/base/commit, PR identity, review `{status,target,mode}`, and summary path. Record workflow mode/current_step/current_phase/started; preserve unrelated fields. Do not defer these writes until merge/archive. Reconcile actual Git/GitHub state and reuse verified effects, including direct skill results and existing authorization. Read the current step and needed evidence; do not reload all history routinely. Design evidence can remain valid while merge eligibility must be freshly verified. Apply the shared binding reference before recovering a legacy simple execution without `execution.plan`; ambiguity blocks progress.

1. **Execute:** Use the `para-execute` skill for the selected task/phase. Wait for its commits and required validation.
2. **Prepare PR:** This step owns PR creation for workflow runs, both simple and phased. Push the execution branch. Query the selected repository/head/base for a matching PR; reuse it, create only if absent, and reconcile ambiguous responses before retrying. Record PR identity. Describe the problem, outcome, validation and plan objective in its body; do not link to local-only plan files as though published.
3. **Review:** Use the `para-review` skill with `--pr` and the PR identity. Apply supported fixes, rerun affected checks, push, and establish review eligibility for the resulting head. Respect its five-round/repeated-blocker limit. `--skip-review` records a user-requested skip against this target; it does not waive checks or merge authorization.
4. **Summarize:** Use the `para-summarize` skill for the task/phase. Record its summary path; a summary does not complete a phase.
5. **Merge:** In a separate tool call, parse the saved primary context JSON and verify PR identity, review target/status, mode (`independent` or an explicit `self`/`user` override), and summary against this task and current head. Require an explicit successful result: missing or stale records block merge, as do write/parse/check errors. Never append merge to a context-update or verification command. Confirm authorization. Query required-check results for the current PR head; require success. Submit `gh pr merge --match-head-commit <validated-sha>` with the repository-supported merge method. On head mismatch, reconcile and re-establish eligibility; never retry unguarded or bypass checks. Verify remote merge before marking completed. A queued merge stays pending.
6. **Phase cleanup:** After each verified phase merge and summary, invoke `para-archive --phase=N` in this run. Independently verify every recorded worktree for that phase is absent from `git worktree list --porcelain` and its cleanup evidence is recorded before fetching the updated base or advancing. If cleanup is blocked or unverifiable, stop phase progression and report the blocker; do not call the phase complete.
7. **Final archive and cleanup:** After the whole simple/phased task is verified merged and summarized, invoke `para-archive` in this run. It must archive the completed plan file(s) as well as the context snapshot, remove only verified clean task worktrees, and reset task-specific active context only when cleanup succeeds. Do not merely recommend archival or describe it as a remaining step. Before reporting completion, independently parse the task-bound archive receipt and verify: (a) the snapshot records the verified merge and summaries; (b) for a simple task, exactly one receipt plan source equals the snapshot's immutable `execution.plan` binding; (c) every plan recorded in simple or phased execution evidence has an existing archived copy whose SHA-256 matches the receipt; (d) no completed task plan remains in fresh `active_context`; and (e) the receipt's task-worktree paths exactly cover the union of simple and phase worktree paths, including phase paths preserved in cleanup evidence, and each is absent from `git worktree list --porcelain`. If any check fails, report the workflow as incomplete with the exact remaining path/evidence and retain recovery state. Preserve unrelated active plans and worktrees and identify them as unrelated rather than treating them as task cleanup failures.

## Authorization and failures

Default mode asks before merge and before advancing to the next phase unless already authorized. `--auto` authorizes those transitions for this run; continue without redundant permission prompts. It does not waive review/check gates. Record explicit user overrides rather than inventing them.

Repeated unsuccessful repairs/searches need new evidence or a changed hypothesis. Otherwise preserve progress and the unresolved fact, then direct focused investigation or consequential replanning; retain direct-skill boundaries. Pending CI/merge or transient failures can justify bounded polling/backoff, not rapid identical calls.

A failed or uncertain step blocks its dependents. Fix recoverable errors within scope, reconcile conflicts and resume from verified state; ask only for unresolved authorization or design choices. Never use a generic skip to bypass a downstream invariant. A verified merge with pending/failed archive or cleanup is not a completed workflow. Return phase results, merged PR links, validation, archive receipt and remaining blockers. Preserve pending work if interrupted.
