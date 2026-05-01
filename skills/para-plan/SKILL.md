---
name: para-plan
description: Create a planning document through collaborative dialogue, with support for multi-phase plans.
---

# Skill: plan

Create a planning document through collaborative dialogue, with support for multi-phase plans.

## Usage

```
/para-plan [task-description]
```

If no task description is provided, ask for one.

## Collaborative Planning Process

**Planning is a dialogue, not a one-shot generation.**

When `/para-plan` is invoked:

1. **Identify ambiguities** in the task description -- scope, approach, constraints, preferences.

2. **Ask 1-4 clarifying questions** before doing anything else:
   - Present options with trade-offs clearly explained
   - Reference existing codebase patterns when relevant ("I see you use X elsewhere, should we follow that?")
   - Skip only if ALL of these are true: task is very narrow, only one reasonable approach exists, no risk of breaking changes, user gave extremely detailed requirements.

3. **Check for research doc.** If a research document exists (`context/data/YYYY-MM-DD-task-name-research.md`), use it as primary input for steps 4-6. If no research doc exists for a non-trivial task, suggest running `/para-research` first.

4. **Explore the codebase** with clarifications in hand -- identify:
   - Existing patterns, conventions, and affected components
   - Complexity and existing test patterns (test framework, test file locations, naming conventions)
   - **Interface boundaries between systems** (APIs, message formats, shared types, database schemas used across modules)
   - **Existing graceful degradation patterns** (how the codebase currently handles external dependency failures, timeouts, retries)

5. **Draft spec + stubs:**
   - Create a spec file in `context/data/YYYY-MM-DD-task-name-spec.yaml` (OpenAPI/Swagger YAML for HTTP APIs; TypeScript interface file or markdown contract for UI components, modules, and scripts)
   - Create stub source files in the project tree with signatures matching the spec but no implementation (return `null`, `{}`, or `501 Not Implemented` as appropriate)
   - Reference the spec and stub file paths in the plan

6. **Determine plan type:**
   - **Simple plan** (single file) for straightforward tasks
   - **Phased plan** (master + sub-plans) when work spans >5-10 files, crosses architectural boundaries, or has natural dependency ordering
   - If proposing a phased plan, confirm with the user first.

7. **Draft the plan** applying Staff+ engineering criteria:
   - **Think about what NOT to build.** Explicitly state what is deferred or out of scope and why.
   - **Identify interface boundaries.** Every boundary between systems, modules, or layers needs a defined contract.
   - **Address graceful degradation.** For every external dependency, document what happens when it fails.
   - **Include observability.** Specify what gets logged, what gets metered/monitored, and what alerts should fire.
   - **Document architecture decisions as a table:** Decision | Choice | Rationale | Alternatives Rejected.
   - **Concrete test annotations on every implementation step.** Each step must have a `Tests:` annotation with specific function signatures, test case names, and key assertions.
   - **Checklist = commit.** Every implementation step MUST be written as a checkbox item (`- [ ] ...`) where the text serves as the git commit message.

8. **Self-review loop (2-3 rounds).** Before presenting the plan to the user, re-read the entire plan and revise it. This is NOT optional for any plan that spans more than 2-3 files.

   **Round 1 -- Correctness & Completeness:**
   - Are there technical bugs in the approach?
   - Are any interface boundaries missing their contract definition?
   - Is anything over-engineered or under-engineered?
   - Are all file paths accurate and consistent across the plan?

   **Round 2 -- Testing & TDD:**
   - Do tests come BEFORE implementation in the ordering?
   - Is there a contract test suite for every interface boundary?
   - Is there an E2E acceptance test defined on day 1 (even if it stays red)?
   - Are test annotations concrete (function signatures, test names) rather than vague?

   **Round 3 (conditional):** Run ONLY if Rounds 1 and 2 together produced more than 3 substantive changes.

   **Convergence rule:** Stop self-review when a round produces fewer than 3 substantive edits.

9. **Present the plan** to the user for review. Note how many self-review rounds were completed.

10. **After the plan is written**, ask the user if they'd like to proceed. Offer options like:
    - "Run `/para-review --plan` for Staff+ review" -- independent reviewer before execution
    - "Yes, run `/para-execute`" -- proceed directly to implementation
    - "I'd like to make adjustments first" -- continue refining the plan
    For phased plans, reference `/para-execute --phase=1` to start with the first phase.

## Plan Structure

### Simple Plan

File: `context/plans/YYYY-MM-DD-task-name.md`

Sections:
- **Objective** -- what needs to be done
- **Core Principles** -- 3-6 engineering principles guiding the implementation
- **Spec** -- path to spec file and what it covers
- **Stubs** -- list of stub source files to be created
- **Architecture Decisions** -- table: Decision | Choice | Rationale | Alternatives Rejected
- **Interface Boundaries** -- every cross-system boundary with its contract
- **Graceful Degradation** -- table: Failure Scenario | Expected Behavior
- **Implementation Steps** -- checklist items (`- [ ] ...`) where each item is a commit message, with per-step `Tests:` annotations
- **Risks** -- potential issues and edge cases
- **Success Criteria** -- measurable outcomes
- **Testing Strategy** -- Contract Tests (written FIRST), Unit Tests, Integration Tests, Acceptance Test

### Phased Plan

Files:
- `context/plans/YYYY-MM-DD-task-name.md` (master plan: architecture-only reference with core principles, architecture decisions, responsibility split, graceful degradation, progressive regression rule)
- `context/plans/YYYY-MM-DD-task-name-phase-1.md` (self-contained implementation-ready sub-plan with TDD ordering)
- `context/plans/YYYY-MM-DD-task-name-phase-2.md`
- etc.

The master plan should be concise (1-3 pages) and never contain implementation steps. Each sub-plan should be independently executable.

Each phase should be independently reviewable and mergeable.

## Context Update

After creating the plan, update `context/context.md`:
- Add plan file(s) to `active_context` array
- For phased plans, add `phased_execution` metadata with phase status tracking:
  ```json
  {
    "phased_execution": {
      "master_plan": "context/plans/YYYY-MM-DD-task-name.md",
      "phases": [
        { "phase": 1, "plan": "context/plans/YYYY-MM-DD-task-name-phase-1.md", "status": "pending", "branch": null, "worktree_path": null },
        { "phase": 2, "plan": "context/plans/YYYY-MM-DD-task-name-phase-2.md", "status": "pending", "branch": null, "worktree_path": null }
      ],
      "current_phase": null
    }
  }
  ```
- Update `last_updated` timestamp

## Notes

- All project work MUST start with a plan (per PARA workflow)
- Master plans should be concise (1-3 pages); sub-plans should be self-contained and implementation-ready
- Don't ask questions you could answer by reading the codebase
- Bias towards 2-4 focused questions, not 10+ scattered ones
- Complex plans undergo 2-3 automatic self-review rounds before being presented for human review
