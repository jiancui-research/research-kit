# Contributing to speckit-research

Thanks for helping improve speckit-research. It is a small, MIT-licensed toolkit: Claude Code slash commands plus Markdown templates and a default research constitution. There is no Python CLI, no hooks, and no build step. Keep it that way.

## Guiding principles

- **Simplicity first.** Markdown only. No new machinery, no speculative features. If a change adds a moving part, it needs a strong reason.
- **Original and generalizable.** Write guidance that works for any researcher. Never copy verbatim sentences, unpublished drafts, person names, or other identifying details from private notes. Distill principles and rewrite them cleanly.
- **Stay consistent.** One namespace (`/research.*`), one working directory (`./.research/...`), one pipeline order, everywhere. A change in one place that contradicts another is a bug.

## Repo conventions

- **Namespace.** Every command is invoked as `/research.<name>` and lives at `commands/research.<name>.md`. `install.sh` copies (or symlinks) those files into `~/.claude/commands/`.
- **Working directory.** Commands read and write only under `./.research/` in the user's own paper repo. They `mkdir -p` as needed and never overwrite user content without saying so.
- **Pipeline order.** `constitution -> idea -> relatedwork -> plan -> experiment -> paper -> analyze`, plus `rebuttal`, `review`, `proposal`, and `ae` as needed. Don't reorder it casually.
- **Command contract.** Each command should: (1) read `./.research/memory/constitution.md` if it exists, skip silently otherwise; (2) read its upstream artifacts; (3) take user input via the `$ARGUMENTS` placeholder; (4) produce or update only its own artifact(s) and end by reporting the path(s) plus a one-line `Next: /research.<x>`; (5) be paper-type aware where relevant via `templates/paper/<type>.md`; (6) stay focused and short - aim under ~120 lines, and reference templates instead of inlining long checklists.

## Adding a new command

1. Create `commands/research.<x>.md`. Start the file with minimal YAML frontmatter:

   ```markdown
   ---
   description: One line on what the command does.
   argument-hint: what the user should type after the command name
   ---
   ```

   Then write the steps. Follow the command contract above. Read the user's free text from `$ARGUMENTS`.
2. If the command needs a template, add it under `templates/` (e.g. `templates/<x>-template.md`) and have the command read it rather than inlining the structure.
3. Add a row for the command to the **Commands** table in `README.md`, and slot it into the pipeline description if it belongs in the main flow.
4. Run `./install.sh` and try the command in a scratch paper repo to confirm it writes the right artifact to `./.research/` and prints the path and next step.

## Adding a paper-type skeleton

Paper-type-aware commands look for `templates/paper/<type>.md` (measurement, attack, defense, benchmark today).

1. Add `templates/paper/<newtype>.md`. Mirror the existing skeletons: a short header noting which artifacts to read first, the core question and proof obligation for that paper type, and bracketed `[...]` placeholders for each section.
2. Make sure commands that infer paper type (such as `/research.idea`) will recognize the new type, and confirm `/research.paper` reads the new skeleton.
3. Note the new type in the **Paper types** section of `README.md`.

## Before you open a PR

- Keep the diff surgical: every changed line should trace to the change you intended.
- Re-read the three guiding principles. If your change adds complexity, removes simplicity, or breaks namespace/path/pipeline consistency, rework it first.
- Confirm `install.sh` still runs cleanly (it is POSIX `sh` and must stay idempotent).
