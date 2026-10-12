# Simple Plan Binding

Applies only to simple tasks; phased tasks use explicit master/phase fields.

- Resume the existing `execution.plan`. If a request selects a different plan, stop to reconcile; never overwrite the binding.
- Otherwise use the exact plan named by the request, defaulting only to the sole `active_context` entry. If multiple plans remain ambiguous, ask before writes or checkout changes; never choose by array order. Persist the project-relative source in `execution.plan` before implementation and require one exact `active_context` match.
- Keep `execution.plan` immutable. At archive start it must match one active entry; on retry it must match one `archive_plan_targets[].source`. Retain it in the archived snapshot while rewriting `active_context` to the copy.
- A simple receipt contains one plan file whose source equals `execution.plan` and whose destination hash matches. Workflow verifies snapshot, receipt, copy and hash. Missing or conflicting identity blocks plan moves and worktree cleanup. Clear the field only after successful archival.
