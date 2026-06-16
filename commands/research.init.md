---
description: Copy the bundled research-kit templates into this paper repo's .research/templates/ so the other commands can load them.
argument-hint: (no arguments) - run once per paper repo
---

## What this command owns

research-kit commands load skeletons and craft guides from `./.research/templates/`. This one-time setup copies the bundled templates into the current paper repo so those loads resolve. Run it once, after `install.sh`, before the rest of the pipeline.

## Steps

1. **Find the bundled templates.** They live in one of two places depending on how research-kit was installed:
   - **Claude Code plugin** (installed via `/plugin install`): inside the plugin bundle at `${CLAUDE_PLUGIN_ROOT}/templates`.
   - **`install.sh`** (any agent): staged at `${RESEARCH_KIT_HOME:-$HOME/.research-kit}/templates`.

   If neither exists, stop and tell the user to install research-kit first - in Claude Code via `/plugin install research-kit@research-kit`, or for any agent by running `install.sh` from the research-kit repo (that step installs the commands *and* stages the templates).

2. **Copy them into this repo**, without clobbering anything the user has already customized:

   ```sh
   mkdir -p ./.research/templates
   SRC=""
   for d in "${CLAUDE_PLUGIN_ROOT}/templates" "${RESEARCH_KIT_HOME:-$HOME/.research-kit}/templates"; do
     [ -d "$d" ] && { SRC="$d"; break; }
   done
   [ -n "$SRC" ] || { echo "No bundled templates found - install research-kit first (/plugin install, or ./install.sh)."; exit 1; }
   cp -Rn "$SRC/." ./.research/templates/
   ```

   `${CLAUDE_PLUGIN_ROOT}` is set by Claude Code when this runs from a plugin install; otherwise it is empty and the loop falls through to the `install.sh` staging dir. `cp -Rn` is no-clobber: existing files in `./.research/templates/` are preserved. Report which files were copied and which were left untouched.

3. **Confirm.** List the populated `./.research/templates/` tree (one level deep) so the user can see the skeletons and craft guides are now local.

## Notes

- Re-running is safe: it only fills in missing files, never overwrites your edits.
- To refresh a template after upgrading research-kit, pull the new bundle first - plugin users run `/plugin marketplace update` then `/plugin install research-kit@research-kit`; `install.sh` users re-run the script - then delete the specific `./.research/templates/<file>` you want updated and re-run `/research.init`.

## Completion

Report the populated `./.research/templates/` path and end with: `Next: /research.constitution`.
