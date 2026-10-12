# Phased plans quick reference

Use the `para-plan` skill to define independently mergeable outcomes and dependencies. Each sub-plan contains the facts and validation needed for its phase. Use the `para-review` skill with `--plan` before execution.

Use the `para-workflow` skill to run the lifecycle; `--auto` authorizes merge and phase progression while retaining review/check gates. The workflow must invoke and verify phase cleanup before advancing, then archive completed plans/context and verify all task worktrees before reporting completion. `--phase=N` resumes a selected phase only after predecessor merges are included in its base. Simple plans use the same orchestrator without phase metadata.

Phase cleanup uses the `para-archive` skill with `--phase=N`; verify that phase's recorded worktree is absent before advancing. One final archive follows all merged/summarized phases and moves the completed plan files into the archive. A summary alone does not complete a phase or workflow.

See the [worked example](phased-plan-example.md) and [context contract](../skills/para-init/references/context-schema.md) for evidence and recovery.
