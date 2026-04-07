# Changelog

All notable changes to this project will be documented in this file.

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
