# Phased Plan Example: Complete Walkthrough

This document demonstrates a complete phased plan workflow from start to finish.

---

## Scenario

**Task:** Implement user authentication system with JWT tokens, including database schema, API layer, and frontend.

**Why phased?**
- Spans multiple architectural layers (database → API → frontend)
- Database migrations must run before API implementation
- API must be complete before frontend can integrate
- Each phase can be code reviewed and merged independently

---

## Step 1: Plan Creation

```bash
/para-plan implement-user-authentication
```

The agent analyzes the task, identifies 15+ files across DB, API, and frontend layers, and recommends 3 phases:

- Phase 1: Database Schema & Migrations
- Phase 2: API Layer (Auth Service, Middleware, Endpoints)
- Phase 3: Frontend Integration (Login UI, Auth Context, Protected Routes)

### Files Created

```
context/plans/2025-12-18-implement-user-authentication.md               (Master)
context/plans/2025-12-18-implement-user-authentication-phase-1.md       (Database)
context/plans/2025-12-18-implement-user-authentication-phase-2.md       (API)
context/plans/2025-12-18-implement-user-authentication-phase-3.md       (Frontend)
```

---

## Step 2: Review

User reviews all 4 plan files (master + 3 phases) and approves the approach.

---

## Step 3: Execute Phase 1

```bash
/para-execute --phase=1
```

1. Creates worktree: `.para-worktrees/implement-user-authentication-phase-1`
2. Branch: `para/implement-user-authentication-phase-1`
3. Extracts todos from phase 1 plan
4. Implements each todo with TDD cycle, commits after each

---

## Step 4: Summarize Phase 1

```bash
/para-summarize --phase=1
```

Creates: `context/summaries/2025-12-18-implement-user-authentication-phase-1-summary.md`

---

## Step 5: Merge Phase 1

Push branch, create PR, review, merge to main.

---

## Step 6: Execute Phase 2

```bash
/para-execute --phase=2
```

Creates new worktree from updated main (with Phase 1 merged). Repeat the implement → summarize → merge cycle.

---

## Step 7: Continue for Remaining Phases

Repeat for Phase 3. Each phase starts from main with all previous phases merged.

---

## Step 8: Final Archive

```bash
/para-archive
```

Removes all worktrees, archives context, creates fresh context.md.

---

## Benefits Demonstrated

- **Code Review:** 3 focused PRs instead of one 15+ file PR
- **Deployment:** Incremental deployment reduces risk
- **Testing:** Each phase independently tested
- **Collaboration:** Clear handoff points between phases
