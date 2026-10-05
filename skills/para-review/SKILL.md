---
name: para-review
description: Independently review a plan or existing PR against requirements and evidence, with target-bound results and a capped correction loop.
model: opus
effort: high
---

Review the requested artifact for consequential defects. Return the result to the caller; workflow owns subsequent lifecycle steps.

## Usage

```text
para-review --plan
para-review --plan=path/to/plan.md
para-review --pr
para-review --pr=123
para-review --approve
```

## Target and packet

1. Resolve the primary context and explicit/active plan or existing PR. Plan mode includes all sub-plans and records paths/content digests. PR mode verifies repository/head/base, reads the diff and relevant files/check results, and records the head SHA. If no PR exists, recommend the `para-workflow` skill to prepare it; direct review never creates one.
2. Spawn a fresh subagent with a small packet: requirements, artifact/diff, relevant source/check evidence and prior issue ledger. Exclude author conversation when the host supports it; report capability limits. A fresh context reduces shared assumptions but does not guarantee correctness or eliminate anchoring from the ledger; never continue a previous reviewer as a new independent round.
3. If independent review is unavailable, report it. A disclosed self-review can provide feedback but cannot satisfy the independent gate without an explicit user override. Do not fabricate a reviewer or approval.

Keep source, context and Git metadata read-only; run write-requiring tests in disposable scratch. Record host isolation as verified, unavailable or unknown. A prompt, fresh agent or worktree does not enforce this boundary. If required enforcement is unavailable, report the limitation and leave that gate unsatisfied. Host setup is documented separately.

## Evidence rubric

For each finding provide location, trigger, violated requirement, impact and supporting evidence. Label uncertainty and the check needed to resolve it. Classify:
- **MUST FIX:** a demonstrated correctness, security, data-preservation or required-contract defect that blocks proceeding.
- **SHOULD FIX:** a supported improvement with concrete benefit, without a blocking violation.
- **NIT:** an optional preference; never block for style alone.

Check applicable boundaries, failure/recovery paths, scope, acceptance criteria, validation and maintainability. Plan reviews verify implementation readiness and mergeable phases. PR reviews check actual changes against the plan and meaningful regression coverage. Command/result evidence can support RED→GREEN; commit order alone cannot prove TDD. No persona/title is evidence of review quality. Return APPROVED when no MUST FIX remains; do not invent changes to make the review appear useful.

## Correction loop and convergence

Present findings with stable issue IDs. Apply supported fixes, record disposition and relevant checks in the issue ledger, then spawn a fresh reviewer. Recheck affected parts and interactions after material fixes, with the original requirements available. Resolve unsupported findings explicitly with evidence.

**5-round maximum:** Escalate unresolved blockers after five rounds. If two consecutive rounds produce the same MUST FIX issues, escalate immediately with the remaining evidence and options to revise, continue, or explicitly override. Never silently skip a failed gate.

Record plan approval against plan digests in progress notes. For a PR write execution.review as {status, target, mode} at the task/phase evidence location: status approved/changes_requested/overridden; target = reviewed head SHA; mode independent/self/user. Preserve unrelated metadata. Approval does not transfer to a changed head; verify resulting head and required checks after fixes. Missing or ambiguous execution identity requires reconciliation before writing.

`--approve` is an explicit user override for the identified target. Record overridden/user separately from independent approval and return it to the caller. It does not waive required checks or merge authorization. Never supply this flag on the user's behalf to bypass findings.
