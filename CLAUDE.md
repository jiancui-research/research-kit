# Repository guidance

## What this repo is

Research-kit is a bundle of Markdown commands, internal procedures, and templates.
The agent performs the work. Two optional Python utilities provide Markdown and
LaTeX/PDF review UIs. Do not add a pipeline daemon, orchestrator, or runtime CLI.
Use original, generalizable guidance; never paste private notes, names, or drafts.
Match the existing writing voice: sentence-case headings and clear, direct prose.

## Public commands

Nine commands live in `commands/`: `proposal`, `relatedwork`, `feasibility`, `plan`,
`implement`, `write`, `review`, `mdreview`, and `texreview`.

```
proposal -> relatedwork -> feasibility -> plan -> implement -> write -> review
```

Feasibility can loop back to proposal. Review routes findings to the relevant
stage. Keep `mdreview` and `texreview` separate. Do not reintroduce retired setup,
queue, style, audit, rebuttal, or artifact-evaluation commands as public aliases.

## Bundle versus user project

- Bundle: `commands/`, `guides/`, `templates/`, `tools/`, plugin manifests, installer.
- User project: `./.research/` contains tracking docs and preferences; code, data,
  experiments, and manuscript source live outside it, in the project's own layout.
- Commands resolve an installed bundle before reading `guides/setup.md`. A plugin
  skill supplies its enclosing root; other paths are the Claude plugin root, OMP's
  enabled installed-path registry entry, and the script's staging directory.
- Internal procedures are loaded from the bundle's `guides/` each run. Templates
  and craft are loaded from the user's `./.research/templates/` copies. Bootstrap
  copying is the deliberate exception: it reads the installed bundle's templates.
- Setup fills missing files with no clobber and seeds project preferences when
  absent. It preserves existing customization and reports relevant drift. Viewers
  only resolve tools; they do not create research tracking files.

## Ownership and execution boundaries

- `proposal` owns proposal framing; `relatedwork` owns its survey and may sharpen
  proposal positioning; feasibility owns the cheap probe and verdict.
- `plan` owns `plan.md` and `tasks.md`. Keep them separate; preserve task IDs,
  checkbox states, done-notes, and dependency history when refining.
- `implement` owns selected work, eval records, claims, and queue progress. It may
  record built-design deviations in the plan. Default execution skips `[USER-LED]`
  Paper tasks; explicitly selected manuscript work follows the shared procedure.
- `write` owns section work and requested style updates. Style stays at
  `.research/writing/style.md`; the queue is untouched. Writing reads the whole
  paper and quotes real sentences before drafting. A drafting request must be explicit.
- Before outlining, drafting, or revising, both writing paths load the bundled
  writing-style guide and require selected example papers or an explicit skip.
  Keep the choice and its scope in the same style file and reuse it across sections.
  Critiques and checks do not require examples.
- Both implementation and writing check consistency before finishing. Check-only
  requests report without modifying the inspected artifacts.
- After setup, `review` writes only its round file. It reads only manuscript and
  venue/type context, never internal project evidence or the consistency guide.
- `Next:` suggests the next stage; it does not authorize invoking it.

## Distribution

Author instructions once in `commands/research.<name>.md`. Use description and
argument-hint frontmatter, with `$ARGUMENTS` for input. Keep commands under about
120 lines; put shared procedures in `guides/` and artifact skeletons in `templates/`.

`install.sh` copies raw Claude/Codex prompt files and generates Copilot custom
agents. It stages guides, templates, and tools. Never hand-edit generated adapters.
Claude/OMP plugins expose commands; Codex plugins use generated skill pointers.
Run `python3 tools/gen_codex_skills.py` after changing commands or the Claude
manifest. The Codex manifest is generated; versions must agree. Bump the bundle
version for meaningful changes.

Keep the README, workflow, design, templates, and command handoffs consistent.
See `docs/workflow.md` for file ownership and `docs/install.md` for upgrade routing.

## Validation

Run the relevant tests with `uv run --with pytest --with markdown-it-py --with pyyaml pytest tools`.
Packaging tests check command references, generated skill drift, staged resources,
and install/upgrade/uninstall in isolated directories. Test changes in throwaway
projects only. Never run installation or uninstall checks against the user's real
agent directories, and never use a personal paper repo as a fixture.
