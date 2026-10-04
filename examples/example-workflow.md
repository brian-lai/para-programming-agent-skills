# Example: one task

Use the `para-research` skill when the task needs exploration, then the `para-plan` skill to capture scope, contracts and validation. Review the plan using the `para-review` skill with `--plan`.

## Skill requests

```text
para-research Add authentication
para-plan Add authentication
para-review --plan
para-workflow --auto
```

Workflow supports both simple and phased plans. A simple plan runs once without phase files. Split a larger change into independently mergeable phases when dependencies or review scope justify it; for example, session storage, API integration, then UI integration.

For every execution unit: implement behavior-sized todos with required checks green, prepare/reuse a PR, review its head, summarize actual changes, verify an authorized guarded merge, then clean up. A summary is not merge evidence. The next dependent phase starts from the updated base. Final archive happens once after all work is merged and summarized.

State lives in primary `context/context.md`; source edits and commits happen in the execution checkout. Unknown fields and unrelated work survive updates. Directly invoking execute or summarize performs only that operation; workflow resumes from verified results.

If interrupted after PR creation, find the existing PR before retrying. If review's head changed, re-establish eligibility. Never force-remove dirty worktrees. See the [context contract](../skills/para-init/references/context-schema.md) for fields and recovery.
