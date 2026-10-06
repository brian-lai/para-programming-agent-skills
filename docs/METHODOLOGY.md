# PARA-Programming Methodology

PARA organizes work into research, planning, execution, review, summary and archival. The skills are instructions interpreted by a host agent; they are not a transactional workflow engine. Their effectiveness must be evaluated with actual agent runs.

## Ownership and artifacts

The [context contract](../skills/para-init/references/context-schema.md) defines fields, roots, lifecycle evidence and recovery. The primary checkout holds dated research/plans/progress/summaries. Implementation uses an isolated Git worktree or an explicitly selected execution branch. Worktree isolation depends on choosing the correct paths; it does not restrict filesystem access.

All implementation changes follow the project branch/PR policy. Workflow artifacts do not recursively require another plan. Existing context and unknown fields survive updates.

## The PARA loop, step by step

**Research and planning do not create a worktree.** They inspect source and write workflow artifacts under the primary checkout's `context/` directory. By default, `para-execute` creates or reuses the isolated worktree when implementation starts. Any needed source stubs are created there during execution.

The complete sequence is:

**Research → Plan → Review Plan → Execute → Prepare PR → Review PR → Summarize → Merge → Cleanup / Archive**

| Step | What happens |
|---|---|
| 1. Research | [`para-research`](../skills/para-research/SKILL.md) inspects relevant code, contracts, tests and failure paths. It saves a dated snapshot under `context/data/`, with evidence, unresolved questions and freshness conditions. A separate research pass is optional when the facts needed to plan are already clear. |
| 2. Plan | [`para-plan`](../skills/para-plan/SKILL.md) turns findings into outcomes, affected files, implementation steps, validation, risks and acceptance criteria. It asks about material unresolved choices and defaults to a simple plan. Plans go under `context/plans/`; new boundary specifications, when needed, go under `context/data/`. Each implementation checkbox supplies a commit message. |
| 3. Review plan | [`para-review --plan`](../skills/para-review/SKILL.md) uses a fresh independent reviewer to check requirements, scope, implementation readiness and validation. Supported blockers are corrected and reviewed again. Approval is tied to the reviewed plan contents. |
| 4. Execute | [`para-execute`](../skills/para-execute/SKILL.md) resolves and fetches the base branch, then creates `.para-worktrees/{task-name}` on `para/{task-name}`, or reuses a matching checkout when resuming. It implements and validates each todo, commits it, then records completion and the SHA in primary context. |
| 5. Prepare PR | [`para-workflow`](../skills/para-workflow/SKILL.md) pushes the execution branch, creates or reuses its matching PR, and records PR identity. The PR describes the problem, outcome and validation. |
| 6. Review PR | [`para-review --pr`](../skills/para-review/SKILL.md) checks actual changes against the plan and evidence. Supported fixes are applied, affected checks rerun, and changes pushed. Approval belongs to a specific head SHA; a changed head needs renewed review eligibility. |
| 7. Summarize | [`para-summarize`](../skills/para-summarize/SKILL.md) inspects committed changes against the base and writes a dated report under `context/summaries/`, covering changes, rationale, observed validation and remaining work. A summary alone does not establish completion. |
| 8. Merge | `para-workflow` verifies saved PR identity, review eligibility for the current head, the summary, successful required checks and authorization. It submits a merge guarded by the validated head SHA, then verifies that the remote merge actually happened. A queued merge remains pending. |
| 9. Cleanup / archive | [`para-archive`](../skills/para-archive/SKILL.md) removes only clean, verified task worktrees after merge and summary. Final archival saves a recoverable context snapshot and creates fresh context, retaining summary references by default. Dirty or unfinished work is preserved. |

For testable behavior, execution observes a meaningful failing test before implementing the fix. Required checks pass before committing each todo. Documentation and configuration changes without meaningful behavioral tests use structural or manual validation. A commit's existence does not prove the order in which tests were authored.

Research, plans, progress and summaries continue to use the **primary checkout's shared `context/` directory**, even while implementation happens in a separate worktree. Execution resolves this root using Git worktree metadata rather than trusting a potentially stale worktree-local context copy. With the explicit `para-execute --no-worktree` option, implementation uses an execution branch in the current checkout, provided switching preserves existing work.

## Orchestration, phases and authorization

Use `para-workflow` after planning and plan review to run execution through PR preparation, review, summary, merge and archival. Direct skills perform their own operation and return: standalone `para-execute` does not push or create a PR; standalone review and summary do not launch the rest of the lifecycle.

A simple plan runs the execution-to-cleanup sequence once. A phased plan repeats it for each independently mergeable phase. Each phase gets its own branch/worktree with a `-phase-N` suffix, PR, review, summary and verified merge. The next dependent phase starts from an updated base containing its prerequisite merges. Phase cleanup retains pending plans and evidence; one final archive closes the whole task.

Default workflow mode asks before merging or advancing to the next phase unless those actions are already authorized. `para-workflow --auto` authorizes those transitions for the run while retaining review and required-check gates. Existing authorization is preserved, so it should not prompt repeatedly for the same permission.

## Review and merge

Independent review checks artifacts against requirements and evidence. A fresh reviewer may still be influenced by its input packet; no persona guarantees correctness. Record the reviewed head, distinguish user override/skip from approval, and retain required check gates. Use an expected-head merge guard so a concurrent push cannot silently substitute an unreviewed commit. A queued request is not yet a merge.

Each correction loop escalates unresolved blockers after five rounds, or sooner if two consecutive rounds produce the same MUST FIX issues. Every independent round uses a fresh reviewer. Review reports host isolation as verified, unavailable or unknown; a separate conversation or worktree alone does not enforce read-only access. If required enforcement is unavailable, that gate remains unsatisfied. See [reviewer isolation](reviewer-isolation.md) for the evaluation host's enforced boundary.

## Interruption and recovery

Context records intent and observed results. On resume, query Git/GitHub before repeating side effects. Reuse existing PRs, reconcile commits that preceded failed metadata writes, and verify remote merges before advancement. Legacy completion strings without evidence do not authorize new actions.

Archive only merged/summarized work. Phase cleanup preserves other phases; final archival reserves a unique destination, saves a snapshot, and initializes fresh context. Dirty worktrees, uncertain identity and missing merge evidence block dependent cleanup. Archives and branches support recovery.

## Context cost and validation

References and templates are loaded when needed. Smaller files alone do not prove lower runtime cost: measure required resources, repeated reads and generated artifacts. Static checks cover packaging, names, links and declared contracts. Disposable Git fixtures and recorded host-agent runs establish observed behavior; deterministic graders inspect actual effects rather than an agent's completion claim.

This workflow adopts software engineering practices and context-management techniques as design choices. Claims about gains in task success or token usage require a pinned baseline, comparable trials and reported limitations. See the [skill catalog](../README.md) for installation and invocation.

## Basis and limits

- [Agent Skills specification](https://agentskills.io/specification): supports progressive loading of metadata, instructions and optional resources. PARA makes load conditions explicit and budgets complete instruction paths, including shared references.
- [Anthropic context engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): motivates focused retrieval and persistent notes. These are design inputs, not measured PARA token savings.
- [Anthropic agent evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): distinguishes agent trajectories and environment outcomes. PARA evaluates recorded effects with deterministic checks plus calibrated judgment for subjective quality.

Branch policy, todo-sized commits and the review cap are project choices. Neither prestige personas nor fixed reread counts establish correctness. Current text savings are static bytes; live success, latency and usage require paired runs on pinned revisions.
