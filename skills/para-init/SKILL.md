---
name: para-init
description: Initialize PARA-Programming structure in the current project. Use when setting up a new repo for PARA workflow, creating context/ directory, or bootstrapping AGENTS.md.
model: haiku
effort: low
---

Initialize PARA-Programming structure in the current project.

## Usage

```
/para-init
/para-init --template=basic    # Minimal project AGENTS.md (default)
/para-init --template=full     # Comprehensive project AGENTS.md
```

## What It Does

1. **Set up global methodology file** at `~/.agents/AGENTS.md` (copied from `resources/AGENTS.md` if missing; never overwrites existing).
2. **Create context directory structure:**
   ```bash
   mkdir -p context/{data,plans,summaries,archives,servers}
   ```
3. **Create `context/context.md`** seeded from `assets/context-template.md`:
   ````markdown
   # Current Work Summary

   Ready to start first task.

   ---
   ```json
   {
     "active_context": [],
     "completed_summaries": [],
     "last_updated": "TIMESTAMP"
   }
   ```
   ````
   See `references/context-schema.md` for the full field reference.
4. **Create project `AGENTS.md`** (if missing) from `assets/agents-basic-template.md` (default, `--template=basic`) or `assets/agents-full-template.md` (`--template=full`).
5. **Update `.gitignore`** to include `.para-worktrees/`:
   - If `.gitignore` exists, check for `.para-worktrees/` entry; append if missing.
   - If `.gitignore` does not exist, create it with `.para-worktrees/` as its content.
   - This prevents worktree directories from being tracked by git.

## Graceful Degradation (partial-install fallback)

If `references/context-schema.md` is not available in this install (single-skill copy without the bundled resource), the minimal context.md JSON schema is:

```json
{
  "active_context": ["path/to/plan.md"],
  "research_docs": [],
  "completed_summaries": [],
  "last_updated": "ISO-8601"
}
```

Required fields: `active_context` (string[]), `completed_summaries` (string[]), `last_updated` (ISO 8601 string). Optional extensions (`phased_execution`, `workflow`, `worktree_path`, `execution_branch`) are documented in the full schema.

## Success Output

After initialization, display:

```
PARA-Programming Structure Initialized

context/
├── archives/     # Historical context snapshots
├── data/         # Input files, payloads, datasets
├── plans/        # Pre-work planning documents
├── servers/      # MCP tool wrappers
├── summaries/    # Post-work reports
└── context.md    # Active session context

.para-worktrees/  # Git worktree isolation (gitignored)

Files created/updated:
- ~/.agents/AGENTS.md (global methodology, if it didn't exist)
- context/context.md (fresh context file)
- AGENTS.md (project-specific context, if it didn't exist)
- .gitignore (added .para-worktrees/ entry)

Next steps:
1. Edit AGENTS.md with your project-specific context
2. Create your first plan: /para-plan <task-description>
3. Check status: /para-status
4. Get help: /para-help
```
