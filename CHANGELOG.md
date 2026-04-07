# Changelog

All notable changes to this project will be documented in this file.

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
