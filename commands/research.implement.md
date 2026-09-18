---
description: "Work the study queue, build and evaluate, maintain claims and progress, and check consistency before finishing; manuscript tasks require explicit selection."
argument-hint: "task ID or queue section, explicit paper work, or check (e.g. \"T012\", \"eval\", \"paper intro\", \"draft evaluation\", \"check claims\")"
---

## Preparation

Resolve `<bundle>` from the enclosing installed plugin directory (the skill adapter
supplies it), else `${CLAUDE_PLUGIN_ROOT}`, else the enabled OMP `installPath` in
the nearest project `.omp/plugins/installed_plugins.json` or `~/.omp/plugins/installed_plugins.json`,
else `${RESEARCH_KIT_HOME:-$HOME/.research-kit}`. Use the first candidate containing
`guides/setup.md` and `templates/`; name the installation problem if none resolves.
Read `<bundle>/guides/setup.md` and complete its setup for this command, then resume
the request. Internal guides use this bundle; artifact templates use local copies.

## User input and dispatch

`$ARGUMENTS` names tasks, queue sections, a result/blocker, manuscript work, or an
explicit `check`. Empty input works automated tasks in dependency order and skips
all `[USER-LED]` tasks. A Next suggestion never authorizes another stage.

1. Read the project constitution. For an explicit consistency check, follow
   `<bundle>/guides/consistency.md`, report available evidence and gaps, then stop.
   This mode needs no queue and does not edit code, manuscript, claims, or tasks.
2. Otherwise read `./.research/tasks.md` and `./.research/plan.md` (both required;
   route to `/research.plan` if either is missing). Read `claims.md` when present.
3. Enter **Manuscript mode** only for explicitly selected Paper/manuscript-setup
   tasks or input beginning with `paper`, `outline`, `critique`, or `draft`.
   Otherwise enter **Execution mode**. Treat legacy `[HUMAN]` tags as `[USER-LED]`.

## Execution mode

Work the selected tasks in dependency order:

- **Setup / Build:** implement in the code directory declared by the plan (default
  `./src/`, legacy `./design/` is valid). If the built design changes, record the
  deviation in `plan.md`, report it, and check the affected tasks and evidence.
- **Eval:** create `./eval/NN-slug.md` from the local eval template. Pre-write the
  hypothesis, claim IDs, setup, baselines, metric, variability, and falsifier; run
  the experiment and record inconvenient results as well as successes. Maintain
  `./eval/index.md` and `./.research/claims.md` with supported/partial/refuted/pending
  verdicts. Every claim and evaluation needs its evidence links.
- **Paper `[USER-LED]`:** skip unless selected explicitly. Default execution must
  never start outlining or drafting the manuscript.
- **Polish:** reproduction checks, figures, tables, and project documentation.

Real code, data, and experiment outputs live outside `.research/`. Do not re-plan
an entire study merely to make a task appear complete; route design/queue changes
beyond the current work to `/research.plan`.

## Manuscript mode

1. Resolve an explicit manuscript path, else `.research/paper-repo`, else the
   current manuscript repo, else `./paper/`. For an explicit setup task with no
   manuscript, use the user's requested local path or Git URL. Creating a new
   remote repository requires the user's instruction; it is not a writing prerequisite.
2. New manuscript setup uses the venue's official template and the constitution's
   layout: thin `main.tex`, `sections/`, `figures/`, `tables/`, `references.bib`,
   README, and `.gitignore`. Honor anonymity requirements; mark stubs READY/BLOCKED.
   Record the local path and optional URL in `.research/paper-repo`. A setup-only
   task finishes here after validating the layout and recording task status.
3. Before outlining, drafting, or revising a section, follow **Before section writing**
   in `<bundle>/guides/writing-style.md`: use 2–3 relevant example papers or an
   explicit skip, reusing the project's choice. If undecided, ask and wait; do not
   mark the Paper task complete. Critique-only work bypasses this step. This
   requirement takes precedence over older local templates that omit it.
4. For section work, read `.research/templates/sections/manuscript-procedure.md`
   (required). Follow the same procedure as `/research.write`: whole-paper reading,
   argument brief, three to five verbatim voice-sample sentences, section/type craft,
   section purpose and evidence, and revision impact checks. Setup fills missing
   templates; a required file still absent is a named blocker, never improvised.
5. Read `.research/writing/style.md` when present. To record requested preferences,
   follow `<bundle>/guides/writing-style.md`, as the shared section procedure directs.
6. Write into the actual section file and include a new section in the manuscript.
   Keep scratch outlines/critiques beside the section, never included in TeX.
   Outline by default; full prose requires an explicit drafting request. Preserve
   existing conventions and never silently overwrite user prose.
7. Update only the selected Paper task with outlined/drafted/critiqued/revised/blocked
   and any evidence or citation gaps. An outline is not a completed draft task.

## Finish and validate

1. Follow `<bundle>/guides/consistency.md` against changed work and its dependencies.
   Correct issues within scope; name broader stale artifacts and the action needed.
2. Check off tasks only when their done-when criteria and validation are met.
   Record `done: <what landed, where>` or `BLOCKED: <reason>`. Preserve IDs, notes,
   and dependency history. Do not turn missing evidence into a supported claim.
3. Confirm code/eval/claims/task states agree and default execution skipped Paper work.
   Outline/draft/revise work required analyzed examples or an explicit skip, with
   the choice and scope saved in the style file. For manuscript work, verify sentence
   construction, terms, number formatting, referential clarity, section/type craft,
   and all remaining `[UNVERIFIED]`/`[cite?]` gaps.

## Completion

Report selected tasks, paths changed, evidence verdicts, consistency status, and
queue counts. Suggest `/research.implement` for remaining automated work,
`/research.write <section>` for a paper needing prose, or `/research.review` when
the manuscript is ready. Explicit check-only work reports findings without fixes.
