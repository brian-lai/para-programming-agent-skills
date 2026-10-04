# PARA-Programming Methodology

PARA organizes work into research, planning, execution, review, summary and archival. The skills are instructions interpreted by a host agent; they are not a transactional workflow engine. Their effectiveness must be evaluated with actual agent runs.

## Ownership and artifacts

The [context contract](../skills/para-init/references/context-schema.md) defines fields, roots, lifecycle evidence and recovery. The primary checkout holds dated research/plans/progress/summaries. Implementation uses an isolated Git worktree or an explicitly selected execution branch. Worktree isolation depends on choosing the correct paths; it does not restrict filesystem access.

All implementation changes follow the project branch/PR policy. Workflow artifacts do not recursively require another plan. Existing context and unknown fields survive updates.

## Research and plan

Research records source locations, relevant contracts, decisions and gaps. A planner checks the requested scope and current evidence, resolving meaningful uncertainty before execution. Existing contracts can be reused. Source stubs, when useful, are created inside execution rather than the primary checkout.

A simple plan is one execution unit. A phased plan has independently mergeable units with explicit dependencies. Each todo is a coherent behavior change including its meaningful validation; its text supplies the commit message. Required checks pass before commit. A commit's existence proves the change was recorded, but does not prove the order in which tests were authored.

## Universal orchestration

Use the `para-workflow` skill after planning/review for either plan kind. It owns this sequence:

| Stage | Result |
|---|---|
| Execute | Validated task commits |
| Prepare PR | Pushed branch and matching PR identity |
| Review | Result tied to PR head |
| Summarize | Actual changes and observed validation |
| Merge | Authorized, guarded, remotely verified merge |
| Cleanup | Completed phase worktree removed; pending state retained |

Simple work runs once. Phased work repeats only after predecessor merges are included in the selected base. A single final archive closes the complete task. Direct skills perform only their own operation and return to the caller.

## Review and merge

Independent review checks artifacts against requirements and evidence. A fresh reviewer may still be influenced by its input packet; no persona guarantees correctness. Record the reviewed head, distinguish user override/skip from approval, and retain required check gates. Use an expected-head merge guard so a concurrent push cannot silently substitute an unreviewed commit. A queued request is not yet a merge.

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
