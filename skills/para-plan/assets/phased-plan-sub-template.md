# Phase {PHASE_ID}: {PHASE_NAME}

> **Parent plan:** `{DATE}-{TASK_NAME}.md`
> **Estimated time:** {ESTIMATED_TIME}
> **Prerequisite:** {PREREQUISITES_OR_NONE}
> **Outcome:** {ONE_SENTENCE_DESCRIBING_WHAT_IS_TRUE_WHEN_DONE}

---

## Objective

[Clear, specific statement of what this phase accomplishes. Should be independently valuable and testable.]

---

## Key Context from Master Plan

[Copy (not reference) the specific decisions, principles, and contracts that are needed for this phase. The test: "Could someone execute this sub-plan without reading the master plan?"]

**Relevant principles:**
- [Principle from master plan that applies to this phase]
- [Principle from master plan that applies to this phase]

**Relevant architecture decisions:**
- [Decision]: [Choice] -- [brief rationale]
- [Decision]: [Choice] -- [brief rationale]

**Contracts this phase implements or depends on:**
```
[Interface definitions, API shapes, or message schemas needed for this phase]
```

---

## Scope

### In Scope

- [Item 1]
- [Item 2]

### Out of Scope

- [Item 1 -- which phase handles it]
- [Item 2 -- which phase handles it]

---

## Implementation Steps

> Each checklist item below maps to one git commit. The checkbox text is the commit message.
> Tests come BEFORE the implementation they cover (TDD).

- [ ] **Implement {behavior} with its regression coverage**
  - **Files:** `path/to/component`, `path/to/test`
  - **Contract:** [Existing contract or changed interface]
  - **Tests:** [Command, intended failing assertion, success condition]
  - Write/observe the regression first, implement, pass required checks, then commit.

- [ ] **Integrate {behavior} and validate acceptance**
  - **Tests:** [Specific integration/acceptance assertions and commands]
  - All required checks pass before this commit; record future coverage as pending work.

---

## Phase-Specific Risks

- **Risk 1:** [Description]
  - *Mitigation:* [How to handle]

- **Risk 2:** [Description]
  - *Mitigation:* [How to handle]

---

## Green Tests After This Phase

- {STATUS} {Test suite 1} — [brief description]
- {STATUS} {Test suite 2} — [brief description]
- {STATUS} {Test suite 3} — [brief description]
- {STATUS} E2E acceptance test — [required passing coverage or future work not yet introduced]

[Required suites pass. Describe future coverage separately; do not merge failing required tests.]

---

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `path/to/new/file.ext` | Create | [What it does] |
| `path/to/new/file_test.ext` | Create | [What it tests] |
| `path/to/existing/file.ext` | Modify | [What changes and why] |

---

**Next Step:** Once reviewed and approved, use the `para-execute` skill with `--phase={PHASE_ID}` to begin implementation.
