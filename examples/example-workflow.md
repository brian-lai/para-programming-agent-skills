# Example PARA-Programming Workflow

This example walks through a complete PARA workflow for adding user authentication to a web API.

---

## Starting Point

You have a web API project that needs authentication added. You're using Codex with the PARA-Programming plugin installed.

---

## Step 1: Check Current Status

```
/para-status
```

**Output:**
```
PARA Status

Current Work:
   No active context

Next Action:
   Run /para-init to set up PARA structure (if not done)
   Or run /para-plan to start a new task
```

---

## Step 2: Verify Workflow Needed

```
/para-check "Add JWT-based user authentication to the API"
```

**Output:**
```
PARA Workflow Check

Request: "Add JWT-based user authentication to the API"

  USE PARA WORKFLOW

Reason: This request requires code changes and file modifications.
Next: Run /para-plan to create an implementation plan.
```

---

## Step 3: Create a Plan

```
/para-plan add-jwt-authentication
```

The agent creates: `context/plans/2025-11-24-add-jwt-authentication.md`

The agent asks clarifying questions, explores the codebase, then creates a structured plan with implementation steps and test annotations.

---

## Step 4: Human Review

You review the plan and provide feedback. The agent updates the plan accordingly.

---

## Step 5: Execution

```
/para-execute
```

The agent:
1. Creates an isolated worktree in `.para-worktrees/add-jwt-authentication`
2. Works through each todo item following TDD (tests first, then implementation)
3. Commits after each completed todo
4. Updates `context/context.md` progress tracking

---

## Step 6: Generate Summary

```
/para-summarize
```

The agent analyzes git changes and creates: `context/summaries/2025-11-24-add-jwt-authentication-summary.md`

---

## Step 7: Archive and Clean Up

```
/para-archive
```

The agent:
- Removes the worktree
- Archives `context/context.md`
- Creates a fresh context for the next task

---

## Key Takeaways

1. **Every code change starts with a plan** — `/para-plan`
2. **Always get human review** — Before execution
3. **Document everything** — `/para-summarize` captures learnings
4. **Clean up when done** — `/para-archive` maintains clean context
5. **Stay oriented** — `/para-status` shows where you are
