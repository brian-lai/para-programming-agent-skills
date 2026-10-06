# Installation Guide

This repository is a portable Agent Skills package. The canonical skill payload is the `skills/` directory plus the shared docs/resources used by those skills.

## Support Matrix

| Client | Installer layout | Notes |
|--------|--------------------|-------|
| OpenAI Codex | Shared discovery path | `scripts/install.sh` links to `~/.agents/skills` and `~/.codex/skills`, and registers the plugin marketplace entry. |
| Gemini CLI | Shared discovery path | Gemini discovers `~/.agents/skills`, so the Codex installer also installs the Gemini-compatible user skill path. |
| Pi | Shared discovery path | Pi discovers `~/.agents/skills`, so the Codex installer also installs the Pi-compatible user skill path. |
| OpenCode | Shared discovery path | OpenCode discovers `~/.agents/skills`, so the Codex installer also installs the OpenCode-compatible user skill path. |
| Cursor | Shared discovery path | Cursor discovers Agent Skills from shared `.agents/skills` locations and Cursor-specific `.cursor/skills` locations; the installer writes the shared global path. |
| Claude Code | No | Use the original Claude plugin instead: `https://github.com/brian-lai/para-programming-plugin`. |

The matrix describes discovery paths. Automated tests check filesystem layout and update propagation, not native discovery in every client/version. Verify linked skills in your active client and reload or restart when needed.

## Client Invocation

The canonical request form is `para-<skill> [arguments]`. Use exact-name natural language whenever the host is unknown or does not expose a user-entered selector.

<!-- para-client-invocation-map:start -->
| Client | User-facing form |
|---|---|
| OpenAI Codex | `$para-<skill> [arguments]` |
| Cursor | `/para-<skill> [arguments]` |
| Pi, skill commands enabled | `/skill:para-<skill> [arguments]` |
| Pi, skill commands disabled | `natural-language` — `Use the para-<skill> skill <intent-and-arguments>.` |
| OpenCode | `natural-language` — `Use the para-<skill> skill <intent-and-arguments>.` |
| Gemini CLI | `natural-language` — `Use the para-<skill> skill <intent-and-arguments>.` |
| Unknown client | `natural-language` — `Use the para-<skill> skill <intent-and-arguments>.` |
<!-- para-client-invocation-map:end -->

## Management and discovery

Client skill managers and debug commands verify installation, list skills, or change enablement. They are not portable workflow invocation syntax.

## Claude Code

Claude users should use the original PARA-Programming Claude plugin:

```text
https://github.com/brian-lai/para-programming-plugin
```

This repository includes Claude-compatible metadata for portability experiments, but `scripts/install.sh` does not install into Claude Code's `~/.claude/skills` path and does not replace the original Claude plugin.

## OpenAI Codex

Codex reads local user skills from `~/.agents/skills`. The installer links each PARA skill directory there and into `~/.codex/skills` for older runtimes, links supporting docs/resources, and registers the permanent local source in the marketplace JSON. Requires Bash 3 or newer, Git and `jq`, including for dry runs.

1. Clone this repository to a permanent location (keep this checkout after installation):

   ```bash
   git clone https://github.com/brian-lai/para-programming-agent-skills.git ~/.codex/plugins/para-programming
   ```

2. Preview the migration, then install the links:

   ```bash
   ~/.codex/plugins/para-programming/scripts/install.sh --dry-run
   ~/.codex/plugins/para-programming/scripts/install.sh
   ```

3. Restart Codex and use the `para-init` skill. The client invocation mapping above shows Codex's explicit form.

Preview the Codex install without writes:

```bash
./scripts/install.sh --dry-run
```

## Link layout and existing installations

For each selected root `R` (default `~/.agents` and `~/.codex`):

```text
R/
├── skills/para-<name>  -> CHECKOUT/skills/para-<name>
├── docs/<entry>       -> CHECKOUT/docs/<entry>
├── resources/AGENTS.md -> CHECKOUT/resources/AGENTS.md
├── AGENTS.md          # existing user guidance, unchanged
└── para-install-backups/<dated-unique-run>/
    ├── manifest.jsonl
    └── <original-relative-path>
```

The installer owns individual entries, preserving other packages in shared directories. Existing copied skills/docs/resources and wrong or broken links are backed up before replacement. Unknown files within a replaced skill directory remain in its backup. Backups preserve link objects without traversing their targets, and stay outside skill discovery directories. Correct existing links are no-ops; repeated successful installs create no new backups.

`AGENTS_HOME` and `CODEX_HOME` override the roots. Symlinked config roots are supported, including `~/.codex` linked into another Git repository. Roots that resolve to the same location are installed once. Unsafe overlaps with source or payload paths are rejected before mutation. Review any resulting changes in your separate configuration repository; the installer never commits them.

Active global `AGENTS.md` files are preserved. The linked `resources/AGENTS.md` is a supporting template; `para-init` may copy it to missing global guidance, but never replaces an existing global guide. Claude/plugin cache installations are separate and remain unchanged.

## Updating without reinstalling

From the permanent checkout:

```bash
git pull --ff-only
```

Existing installed skills, docs, and resource links now expose the pulled contents. New assets inside a linked skill directory also appear automatically. Reload or restart the client if it caches skill metadata or instructions. The installer does not pull, switch branches, or restart clients for you.

