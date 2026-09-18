# Project setup

Internal procedure loaded from the installed bundle by each command. Run only the
selected command after setup; a suggested next command is not permission to run it.
`<bundle>` is the absolute bundle directory resolved by the calling command.

## Viewer commands

For `mdreview` and `texreview`, only resolve the bundled tool. Do not create
`.research/`, copy templates, or create project preferences to open a viewer.

## Research and writing commands

1. Use the current project root for `./.research/`. A manuscript named in
   `.research/paper-repo` may be elsewhere; keep tracking files in the project
   that invoked the command. Do not move an existing manuscript or project record.
2. Fill in missing templates from `<bundle>/templates/` automatically:

   ```sh
   # Set RESEARCH_KIT_BUNDLE to the absolute bundle directory already resolved.
   set -e
   mkdir -p ./.research/templates
   find "$RESEARCH_KIT_BUNDLE/templates" -type f | while IFS= read -r src; do
     rel="${src#"$RESEARCH_KIT_BUNDLE/templates/"}"
     target="./.research/templates/$rel"
     if [ -e "$target" ] || [ -L "$target" ]; then continue; fi
     mkdir -p "$(dirname "$target")"
     cp -n "$src" "$target"
   done
   ```

   Copy only missing files: some `cp -n` implementations return a nonzero status
   when they skip an existing file. Do not mistake that for a failed setup, or
   suppress real copy errors. Bundled template filenames contain no newlines.

   Preserve all existing local files. Compare the local templates needed for this
   run with the bundled versions. Report differences once; without an old baseline,
   a diff alone cannot prove whether a change was made by the user or the bundle.
   Refresh an existing file only when the user has requested or authorized it.
   Do not delete old templates or artifacts during setup.
3. Read `./.research/memory/constitution.md` if present. Otherwise create its parent
   and seed it from `./.research/templates/constitution-template.md`. Omit template
   usage notes from the live file. Specialize only from preferences explicitly
   supplied in this conversation: field, venue, quality priorities, and layout.
   Leave unknowns at their general defaults. Never infer results or project facts.
   Existing preferences survive setup; update them only on a request to change
   project settings, and report the changes. Writing preferences live in
   `./.research/writing/style.md` and are handled by `write`.
4. Resume the selected task in this turn. Do not ask the user to run a setup command.
   Required templates that remain unavailable are a named blocker: report the exact
   path and installation problem; never reconstruct missing guidance from memory.
   Missing optional guides are reported, with the resulting coverage limit.

For `review`, setup may read only bundled/local guidance and the constitution.
Do not inspect proposal, plan, tasks, claims, evals, style samples, or implementation
code to customize the review. After setup, its only output is the review round.

## Older local templates

Local copies may still mention retired stages. Preserve the files and translate
their routing instructions when using them:

| Old stage name | Current behavior |
|---|---|
| `init`, `constitution` | Complete the setup and project-preference steps above |
| `tasks` | `/research.plan` maintains both the design and queue |
| `style` | `/research.write style` uses `<bundle>/guides/writing-style.md` |
| `analyze` | Built-in consistency checks in `write` or `implement`; an explicit audit uses `/research.implement check` |
| `rebuttal`, `ae` | Retired; do not direct the user to a nonexistent command |

The current command's input, output, and reading boundaries take precedence over
old routing or ownership notes in a local template. In particular, a paper-only
review must not obey a skeleton's instruction to read internal project artifacts.
Internal procedures in `<bundle>/guides/` are read from the installed bundle each
run; customizable skeletons and craft guides are read from local template copies.

Report newly created setup files briefly alongside the task's own output.
