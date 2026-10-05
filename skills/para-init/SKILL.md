---
name: para-init
description: Initialize PARA-Programming structure in the current project. Use when setting up a new repo for PARA workflow, creating context/ directory, or bootstrapping AGENTS.md.
model: haiku
effort: low
---

Initialize only missing PARA structure, preserving existing context and project guidance.

```text
para-init [--template=basic|full]
```

1. Resolve the primary project/context root; inspect existing AGENTS.md, context, repository facts and check commands. Parse existing context before any mutation. Preserve its contents, active progress and unknown fields; malformed state requires reconciliation, not a reset.
2. Create missing directories: context/data, context/plans, context/summaries, context/archives and context/servers. Create context/context.md from `assets/context-template.md` only if absent, with the actual timestamp. See `references/context-schema.md` for field meanings; do not replace existing context from a template.
3. If project AGENTS.md is absent, fill `assets/agents-basic-template.md` (default) or `assets/agents-full-template.md` from inspected project facts. Omit inapplicable sections and label unknown facts. Do not invent tools, commands, coverage targets or credentials. Preserve an existing AGENTS.md; propose additions separately only when needed.
4. If global ~/.agents/AGENTS.md is missing and the bundle includes ../../resources/AGENTS.md (relative to this skill directory), copy that methodology. This operation never overwrites existing global guidance. In a single-skill install without that resource, report the missing optional guidance and continue with the local skill contract.
5. Append .para-worktrees/ to .gitignore only if not already covered. This is a tracked project change: use an existing authorized execution branch/worktree or the project branch/PR workflow. Missing primary-context artifacts themselves do not recursively require a plan.
6. Report created, preserved and pending files accurately. Recommend the `para-plan` skill for work, the `para-status` skill for current state, or the `para-help` skill for invocation help.

If `references/context-schema.md` is not available in this install, fresh context requires active_context and completed_summaries string arrays and last_updated as an ISO timestamp. Preserve all optional/unknown existing fields, including research_docs, execution, phased_execution and workflow. Initialization does not infer completion or reset execution evidence.