- **New/renamed top-level skills or docs:** run the installer again to add the new links.
- **Deleted/renamed entries:** rerunning reports stale links into this checkout. Inspect each reported target and remove only the obsolete link itself; unrelated entries are not deleted.
- **Moved checkout:** absolute links break. Run `scripts/install.sh --dry-run` from the new permanent checkout, then rerun without that flag to back up old links, repair them, and update the local registry path.
- **Source edits:** edits made through an installed link modify the source checkout, including uncommitted changes. Commit or resolve local changes using your normal Git workflow before pulling.

Do not install from a disposable linked worktree: installation rejects it because worktree cleanup would break live skills. Implement/review changes in a worktree, merge them, and install from the permanent primary checkout.

## Recovery and partial failures

Dry run performs dependency, path and registry preflight with **zero filesystem writes**. Actual installation prints source/destination paths, entry classifications, backup manifests and final counts. Use one installer/operator per selected root; detected destination changes abort the run.

Each backup manifest records the intended source, destination, original entry kind and reserved backup path before the entry moves. If an operation fails, completed links remain installed. The installer attempts to restore the failing entry and reports completed/pending paths and recovery locations. Fix the reported problem and rerun to finish. There is no whole-install rollback guarantee.

For manual restoration, find the original entry in the recorded backup. Verify the current destination is absent or is the installer-created link to the recorded source; remove only that verified link, then move the backup back to its original path. Never delete through the symlink or overwrite a new user entry. Preserve the manifest and any remaining backups. Backup deletion and automated uninstall are outside the installer.

Marketplace JSON is validated before linking. Unrelated entries and metadata are preserved; a single local PARA entry is added or its path updated. Ambiguous or nonlocal PARA registrations require manual reconciliation. Registry publication happens after links succeed, retaining the previous registry in a backup; a publication failure leaves it at its original path. A changed registry that was itself a symlink is replaced at its leaf without changing the former target. Rerun after resolving a registry failure.

## Gemini

Gemini CLI discovers user skills from `~/.agents/skills`, so the Codex installer provides the shared Gemini skill layout.

1. Run the same installer:

   ```bash
   ./scripts/install.sh
   ```

2. In Gemini, verify discovery:

   ```bash
   gemini skills list --all
   ```

## Pi

Pi discovers user skills from `~/.agents/skills`, so the Codex installer provides the shared Pi skill layout.

1. Run the same installer:

   ```bash
   ./scripts/install.sh
   ```

2. In Pi, verify skill discovery. Use the `para-init` skill; Pi may use its explicit selector when skill commands are enabled and natural language when they are disabled.

## OpenCode

OpenCode discovers user skills from `~/.agents/skills`, so the Codex installer provides the shared OpenCode skill layout.

1. Run the same installer:

   ```bash
   ./scripts/install.sh
   ```

2. Start OpenCode from any project. OpenCode exposes discovered skills to agents through its native `skill` tool.

3. Optional project-local install: set both installer roots to the project's `.agents` directory in a different project checkout. This keeps individual skills linked and includes supporting docs/resources without replacing a shared skill root.

## Cursor

Cursor supports Agent Skills in the editor and CLI. The installer writes the shared global `~/.agents/skills` path, which Cursor-compatible Agent Skills tooling can discover. Cursor also supports Cursor-specific skill directories such as `.cursor/skills/` for project-level skills and `~/.cursor/skills/` for user-level skills.

1. Run the same installer:

   ```bash
   ./scripts/install.sh
   ```

2. Restart Cursor. Skills can be auto-selected by the agent or chosen from its skill menu. Use the `para-init` skill to verify the workflow.

3. If your Cursor version does not discover the shared global path, use the same backup-and-link migration for Cursor's root:

   ```bash
   AGENTS_HOME="$HOME/.cursor" CODEX_HOME="$HOME/.cursor" ./scripts/install.sh --dry-run
   AGENTS_HOME="$HOME/.cursor" CODEX_HOME="$HOME/.cursor" ./scripts/install.sh
   ```

   Equal roots are deduplicated. Existing copied PARA entries are backed up before replacement, and docs/resources remain beside skills. This also maintains the installer's local marketplace JSON under that root; Cursor discovers the skill links. Verify discovery after reloading Cursor.

## Manual Acceptance Checklist

Before publishing or cutting a release, verify these flows manually:

- Claude Code: users are directed to `https://github.com/brian-lai/para-programming-plugin`.
- OpenAI Codex: `scripts/install.sh` installs `para-*` skills into `~/.agents/skills`, and the `para-init` skill is available to the agent and skill picker.
- Gemini CLI: `gemini skills list --all` discovers the installed `para-*` skills from `~/.agents/skills`.
- Pi: Pi discovers the installed `para-*` skills from `~/.agents/skills`; verify both commands-enabled and commands-disabled behavior.
- OpenCode: OpenCode discovers installed `para-*` skills from `~/.agents/skills` and exposes them through its native `skill` tool.
- Cursor: Cursor discovers installed `para-*` skills from the shared `~/.agents/skills` path or from fallback `~/.cursor/skills` links, and exposes them through the slash command menu.
- Single-skill installs: any skill that references a sibling skill includes a graceful fallback phrase.
- Full-tree installs: `docs/` and `resources/` are present beside `skills/` for methodology and initialization references.

## Troubleshooting

### Skills Not Available

- Restart the client after changing plugin or skill paths.
- Verify each linked skill directory contains `SKILL.md`.
- Confirm each `SKILL.md` frontmatter `name` matches the directory basename.

### Codex Registration Failed

- Install `jq`; both installation and `--dry-run` require it.
- Check that `~/.agents/plugins/marketplace.json` is valid JSON.
- Re-run `./scripts/install.sh --dry-run` to inspect the intended marketplace path.
