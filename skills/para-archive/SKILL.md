---
name: para-archive
description: Archive the current context to create a clean slate for the next task. Removes worktrees, resets context/context.md, preserves summaries.
model: haiku
effort: low
---

Archive the current context to create a clean slate for the next task.

## Usage

```
/para-archive
/para-archive --fresh          # Completely empty context
/para-archive --seed           # Carry forward relevant context
```

Default: create fresh context with references to completed summaries.

## What It Does

1. Read `context/context.md` and extract worktree metadata, including top-level `worktree_path` and per-phase worktree paths.
2. Verify work is complete:
   - Summary exists in `context/summaries/`
   - Tests have passed
   - Branch has been pushed and PR created or merged
3. **Clean up worktrees:**
   - For each worktree path found in metadata, run `git worktree remove {worktree_path}`
   - If the worktree has uncommitted changes, warn the user and require them to commit or stash first, then re-run `/para-archive`; do NOT force-remove because that can permanently destroy uncommitted work
   - After removal, run `git worktree prune` to clean up stale references
   - Remove `.para-worktrees/` if empty
4. Move `context/context.md` to `context/archives/YYYY-MM-DD-HHMM-context.md`
5. Create a fresh `context/context.md` seeded from `../para-init/assets/context-template.md`
6. Carry forward completed summary references unless `--fresh` was specified
7. Display archive location, worktrees removed, fresh context confirmation, and readiness for the next task

See `../para-init/references/context-schema.md` for the full context metadata field reference.

If ../para-init/references/context-schema.md is not available in this install, the minimal fields needed are: `active_context` (string[]), `completed_summaries` (string[]), `research_docs` (string[]), `worktree_path` (string or null), and `last_updated` (ISO 8601 string).

## Fresh vs Seeded Context

### `--fresh`

Create a clean context with no carryover references. Use this when all current work is complete and no summaries need to stay active.

### `--seed`

Create a clean context from `../para-init/assets/context-template.md`, then seed it with references to completed summaries and any still-relevant research docs.

## When to Archive

- Work is complete and summarized
- All tests pass and changes are committed
- Branch has been pushed and PR created or merged
- Ready to start a new, unrelated task

Do NOT archive if work is still in progress or you need the current context for continued work.

## Recovery

```bash
ls -lt context/archives/
cp context/archives/2025-11-24-1430-context.md context/context.md
```

To restore a worktree after archive if the branch still exists:

```bash
git worktree add .para-worktrees/{task-name} para/{task-name}
```

## Notes

- Never delete archives; they are project memory
- Archives are searchable: `grep -r "keyword" context/archives/`
- Worktree cleanup is automatic during archive; branches are preserved for PR and merge workflows
