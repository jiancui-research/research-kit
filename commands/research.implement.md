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
4. Read `./.research/proposal.md`, `./.research/related-work.md`, `./.research/claims.md` if present, and `./.research/plan.md` for Design/Implementation. Infer paper type and load `.research/templates/paper/<type>.md`; load the abstract/intro or figures/tables craft guide when relevant. Missing claims mean result beats are `[UNVERIFIED]`, not invented.
5. Resolve the manuscript once: use the valid path in `.research/paper-repo`; else ask for an existing local path or Git URL; else derive `<shortname>-<venueabbrev><yy>-latex`, confirm it, create a private repo with `gh`, and clone it as a sibling. Never overwrite. Seed a new repo from the venue's current official CFP/LaTeX template, with `main.tex`, `refs.bib`, `.gitignore`, README, anonymization if required, and READY/BLOCKED section stubs. Record local path on line 1 and optional URL on line 2 of `.research/paper-repo`. If the selected task is manuscript setup only, mark it done and stop here.
6. Select the section from input or the next unfinished Paper task. Choose mode: **CRITIQUE** for pasted/referenced prose, **DRAFT** only with the explicit word `draft`, otherwise **OUTLINE**.
   - **Outline:** ordered argument beats, claim ids, evidence/eval/figure pointers, citations from `related-work.md`, and `[UNVERIFIED]`/`[cite?]` gaps. Hand back a skeleton, not paragraphs.
   - **Critique:** located findings for voice, claim traceability, overclaim, and tightening. Do not rewrite the user's prose.
   - **Draft:** write full prose only on explicit request, in the user's voice, with every empirical statement scoped to `claims.md`.
7. Write to `<manuscript>/<section>.md` or a labeled `.outline.md`/`.critique.md`. Never silently overwrite user prose. Update only the selected Paper task with `outlined`, `drafted`, `critiqued`, or `blocked` plus any evidence/citation gaps.
8. Apply load-bearing craft in every manuscript mode: motivation before method; scoped novelty; active `we`; each statistic paired with a named instance and absolute count; artifact named once; a "so what" after major findings; effectiveness and cost reported together; related-work themes ending in explicit deltas; venue-appropriate threat model and ethics/disclosure.

## Shared queue bookkeeping
9. Check off completed tasks with `done: <what landed, where>`; mark blockers `BLOCKED: <reason>`. Preserve ids and dependency history. Reference files rather than pasting source into `.research/`.

## Validate
- Empty/default execution did not perform a `[USER-LED]` task; Manuscript mode had explicit user selection.
- Build code is outside `.research/`; eval files, index, claims, and task states agree.
- Manuscript mode defaulted to outline, used the paper-type skeleton, mapped result beats to claims, and never overwrote prose.
- Full prose was produced only after the explicit word `draft`.

## Completion
Report selected tasks, paths changed, eval/claim verdicts, manuscript path and Paper status when applicable, all `[UNVERIFIED]`/`[cite?]` gaps, and queue counts (done/blocked/remaining). End with `Next: /research.implement` while work remains, otherwise `Next: /research.analyze`.
