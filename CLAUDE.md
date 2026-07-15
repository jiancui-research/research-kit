# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

research-kit is **not an application** - it is a bundle of AI-agent slash commands authored as Markdown, plus Markdown templates and a default research constitution. There is no runtime, no build step, no Python CLI, no hooks, no tests in the conventional sense. "The model does the work; the files are the interface." A command is just `commands/research.<name>.md`: YAML frontmatter (`description`, optional `argument-hint`) + a prompt body. Keep it that way - a change that adds a moving part needs a strong reason (see `CONTRIBUTING.md`).

The product is a Spec-Driven Development pipeline for writing research papers. Each command turns one fuzzy stage (proposal, related work, feasibility, tasks, design, eval, paper, analyze, review, ...) into one reviewable artifact on disk.

Because the shipped Markdown *is* the product (read by AI agents and users, never compiled), editing prose is the main activity here - match the existing voice: sentence-case headers, spaced hyphens not em-dashes, distilled/original guidance (never paste private notes, names, or unpublished drafts), and the writing-voice rules in `memory/constitution.md`.

## The two repos you must never confuse

When editing this repo you are authoring the **bundle**. The `.research/...` paths written inside command bodies refer to the **end user's paper repo at runtime**, not to this repo.

- **This repo (the bundle):** `commands/`, `templates/` (root), `tools/` (optional utilities), `memory/constitution.md` (root), `install.sh`, `.claude-plugin/`.
- **The user's paper repo (runtime, never exists here):** `./.research/` holds tracking docs - `.research/templates/` (copied in by `/research.init`), `.research/memory/constitution.md`, `proposal.md`, `claims.md`, `tasks/`, etc. Work products (`design/`, `eval/`, `paper/`, `feasibility/`) are sibling root folders.

So: this repo's root `templates/` and `memory/constitution.md` are the **source** that gets *copied into* a user's `./.research/templates/` and `./.research/memory/constitution.md`. Command bodies read from the `.research/` copies, never from this repo's paths.

## Distribution: one source, three agents, two mechanisms

Commands are authored **once** in the Claude/Codex slash-command form. Two install paths exist:

1. **`install.sh`** (POSIX sh, idempotent, self-pruning) installs for Claude Code (`~/.claude/commands/`), Codex CLI (`~/.codex/prompts/`), or Copilot CLI (`~/.copilot/agents/`). For Claude/Codex it copies the raw `.md` verbatim. For **Copilot it transforms** each command into a `*.agent.md` custom agent, prepending an adapter note that maps `$ARGUMENTS` → the user's message and `Next: /research.<x>` → switching agents. You do **not** hand-write the Copilot copy - `install_copilot()` generates it.
2. **Plugin marketplace** (`.claude-plugin/marketplace.json` + `plugin.json`) - zero-script path for Claude Code and Copilot CLI, both reading `commands/` directly. Stages get namespaced as `/research-kit:research.<name>`. Codex can't use this bundle (it needs a skill-based plugin), so Codex always goes through the script.

Template resolution at runtime (see `commands/research.init.md`): templates live at `${CLAUDE_PLUGIN_ROOT}/templates` (plugin install) **or** `${RESEARCH_KIT_HOME:-$HOME/.research-kit}/templates` (staged by `install.sh`). `/research.init` checks both, then `cp -Rn` (no-clobber) into the user's `./.research/templates/`.

## The command contract

Every command body must:
1. Read `./.research/memory/constitution.md` if it exists; skip silently otherwise.
2. Read its upstream artifacts (e.g. `tasks` reads `proposal.md` + `feasibility.md`; `paper` reads `tasks/paper.md` + `tasks/design.md` + `claims.md`).
3. Take user input via the `$ARGUMENTS` placeholder.
4. Produce/update **only its own artifact(s)**, `mkdir -p` as needed, never overwrite user content silently, and end by reporting the path(s) + a one-line `Next: /research.<x>`.
5. Be paper-type aware where relevant, via `.research/templates/paper/<type>.md` (types: measurement, attack, defense, benchmark, systematization/SoK).
6. Stay short (aim < ~120 lines); reference templates instead of inlining long checklists.

