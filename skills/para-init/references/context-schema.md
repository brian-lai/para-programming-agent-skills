# Context and lifecycle contract

`context/context.md` contains a summary, todos/progress notes and one fenced JSON metadata block. Read the sections needed for the current operation. This is an instruction contract, not an executable state engine.

## Roots and writes

Resolve the primary checkout/context root and execution checkout from Git worktree metadata; ask only if ambiguous. Workflow artifacts belong to primary `context/`; source edits/tests/commits belong to the execution checkout. Do not trust a worktree-local context copy. Preserve unknown fields and unrelated references; deduplicate appended paths. Parse before editing; malformed or concurrently changed state requires reconciliation. One orchestrator writes an active task.

## Fields

| Field | Type / meaning |
|---|---|
| `active_context` | Required string[]: active plan paths, including unmerged work |
| `completed_summaries` | Required string[]: actual summary paths; summary is not merge evidence |
| `last_updated` | Required ISO timestamp |
| `research_docs` | Optional string[]: research paths |
| `execution_branch`, `worktree_path` | Simple task's branch and path; path null for branch-only execution |
| `execution_started` | Optional ISO timestamp |
| `phased_execution` | Optional `{master_plan, phases, current_phase, staff_review?}`; absent for simple plans |
| `phased_execution.phases[]` | `{phase, plan, status, branch, worktree_path, execution?}`; branch/path null until execution |
| `workflow` | `{mode, current_step, current_phase, phases_completed, started}`; mode default/auto; current_phase null for simple plans |
| `archive_target` | Reserved final snapshot path; retained in snapshot, omitted from fresh context |

Phase status: `pending`, `in_progress`, `completed`; completed means verified merged. `workflow.current_step`: execute/pr/review/summarize/merge/archive. It is a resume hint, not proof of an effect. Reconcile `phases_completed` with merge evidence. A simple task needs no synthetic phases.

Evidence belongs in top-level `execution` for a simple task or the active phase's `execution`, never both. Existing branch/path fields remain canonical.

| Field | Shape / evidence |
|---|---|
| `execution.base` | `{remote, branch, start_sha}` resolved from repository configuration/PR; no assumed origin/main |
| `execution.pr` | `{repository, number, url}` verified against head/base |
| `execution.review` | `{status, target, mode}`; target = PR head SHA; status approved/changes_requested/overridden/skipped; mode independent/self/user |
| `execution.summary` | Summary path |
| `execution.merge` | `{commit}` after remote confirms merge |

Plan approval records plan paths/content digests in progress notes separately. A legacy `staff_review` string cannot approve a new target. Recover legacy missing fields from unambiguous Git/GitHub facts; preserve history and report unknowns when remote verification is unavailable.

## Lifecycle

| Operation | Owner | Success evidence / recovery |
|---|---|---|
| Implement | execute | Required checks pass, intended commit exists; then mark todo complete. Reconcile commit-before-context failures. |
| Prepare PR | workflow | Push, find matching repository/head/base PR, create only if absent; query ambiguous responses before retry. |
| Review | review | Independent result for current head, or explicit user override/skip; self-review is not independent approval. |
| Summarize | summarize | Actual branch diff and check evidence recorded; append summary path without declaring merge. |
| Merge | workflow | Existing authorization, eligible review and required checks for head; guarded request, then remote confirmation. |
| Phase cleanup | archive --phase=N | Merged, summarized phase; remove only its clean worktree; retain pending work. |
| Final archive | archive | Entire task merged/summarized; one recoverable snapshot, then fresh context. |

Workflow handles simple and phased plans. Direct skills perform their own operation and return; they do not publish PRs or chain the lifecycle. Resume from actual Git/GitHub state before repeating effects. Advance a dependent phase only after its predecessor's merge is included in the selected base.

Bind merge to the validated SHA with `gh pr merge --match-head-commit <sha>` (or equivalent server guard). A changed head requires reconciliation and fresh eligibility; never retry unguarded or bypass checks. Queued merges remain pending until remotely merged. User override/skip does not waive required checks or merge authorization.

Keep command/results, commit IDs, PR identity and blockers in progress notes. Missing dependencies or failed gates block dependent actions; continue independent inspection. Do not silently skip a gate.

## Archive recovery

Never force-remove dirty worktrees or archive open/unverified work as finished. Reserve a unique `archive_target` before saving the snapshot, save before resetting context, and reuse that target on retry only after verifying task identity. Never overwrite another snapshot. Already-removed worktrees are reconciled, not errors requiring destructive recreation. Fresh context without active work is a no-op. Phase cleanup does not reset context.

## Fresh context example

```json
{
  "active_context": [],
  "completed_summaries": [],
  "research_docs": [],
  "worktree_path": null,
  "last_updated": "2026-10-04T12:00:00Z"
}
```
