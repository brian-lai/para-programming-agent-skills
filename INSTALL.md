# Installation Guide

This repository is a portable Agent Skills package. The canonical skill payload is the `skills/` directory plus the shared docs/resources used by those skills.

## Support Matrix

| Client | Out-of-box support | Notes |
|--------|--------------------|-------|
| OpenAI Codex | Yes | `scripts/install.sh` installs to `~/.agents/skills`, mirrors to `~/.codex/skills`, and registers the plugin marketplace entry. |
| Gemini CLI | Yes | Gemini discovers `~/.agents/skills`, so the Codex installer also installs the Gemini-compatible user skill path. |
| Pi | Yes | Pi discovers `~/.agents/skills`, so the Codex installer also installs the Pi-compatible user skill path. |
| OpenCode | Yes | OpenCode discovers `~/.agents/skills`, so the Codex installer also installs the OpenCode-compatible user skill path. |
| Cursor | Yes | Cursor discovers Agent Skills from shared `.agents/skills` locations and Cursor-specific `.cursor/skills` locations; the installer writes the shared global path. |
| Claude Code | No | Use the original Claude plugin instead: `https://github.com/brian-lai/para-programming-plugin`. |

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

OpenCode discovers user skills from `~/.agents/skills`, so the Codex installer provides out-of-box OpenCode support.

1. Run the same installer:

   ```bash
   ./scripts/install.sh
   ```

2. Start OpenCode from any project. OpenCode exposes discovered skills to agents through its native `skill` tool.

3. Optional project-local install: copy or symlink this repository's `skills/` tree into `.agents/skills/` or `.opencode/skills/` in a project.

## Cursor

Cursor supports Agent Skills in the editor and CLI. The installer writes the shared global `~/.agents/skills` path, which Cursor-compatible Agent Skills tooling can discover. Cursor also supports Cursor-specific skill directories such as `.cursor/skills/` for project-level skills and `~/.cursor/skills/` for user-level skills.

1. Run the same installer:

   ```bash
   ./scripts/install.sh
   ```

2. Restart Cursor. Skills can be auto-selected by the agent or invoked from the slash command menu, for example:

   ```text
   /para-init
   ```

3. If your Cursor version does not discover the shared global path, mirror the installed skills into Cursor's user-level skill directory:

   ```bash
   mkdir -p ~/.cursor/skills
   cp -R ~/.agents/skills/para-* ~/.cursor/skills/
   ```

## Manual Acceptance Checklist

Before publishing or cutting a release, verify these flows manually:

- Claude Code: users are directed to `https://github.com/brian-lai/para-programming-plugin`.
- OpenAI Codex: `scripts/install.sh` installs `para-*` skills into `~/.agents/skills`, and `$para-init` is selectable via `/skills` or direct `$para-init` mention.
- Gemini CLI: `gemini skills list --all` discovers the installed `para-*` skills from `~/.agents/skills`.
- Pi: Pi discovers the installed `para-*` skills from `~/.agents/skills`; `/skill:para-init` works when skill commands are enabled.
- OpenCode: OpenCode discovers installed `para-*` skills from `~/.agents/skills` and exposes them through its native `skill` tool.
- Cursor: Cursor discovers installed `para-*` skills from the shared `~/.agents/skills` path or from a fallback `~/.cursor/skills` mirror, and exposes them through the slash command menu.
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
