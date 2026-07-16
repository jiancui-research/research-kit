---
description: Copy the bundled research-kit templates into this paper repo's .research/templates/ so the other commands can load them.
argument-hint: (no arguments) - run once per paper repo
---

## What this command owns

research-kit commands load skeletons and craft guides from `./.research/templates/`. This one-time setup copies the bundled templates into the current paper repo so those loads resolve. Run it once, after installing research-kit, before the rest of the pipeline.

## Steps

1. **Find the bundled templates.** They live in one of three places depending on how research-kit was installed:
   - **Claude Code plugin** (installed via `/plugin install`): inside the plugin bundle at `${CLAUDE_PLUGIN_ROOT}/templates`.
   - **OMP plugin** (installed via `/marketplace install`): inside the absolute `installPath` recorded for `research-kit@research-kit` in the nearest project-scoped `.omp/plugins/installed_plugins.json`, falling back to `~/.omp/plugins/installed_plugins.json`.
   - **`install.sh`** (Claude Code, Codex CLI, or Copilot CLI): staged at `${RESEARCH_KIT_HOME:-$HOME/.research-kit}/templates`.

   If none exists, stop and tell the user to install research-kit first - via `/plugin install research-kit@research-kit` in Claude Code, via `/marketplace install research-kit@research-kit` in OMP, or by running `install.sh` from the research-kit repo.

2. **Copy them into this repo**, without clobbering anything the user has already customized:

   For an OMP install, read the registry JSON first and set `OMP_PLUGIN_ROOT` to the enabled `research-kit@research-kit` entry's absolute `installPath` (project scope takes precedence over user scope). Then run:

   ```sh
   mkdir -p ./.research/templates
   OMP_PLUGIN_ROOT="${OMP_PLUGIN_ROOT:-}"
   SRC=""
   for d in \
     "${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/templates}" \
     "${OMP_PLUGIN_ROOT:+$OMP_PLUGIN_ROOT/templates}" \
     "${RESEARCH_KIT_HOME:-$HOME/.research-kit}/templates"; do
     [ -d "$d" ] && { SRC="$d"; break; }
   done
   [ -n "$SRC" ] || { echo "No bundled templates found - install research-kit first (/plugin install, /marketplace install, or ./install.sh)."; exit 1; }
   cp -Rn "$SRC/." ./.research/templates/
   ```

   `${CLAUDE_PLUGIN_ROOT}` is set by Claude Code, while OMP's plugin root comes from its installed-plugin registry. Otherwise the loop falls through to the `install.sh` staging directory. `cp -Rn` is no-clobber: existing files in `./.research/templates/` are preserved. Report which files were copied and which were left untouched.

3. **Confirm.** List the populated `./.research/templates/` tree (one level deep) so the user can see the skeletons and craft guides are now local.

## Notes

- Re-running is safe: it only fills in missing files, never overwrites your edits.
- To refresh a template after upgrading research-kit, pull the new bundle first - Claude Code plugin users run `/plugin marketplace update` then `/plugin install research-kit@research-kit`; OMP users run `/marketplace update research-kit` then `/marketplace upgrade research-kit@research-kit`; `install.sh` users re-run the script. Then delete the specific `./.research/templates/<file>` you want updated and re-run `/research.init` (namespaced for plugin installs).

## Completion

Report the populated `./.research/templates/` path and end with: `Next: /research.constitution`.
