# Installation Guide

This repository is a portable Agent Skills package. The canonical skill payload is the `skills/` directory plus the shared docs/resources used by those skills.

## Support Matrix

| Client | Out-of-box support | Notes |
|--------|--------------------|-------|
| OpenAI Codex | Yes | `scripts/install.sh` installs to `~/.agents/skills`, mirrors to `~/.codex/skills`, and registers the plugin marketplace entry. |
| Gemini CLI | Yes | Gemini discovers `~/.agents/skills`, so the Codex installer also installs the Gemini-compatible user skill path. |
| Pi | Yes | Pi discovers `~/.agents/skills`, so the Codex installer also installs the Pi-compatible user skill path. |
| Claude Code | No | Use the original Claude plugin instead: `https://github.com/brian-lai/para-programming-plugin`. |
| OpenCode | Manual/experimental | Copy or symlink `skills/` into the OpenCode skills path configured on your machine. |
| Cursor | Manual/experimental | Copy or symlink `skills/` into the Cursor Agent Skills path configured on your machine. |

## Claude Code

Claude users should use the original PARA-Programming Claude plugin:

```text
https://github.com/brian-lai/para-programming-plugin
```

This repository includes Claude-compatible metadata for portability experiments, but `scripts/install.sh` does not install into Claude Code's `~/.claude/skills` path and does not replace the original Claude plugin.

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

## Gemini

Gemini CLI discovers user skills from `~/.agents/skills`, so the Codex installer provides out-of-box Gemini support.

1. Run the same installer:

   ```bash
   ./scripts/install.sh
   ```

2. In Gemini, verify discovery:

   ```bash
   gemini skills list --all
   ```

## Pi

Pi discovers user skills from `~/.agents/skills`, so the Codex installer provides out-of-box Pi support.

1. Run the same installer:

   ```bash
   ./scripts/install.sh
   ```

2. In Pi, verify skill discovery. If Pi skill commands are enabled, skills can be invoked as:

   ```text
   /skill:para-init
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

## Manual Acceptance Checklist

Before publishing or cutting a release, verify these flows manually:

- Claude Code: users are directed to `https://github.com/brian-lai/para-programming-plugin`.
- OpenAI Codex: `scripts/install.sh` installs `para-*` skills into `~/.agents/skills`, and `$para-init` is selectable via `/skills` or direct `$para-init` mention.
- Gemini CLI: `gemini skills list --all` discovers the installed `para-*` skills from `~/.agents/skills`.
- Pi: Pi discovers the installed `para-*` skills from `~/.agents/skills`; `/skill:para-init` works when skill commands are enabled.
- OpenCode: copying `skills/` preserves every `SKILL.md` and asset/reference path used by the skills.
- Cursor: the skills directory is discoverable and the `$para-*` invocation names are shown consistently.
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
