# Phased Plans: Quick Reference

## When to Use Phased Plans

Create a phased plan when ANY of these apply:

**Architectural Boundaries**
- Work spans database → API → frontend
- Multiple services/microservices affected
- Infrastructure changes before application code
- Migration work precedes feature work

**Size & Complexity**
- More than 5-10 files affected
- Multiple major components to build
- Can break into independently testable units
- Each phase could be code reviewed separately

**Dependencies**
- Later work depends on earlier foundation
- Database migrations before code changes
- API contracts before client implementation
- Configuration/setup before features

**Review Benefits**
- Phases make code review manageable
- Each phase delivers incremental value
- Different team members can review phases
- Risk reduced by deploying in stages

---

## Command Comparison

### Simple Plan

| Step | Command | Output |
|------|---------|--------|
| Plan | `/para-plan task-name` | `context/plans/YYYY-MM-DD-task-name.md` |
| Execute | `/para-execute` | Worktree: `.para-worktrees/task-name`, Branch: `para/task-name` |
| Summarize | `/para-summarize` | `context/summaries/YYYY-MM-DD-task-name-summary.md` |
| Archive | `/para-archive` | Moves context to archives |

### Phased Plan

| Step | Command | Output |
|------|---------|--------|
| Plan | `/para-plan task-name` | Master + N phase plans |
| Review | (Manual) | Review all phases |
| Execute Phase 1 | `/para-execute --phase=1` | Worktree: `.para-worktrees/task-name-phase-1`, Branch: `para/task-name-phase-1` |
| Summarize Phase 1 | `/para-summarize --phase=1` | Phase 1 summary |
| Merge Phase 1 | `gh pr create` + merge | Phase 1 in main |
| Execute Phase 2 | `/para-execute --phase=2` | Worktree: `.para-worktrees/task-name-phase-2`, Branch: `para/task-name-phase-2` |
| ... | (Repeat for each phase) | ... |
| Archive | `/para-archive` | After all phases complete |

---

## Phase Status Flow

```
pending → in_progress → completed
```

- **pending**: Phase planned but not started
- **in_progress**: Phase currently being executed
- **completed**: Phase summarized and merged

---

## Common Phasing Patterns

### 1. Full-Stack Feature (Layer-Based)

```
Phase 1: Database Schema
Phase 2: API/Backend
Phase 3: Frontend
```

### 2. Refactoring (Strangler Pattern)

```
Phase 1: Add New System (alongside old)
Phase 2: Migrate Existing Usage
Phase 3: Remove Old System
```

### 3. Data Migration (Zero-Downtime)

```
Phase 1: Dual-Write (new + old)
Phase 2: Backfill Existing Data
Phase 3: Read Switch (use new)
Phase 4: Cleanup (remove old)
```

### 4. Feature with Infrastructure

```
Phase 1: Infrastructure Setup
Phase 2: Core Feature
Phase 3: Integration & Testing
```

### 5. Service Decomposition

```
Phase 1: Extract Service Code
Phase 2: Deploy as Separate Service
Phase 3: Update Clients
Phase 4: Remove from Monolith
```

---

## Tips & Best Practices

### Planning
- Each phase should deliver **independent value**
- Keep phases **similar in size** (2-8 files each)
- Make dependencies **explicit** in master plan
- Define **success criteria** per phase

### Execution
- Always start from `main` for each phase
- Ensure previous phases are **merged** first
- Test each phase **independently**
- Commit **incrementally** within phases

---

## Quick Decision Tree

```
Is it >5-10 files? → Multiple layers? → Has dependencies? → Benefits from incremental review?
If YES to 2+: USE PHASED PLAN
If NO to most: USE SIMPLE PLAN
```

---

## See Also

- [Complete Phased Plan Example](./phased-plan-example.md)
