# Changelog

All notable changes to this project will be documented in this file.

## [3.0.0-alpha.1] - 2026-05-01

### Breaking Changes
- **Directory renames**: All skill directories renamed from `skills/<name>/` to `skills/para-<name>/`
  to satisfy the Agent Skills open standard requirement that `name == basename(dir)`.
  Update any hardcoded skill paths in install scripts or CI configuration.
- **Template relocation**: All template files moved from top-level `templates/` into each
  owning skill's `assets/` subdirectory. SKILL.md body references updated accordingly.
  - `templates/context-template.md` → `skills/para-init/assets/context-template.md`
  - `templates/agents-basic-template.md` → `skills/para-init/assets/agents-basic-template.md`
  - `templates/agents-full-template.md` → `skills/para-init/assets/agents-full-template.md`
  - `templates/plan-template.md` → `skills/para-plan/assets/plan-template.md`
  - `templates/phased-plan-master-template.md` → `skills/para-plan/assets/phased-plan-master-template.md`
  - `templates/phased-plan-sub-template.md` → `skills/para-plan/assets/phased-plan-sub-template.md`
  - `templates/research-template.md` → `skills/para-research/assets/research-template.md`
  - `templates/summary-template.md` → `skills/para-summarize/assets/summary-template.md`

### Added
- `scripts/validate-skills.sh` — conformance validator (runs `tests/conformance/run_all.sh`)
- `tests/conformance/` — conformance test suite (name regex, dir matching, description bounds, body size, reference resolution)
- `docs/METHODOLOGY.md` — stub; full content in v3.0.0 release
- `tests/e2e/multi-client-layout-compat.sh` — E2E stub (exits 1 until phase 7 implements)

## [2.0.0] - 2026-04-07

### Added
- New skill: `para-research` — deep codebase exploration before planning
- New skill: `para-review` — Staff+ FAANG engineer review loops for plans and PRs
- New skill: `para-workflow` — multi-phase orchestration (execute → PR → review → summarize → merge)
- New template: `research-template.md` for research output documents

### Changed
- `para-plan` skill: added 2-3 round self-review loop, Core Principles, Architecture Decisions table, Interface Boundaries, Graceful Degradation, Observability, Stubs, checklist-as-commit rule, `/para-review --plan` suggestion
- `para-execute` skill: added explicit checkbox text extraction, RED/GREEN TDD stages, commit message from checkbox text, `/para-review --pr` suggestion
- `para-help` skill: updated workflow diagram, added all 11 skills to table
- `plan-template.md`: v2 structure with Core Principles, Architecture Decisions, Interface Boundaries, Graceful Degradation, Contract Tests
- `phased-plan-master-template.md`: v2 structure with Core Principles, Responsibility Split, Progressive Regression Rule, New Components, Security Model
- `phased-plan-sub-template.md`: v2 structure with Key Context from Master Plan, checklist-as-commit items, Green Tests After This Phase
- `context-template.md`: added `research_docs` array
- `resources/AGENTS.md`: v2 workflow loop with Research, Review Plan, Review PR steps
- `README.md`: updated to 11 skills with v2 workflow
- Bumped version from 1.0.0 to 2.0.0

## [1.0.0] - 2026-04-07

### Added
- Remaining skills: `para-summarize`, `para-archive`, `para-check`, `para-help`
- `.mcp.json` with repo-search MCP server config
- `INSTALL.md` with detailed Codex-specific installation instructions
- `scripts/install.sh` marketplace-entry registration helper (requires `jq`)
- `docs/` with phased plans quick reference, example, and changelog
- `examples/example-workflow.md` adapted for Codex

### Changed
- Bumped version from 0.1.0 to 1.0.0 (full feature parity)
- Updated README to remove v1.0.0 markers on skills
- Updated AGENTS.md project structure with new directories

## [0.1.0] - 2026-04-07

### Added
- Initial project scaffold with Codex plugin manifest
- Core skills: `para-init`, `para-plan`, `para-execute`, `para-status`
- 7 templates adapted from Claude version (plan, phased-plan-master, phased-plan-sub, summary, context, agents-basic, agents-full)
- `resources/AGENTS.md` global workflow methodology
- `examples/marketplace-entry.json` for plugin discovery
- Project `AGENTS.md`, `README.md`, `LICENSE`, `CHANGELOG.md`

### Adapted From
- [para-programming-plugin v1.6.2](https://github.com/brian-lai/para-programming-plugin) for Claude Code
- Key naming changes: CLAUDE.md → AGENTS.md, /para:command → /para-command
