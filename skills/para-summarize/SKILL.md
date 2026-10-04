---
name: para-summarize
description: Summarize actual branch changes and validation for a task or phase, preserving unmerged work and returning the report to its caller.
model: sonnet
effort: medium
---

Record the actual changes, rationale, validation and remaining work for a task or phase.

```text
para-summarize
para-summarize --phase=N
```

1. Resolve the primary context, active plan and execution branch/worktree. If phased, select the requested/current phase; ask only if ambiguous.
2. Inspect committed changes against the PR base, or the recorded/resolved base and its merge-base with the execution branch. Use the same branch comparison with `--no-worktree`; plain working-tree `git diff` misses committed changes. If the branch was deleted after merge, recover the recorded PR diff/commits. Report missing evidence instead of an empty result.
3. Write primary `context/summaries/YYYY-MM-DD-task-name[-phase-N]-summary.md` using `assets/summary-template.md`. Include only observed checks/results; unknown coverage or timing is not a measured value.
4. Preserve context, append/deduplicate the actual summary path in completed_summaries, record execution.summary and timestamp. This does not mark the task/phase merged or remove unmerged plans from active context.
5. Return to the orchestrator when called by workflow. In standalone mode, return the report and missing lifecycle prerequisites; do not publish a PR or launch later skills. Use the `para-workflow` skill to continue the lifecycle.