## Pipeline and the parallel lanes

```
constitution → proposal → relatedwork → feasibility(GO/NO-GO/PIVOT gate) → tasks → (design ∥ eval ∥ paper) → analyze → review (loop)
```
Plus `rebuttal` (post-submission) and `ae` (artifact eval). After `tasks`, three lanes co-evolve and **communicate only through shared docs they read, never by writing into each other**: `design` builds code in `./design/` (+ owns `tasks/design.md`); `eval` writes `claims.md`; `paper` reads `claims.md`. Only **two** commands ever write into another command's doc: `relatedwork → proposal.md` (sharpens the gap) and `eval → claims.md`. `analyze` and `review` are **report-only** - they detect drift / findings and route a re-run to the owning command rather than editing other lanes. The `design` lane is paper-type aware: present for build-papers (systems/defense/attack/benchmark), skipped for measurement/SoK.

Authoritative references: `docs/workflow.md` (per-command input→output table + write-edges) and `docs/design.md` (spec-kit mapping, form factor, scope/non-goals).

## Common commands

```sh
./install.sh                 # install for Claude Code (default)
./install.sh --all           # Claude + Codex + Copilot
./install.sh --codex --copilot   # named agents
./install.sh --symlink       # symlink instead of copy (claude/codex only)
./install.sh --uninstall     # remove everything from all agents + staged templates
```

There is no test runner or linter. The validation loop (from `CONTRIBUTING.md`) is: run `./install.sh --all` then `./install.sh --uninstall` to confirm the script stays clean and idempotent, and try a changed command in a scratch paper repo to confirm it writes the right artifact under `./.research/` and prints the path + next step.

## When adding or editing a command

- Create `commands/research.<x>.md`, follow the command contract, read input from `$ARGUMENTS`.
- New structure goes in a `templates/<x>-template.md` the command reads from `.research/templates/...` - don't inline long skeletons.
- Update the **Commands** table in `README.md` (and the pipeline description if it's in the main flow); mirror in `docs/workflow.md` / `docs/design.md` if the flow changes.
- New paper type → add `templates/paper/<type>.md`, ensure type-inferring commands (e.g. `research.proposal`) recognize it.
- Keep consistency invariant: one namespace (`/research.*`), one working dir (`./.research/...`), one pipeline order, everywhere. A change in one place that contradicts another is a bug. Bump `version` in `.claude-plugin/plugin.json` when the bundle changes meaningfully.

## Gotchas

- **Never hand-edit a Copilot `*.agent.md`.** It is generated by `install_copilot()` from the source command; edits get overwritten on the next install. Author once in `commands/research.<x>.md`.
- **Don't read this repo's root `templates/` or `memory/constitution.md` from a command body.** Commands read the user's `./.research/templates/...` and `./.research/memory/constitution.md` copies (placed by `/research.init`). The root files are the *source* that gets copied, not the runtime path.
- **Don't let a command write into another command's artifact.** The only two allowed cross-writes are `relatedwork → proposal.md` and `eval → claims.md`; `analyze` and `review` are report-only (they route a re-run, never edit other lanes).
- **Don't inline a long checklist or skeleton** into a command body - it belongs in `templates/` and is referenced via `.research/templates/...`. Keep command files short (< ~120 lines).
- **`cp -Rn` (init) and the install copy are no-clobber by design.** They fill in missing files and never overwrite a user's customized `./.research/` content - that's a feature; don't "fix" it into an overwrite.
- **Don't add machinery.** No Python CLI, hooks, MCP servers, daemon, or build step for the pipeline itself. One deliberate exception exists: `tools/mdreview.py`, an optional leaf review UI launched by `/research.mdreview` - nothing in the pipeline depends on it, and it must stay that way. The plugin packaging is a manifest around the same Markdown - nothing more.
- **Editing one place means editing the mirrors.** A flow change must stay consistent across `README.md`, `docs/workflow.md`, and `docs/design.md`; a command's one-line description lives in its frontmatter *and* the README Commands table.
