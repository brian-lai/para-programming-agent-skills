# Installation Guide

This repository is a portable Agent Skills package. The canonical skill payload is the `skills/` directory plus the shared docs/resources used by those skills.

## Claude Code

Claude-compatible package metadata lives in `.claude-plugin/`.

1. Clone this repository:

   ```bash
   git clone https://github.com/brian-lai/para-programming-agent-skills.git ~/para-programming-agent-skills
   ```

2. Register the marketplace entry from `.claude-plugin/marketplace.json`, or point your Claude Code plugin configuration at this checkout.

3. Restart Claude Code and verify the PARA skills are visible.

## OpenAI Codex

Codex reads local user skills from `~/.agents/skills`. The installer copies this package's `skills/` tree there, mirrors it into `~/.codex/skills` for older local runtimes, installs supporting docs, and registers the plugin marketplace entry.

1. Clone this repository:

   ```bash
   git clone https://github.com/brian-lai/para-programming-agent-skills.git ~/.codex/plugins/para-programming
   ```

2. Install the skills:

   ```bash
   ~/.codex/plugins/para-programming/scripts/install.sh
   ```

3. Restart Codex and mention the skill, or run `/skills` and select it:

   ```text
   $para-init
   ```

Preview the Codex install without writes:

```bash
./scripts/install.sh --dry-run
```

## OpenCode

Use the open-standard skill layout directly.

1. Clone this repository:

   ```bash
   git clone https://github.com/brian-lai/para-programming-agent-skills.git ~/.opencode/para-programming-agent-skills
   ```

2. Copy or symlink `skills/` into the OpenCode skills location configured on your machine.

3. Keep `docs/` and `resources/` beside the package when possible so cross-skill references and methodology docs remain available.

## Cursor

Cursor can consume the same `skills/` layout when configured for Agent Skills.

1. Clone this repository:

   ```bash
   git clone https://github.com/brian-lai/para-programming-agent-skills.git ~/.cursor/para-programming-agent-skills
   ```

2. Copy or symlink `skills/` into the Cursor Agent Skills directory used by your environment.

3. Restart Cursor and confirm the `$para-*` skills are discoverable in the agent session.

## Gemini

Gemini CLI can use the portable skill directories when its local Agent Skills path is enabled.

1. Clone this repository:

   ```bash
   git clone https://github.com/brian-lai/para-programming-agent-skills.git ~/.gemini/para-programming-agent-skills
   ```

2. Copy or symlink `skills/` into the Gemini CLI skills directory configured on your machine.

3. Start a new Gemini CLI session and verify the `para-*` skills are available.

## Manual Acceptance Checklist

Before publishing or cutting a release, verify these flows manually:

- Claude Code: plugin metadata loads from `.claude-plugin/plugin.json` and the `para-skills` package appears.
- OpenAI Codex: `scripts/install.sh` installs `para-*` skills into `~/.agents/skills`, and `$para-init` is selectable via `/skills` or direct `$para-init` mention.
- OpenCode: copying `skills/` preserves every `SKILL.md` and asset/reference path used by the skills.
- Cursor: the skills directory is discoverable and the `$para-*` invocation names are shown consistently.
- Gemini: each `para-*` skill can be installed independently or as a full `skills/` tree.
- Single-skill installs: any skill that references a sibling skill includes a graceful fallback phrase.
- Full-tree installs: `docs/` is present beside `skills/` when using `para-help` methodology links.

## Troubleshooting

### Skills Not Available

- Restart the client after changing plugin or skill paths.
- Verify each copied skill directory contains `SKILL.md`.
- Confirm each `SKILL.md` frontmatter `name` matches the directory basename.

### Codex Registration Failed

- Install `jq` if running `scripts/install.sh` without `--dry-run`.
- Check that `~/.agents/plugins/marketplace.json` is valid JSON.
- Re-run `./scripts/install.sh --dry-run` to inspect the intended marketplace path.
