---
description: Copy the bundled speckit-research templates into this paper repo's .research/templates/ so the other commands can load them.
argument-hint: (no arguments) - run once per paper repo
---

## What this command owns

speckit-research commands load skeletons and craft guides from `./.research/templates/`. This one-time setup copies the bundled templates into the current paper repo so those loads resolve. Run it once, after `install.sh`, before the rest of the pipeline.

## Steps

1. **Find the staged templates.** `install.sh` stages them at `${SPECKIT_RESEARCH_HOME:-$HOME/.claude/speckit-research}/templates`. If that directory does not exist, stop and tell the user to run `install.sh` from the speckit-research repo first - that step installs the commands *and* stages the templates.

2. **Copy them into this repo**, without clobbering anything the user has already customized:

   ```sh
   SRC="${SPECKIT_RESEARCH_HOME:-$HOME/.claude/speckit-research}/templates"
   mkdir -p ./.research/templates
   cp -Rn "$SRC/." ./.research/templates/
   ```

   `cp -Rn` is no-clobber: existing files in `./.research/templates/` are preserved. Report which files were copied and which were left untouched.

3. **Confirm.** List the populated `./.research/templates/` tree (one level deep) so the user can see the skeletons and craft guides are now local.

## Notes

- Re-running is safe: it only fills in missing files, never overwrites your edits.
- To refresh a template after upgrading speckit-research, re-run `install.sh` (re-stages the bundle), delete the specific `./.research/templates/<file>` you want updated, then re-run `/research.init`.

## Completion

Report the populated `./.research/templates/` path and end with: `Next: /research.constitution`.
