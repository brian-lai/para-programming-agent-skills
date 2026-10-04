---
name: para-plan
description: Plan a repository change using inspected evidence and focused clarification; produce a simple or phased plan with concrete acceptance criteria before execution.
model: opus
effort: high
---

Create an implementation-ready plan proportional to the requested change. Planning writes primary-context artifacts; source changes begin during execution.

## Usage

```text
para-plan [task-description]
```

## Inspect, decide, draft

1. Resolve the task from the request and active context; ask if missing or ambiguous. Inspect existing research, project guidance, relevant code/contracts and validation commands. Use the `para-research` skill when consequential gaps need deeper exploration.
2. Ask only about material unresolved choices affecting scope, behavior, cost or risk. Present concise options with tradeoffs. Preserve decisions and authorization already given; do not ask questions answered by inspection.
3. Choose a simple plan by default. Consider phases for cross-file refactoring across many files, multiple architectural layers, or dependencies requiring an earlier merge into the selected base. Prefer independently reviewable, mergeable outcomes over arbitrary file counts. Confirm a proposed phase split unless already agreed.
4. Reuse existing contracts. Create a spec under `context/data/` only for a new/changed boundary needing one; describe necessary interfaces and anticipated stub paths. Create any source stubs later in the execution checkout. Include architecture, failure handling, observability and test categories only where the change makes them relevant.
5. Draft outcome, affected files, behavior-sized steps, validation, material risks and measurable acceptance criteria. **Checklist = commit:** checkbox text is the commit message; keep items atomic -- one logical change per item. Each step includes its meaningful tests/checks and implementation. For testable behavior, observe failure before the fix, then keep required checks green before commit. Documentation can use structural/manual checks; do not invent test signatures or metrics.
6. Check requirements, source contracts, paths, ordering and validation once; fix supported gaps and recheck affected parts after material changes. Stop when no blocking gaps remain. Use the independent `para-review` skill with `--plan` for the review gate; its 5-round cap and repeated-blocker escalation apply. Do not count edits or require fixed rereads.
7. Save the plan and update context as below. Present scope, decisions, open issues and the next step. When already authorized, continue through the `para-workflow` skill; otherwise offer plan review or execution. Direct `para-execute` performs implementation only.

## Templates and context

Load only the selected template:
- Simple: `assets/plan-template.md` → `context/plans/YYYY-MM-DD-task-name.md`.
- Phased: `assets/phased-plan-master-template.md` plus `assets/phased-plan-sub-template.md` → master and `YYYY-MM-DD-task-name-phase-N.md` files. Keep master decisions shared; each sub-plan carries only the contract/dependency context needed to execute its phase.

Read `../para-init/references/context-schema.md` when updating metadata. Preserve unrelated/unknown fields; append/deduplicate active_context and update last_updated. Simple plans do not create phased_execution. For phased plans initialize pending entries with branch/worktree_path null, preserving existing progress when revising. Record plan-review paths/digests separately from PR-head approval.

If ../para-init/references/context-schema.md is not available in this install, preserve existing state and use active_context/completed_summaries/research_docs arrays and last_updated; phased_execution contains master_plan, phases (phase, plan, status, branch, worktree_path), and current_phase. Parse before mutation; unresolved malformed/concurrent state blocks writes.
