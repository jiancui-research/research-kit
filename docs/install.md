# Installation and upgrades

Choose the install path for your agent. The bundle contains nine commands and nine
generated skills, plus the templates, internal guides, and both review tools.

## Claude Code

In Claude Code:

```text
/plugin marketplace add jiancui-research/research-kit
/plugin install research-kit@research-kit
```

Invoke plugin stages as `/research-kit:research.write related-work`.

## Codex

From a terminal with Codex CLI installed:

```sh
codex plugin marketplace add https://github.com/jiancui-research/research-kit
codex plugin add research-kit@research-kit
```

The plugin ships `skills/<stage>/SKILL.md`; each skill reads its command from the
same installed bundle. Select `research.write` and include the section or other
input in the invoking message. No separate turn for arguments is required.

In the Codex skill selector, the fully qualified name is
`$research-kit:research.write`: `research-kit` is the plugin, and `research.write`
is the skill inside it. For example:

```text
$research-kit:research.write draft introduction
$research-kit:research.texreview
```

A bare `$research-kit` entry is an older, separately installed dispatcher skill.
It contains its own stage copies and does not update when the plugin updates.
Use the plugin's nine stage skills. If both installations exist, back up and
remove the legacy standalone skill and uninstall the old `research-kit-codex`
personal plugin. Also check for a separate custom-prompt installation before
assuming the plugin still ships retired stages.

You can also manage installed plugins through `/plugins`. Start a new session after
installation before using the bundled skills. See the [official plugin documentation](https://learn.chatgpt.com/docs/plugins).

The script's `--codex` option remains available for users of custom prompts; it
installs the command files to `~/.codex/prompts/`. The plugin and script are separate
installations, so update whichever one you use.

## Oh My Pi (OMP)

In OMP:

```text
/marketplace add jiancui-research/research-kit
/marketplace install research-kit@research-kit
```

Stages use `/research-kit:research.<name>`. The commands resolve bundled resources
through the enabled OMP plugin's installed-path registry entry.

## Script installs, including Copilot

```sh
git clone https://github.com/jiancui-research/research-kit
cd research-kit
./install.sh             # Claude Code
./install.sh --codex     # Codex custom prompts
./install.sh --copilot   # Copilot custom agents
./install.sh --all       # all three destinations
```

Copilot uses generated personal custom agents: select `research.write` through
`/agent`, then provide your request. The script stages shared resources in
`~/.research-kit/`. Other destinations are `~/.claude/commands/`,
`~/.codex/prompts/`, and `~/.copilot/agents/`.

Override them with `CLAUDE_COMMANDS_DIR`, `CODEX_PROMPTS_DIR`,
`COPILOT_AGENTS_DIR`, and `RESEARCH_KIT_HOME`. `--symlink` is available for
Claude/Codex command files. `--uninstall` removes installed research commands and
the staging directory; run it only against installations you mean to remove.

## Upgrading

For script installs, pull the updated checkout and re-run the same install flags.
For plugins, update the marketplace and installed plugin in your agent's plugin
manager. Start a new session to use the updated command/skill list.

Script upgrades use their install manifests to prune retired commands. An old
untracked file is preserved rather than guessed to belong to the kit. If retired
commands still appear, check whether you have both plugin and script installations,
and inspect the installer output for files it kept.

Project setup now runs automatically. There is no separate setup command to run.
It fills missing `.research/templates/` files, keeps existing ones, and reports
relevant differences. A difference alone does not distinguish an old bundle from a
local customization; request a selective refresh when needed. Existing project
artifacts, completed task notes, and writing preferences are preserved.

The consolidated routes are:

| Previous command name | Current route |
|---|---|
| `init`, `constitution` | Automatic setup; edit `.research/memory/constitution.md` for preferences |
| `tasks` | `/research.plan` maintains both `plan.md` and `tasks.md` |
| `style` | `/research.write style` maintains the same style file |
| `analyze` | Checks built into writing/implementation; `/research.implement check` for an explicit audit |
| `rebuttal`, `ae` | Removed |

The two viewers remain separate: `/research.mdreview` and `/research.texreview`.
Legacy local template handoffs are interpreted through the current bundled setup
guide, so they do not require a removed command. Old output files are not deleted.

### Installing an unpublished local checkout in Codex

Use this when you want the code in your checkout, including uncommitted changes.
The Git marketplace installs the published repository, which may be older.
After generating skills and running the packaging tests, select the local source:

```sh
codex plugin marketplace remove research-kit
codex plugin marketplace add /absolute/path/to/research-kit
codex plugin add research-kit@research-kit
```

The first command is needed only if that marketplace name already points to a
different source. It removes the configured marketplace source, not your checkout
or paper files. Check `codex plugin marketplace list` and `codex plugin list` to
confirm the local path and installed version, then start a new session. This
switches updates to your local checkout; use the Git URL again to return to releases.

## Troubleshooting

- **Unexpected command list:** compare the nine entries in the README with what
  your agent exposes. For a script install, list the `research.*` files in the
  destination and re-run the installer if necessary.
- **Missing guides/templates:** re-install the complete bundle. A command file by
  itself is insufficient; it needs the staged resources or its enclosing plugin.
- **Windows script reports “No such file or directory”:** use LF line endings.
  The repo's `.gitattributes` pins shell scripts to LF; `dos2unix install.sh` can
  repair an older checkout with a CRLF shebang.
- **File locked during an upgrade:** close sessions using that installation and retry.
- **Viewer prerequisites:** `mdreview` needs `uv`; `texreview` also needs a TeX
  installation for compilation and SyncTeX. Viewer launch does not create `.research/`.
