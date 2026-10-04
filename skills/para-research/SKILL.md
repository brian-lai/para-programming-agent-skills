---
name: para-research
description: Investigate relevant code, contracts and uncertainties before planning; produce a compact research snapshot with evidence and freshness guidance.
model: opus
effort: high
---

Investigate the facts needed to plan the requested change. Research is read-only except for primary-context artifacts.

## Usage

```text
para-research <task> [--scope=<area>] [--specs]
```

1. Identify the task and primary context root. Read existing research and project guidance first; inspect the affected code, contracts and tests. Ask only about material uncertainty the available evidence cannot resolve.
2. Follow relevant call/data paths and failure handling. `--scope` bounds exploration; `--specs` emphasizes interface contracts. Read adjacent components only when they affect a decision. Reuse existing specs; distinguish observed behavior from inference.
3. Stop when remaining unknowns would not change scope, design or validation. For unresolved consequential gaps, record the next focused check rather than claiming exhaustive coverage.
4. Write `context/data/YYYY-MM-DD-task-name-research.md` using `assets/research-template.md`. Include the inspected revision, relevant source paths/symbols, decisions supported by evidence, gaps and freshness conditions. Omit irrelevant sections and long file inventories.
5. Parse primary context before writing; preserve existing/unknown fields, append and deduplicate research_docs, and update last_updated. Malformed or concurrently changed state requires reconciliation. Report the artifact and planning-relevant findings; recommend the `para-plan` skill.

Research is a snapshot. Reopen sources when the revision/scope changed or a decision lacks evidence; the document does not promise to eliminate future exploration.
