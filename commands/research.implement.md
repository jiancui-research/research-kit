---
description: Work the tasks.md queue across Setup, Build, Eval, explicit user-led manuscript work, and Polish; keep claims and task status current.
argument-hint: task id/section (e.g. T012, eval, or "paper intro"); Manuscript mode also accepts outline, critique, or explicit "draft <section>"
---

## User input
The user request arrives via `$ARGUMENTS`. It may name task ids, a queue section, a result/blocker, or explicit manuscript work (`paper intro`, `outline threat-model`, `critique <path>`, `draft eval`). If empty, work automated tasks top to bottom and **never** execute `[USER-LED]` tasks.

## What this phase is
The spec-kit `implement` analogue and the single queue executor. Setup/Build produce real project artifacts in the folders `plan.md` declares; Eval runs experiments and keeps `claims.md` honest; Polish closes reproducibility gaps. Paper tasks stay human-led inside an explicit mode: outline by default, critique an existing draft, and write full prose only when the user says `draft`. `.research/` remains docs-only.

## Dispatch before reading broad context
1. Read `./.research/memory/constitution.md` if it exists and `./.research/tasks.md` (required; route to `/research.tasks` if missing).
2. Enter **Manuscript mode** only when `$ARGUMENTS` explicitly names a `[USER-LED]` manuscript-setup or Paper task, starts with `paper`/`outline`/`critique`/`draft`, or points to a draft while naming its task. Otherwise enter **Execution mode**. Empty input always skips `[USER-LED]` tasks and reports which are READY/BLOCKED. Treat a legacy `[HUMAN]` tag (pre-0.8 queues) exactly like `[USER-LED]` - never execute it by default.

## Execution mode: Setup, Build, Eval, Polish
3. Read `./.research/plan.md` (required; route to `/research.plan` if missing) and `./.research/claims.md` if present. Work selected tasks in dependency order:
   - **Setup / Build:** implement per the architecture in the declared code folder (default `./src/`, legacy `./design/`). A `[spec-kit]` task gets its own spec-driven pass. If reality changes the design, update `plan.md` to built reality and flag the deviation for `/research.analyze`.
   - **Eval:** create `./eval/NN-slug.md` from `.research/templates/eval-template.md`; pre-write hypothesis, linked claim, setup, metric, baselines, variance, and falsifier; run it; record all results. Maintain `./eval/index.md` and `./.research/claims.md` with `supported / partial / refuted / pending`. No orphan claim or eval.
   - **Paper `[USER-LED]`:** skip unless explicitly selected. Never auto-outline or draft while walking the queue.
   - **Polish:** artifact README, reproduction pass, figures, and tables.

## Manuscript mode: explicit user-led work
4. Read `.research/templates/sections/manuscript-procedure.md` (**required**; if missing, say so, route to `/research.init` to fill the gap, and stop - never reconstruct the procedure from context), then follow it end to end - it is the shared procedure behind this mode and `/research.write`, so the two cannot drift. It covers: read the whole manuscript and show the argument brief plus a voice sample of the paper's own terms, person, tense, and number formatting before any prose; load the paper-type skeleton, `sections/rhetorical-moves.md`, the type's block in `sections/moves-by-type.md`, and the section craft guide; pin the section's claim, evidence, reviewer objection, and boundary; pick the mode (OUTLINE by default, REVISE / CRITIQUE / DRAFT on request, full prose only on the explicit word `draft`); run the blast radius on a revision; and never invent a number or overwrite prose silently.
5. Resolve the manuscript once: use the valid path in `.research/paper-repo`; else ask for an existing local path or Git URL; else derive `<shortname>-<venueabbrev><yy>-latex`, confirm it, create a private repo with `gh`, and clone it as a sibling. Never overwrite. Seed a new repo from the venue's current official CFP/LaTeX template, with `main.tex`, `refs.bib`, `.gitignore`, README, anonymization if required, and READY/BLOCKED section stubs. Record local path on line 1 and optional URL on line 2 of `.research/paper-repo`. If the selected task is manuscript setup only, mark it done and stop here.
6. Select the section from input or the next unfinished Paper task, then run the procedure above against it.
7. Write to `<manuscript>/<section>.md` or a labeled `.outline.md`/`.critique.md`. Never silently overwrite user prose. Update only the selected Paper task with `outlined`, `drafted`, `critiqued`, `revised`, or `blocked` plus any evidence/citation gaps. This queue bookkeeping is what this mode adds over `/research.write`.

## Shared queue bookkeeping
9. Check off completed tasks with `done: <what landed, where>`; mark blockers `BLOCKED: <reason>`. Preserve ids and dependency history. Reference files rather than pasting source into `.research/`.

## Validate
- Empty/default execution did not perform a `[USER-LED]` task; Manuscript mode had explicit user selection.
- Build code is outside `.research/`; eval files, index, claims, and task states agree.
- Manuscript mode followed the shared procedure: whole manuscript read, argument brief and voice sample shown before writing, section job pinned, outline by default, prose never overwritten, and a REVISE run reported its blast radius and proposed before applying.
- New prose matches the paper's established terms, person, tense, and number formatting, and applies the cross-cutting moves, the paper type's own moves, and the section guide.
- Full prose was produced only after the explicit word `draft`.

## Completion
Report selected tasks, paths changed, eval/claim verdicts, manuscript path and Paper status when applicable, all `[UNVERIFIED]`/`[cite?]` gaps, and queue counts (done/blocked/remaining). End with `Next: /research.implement` while work remains, otherwise `Next: /research.analyze`.
