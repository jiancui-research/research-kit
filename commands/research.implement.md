---
description: Work the tasks.md queue - build into the folder plan.md declares, run evals and keep claims.md current, tick checkboxes. Skips [HUMAN] paper tasks; those belong to /research.paper.
argument-hint: which task(s) or section to work (e.g. "T012" or "eval") - or paste a result / blocker to record
---

## User input
The user request arrives via the $ARGUMENTS placeholder. It may name tasks or a section to work, or report a result/blocker. If empty, work `./.research/tasks.md` top to bottom.

## What this phase is
The spec-kit `implement` analogue: execute the queue. Build tasks produce **actual code** in the folder `plan.md` declares (default `./src/`; legacy `./design/` honored); Eval tasks run evaluations, write writeups to `./eval/`, and keep `./.research/claims.md` honest. **Paper tasks are never executed here** - anything tagged `[HUMAN]` is skipped and routed to `/research.paper` (the paper is human-led). `.research/` stays docs-only: no source code in it, ever.

## Steps
1. Read `./.research/memory/constitution.md` if it exists; skip silently otherwise.
2. Read `./.research/plan.md` (architecture, evaluation design, code-folder declaration) and `./.research/tasks.md` (the queue) - both required; route to the owning command if missing. Read `./.research/claims.md` if present.
3. **Work the queue in order** (or the tasks $ARGUMENTS names), respecting `(after Txxx)` dependencies:
   - **Setup / Build** - implement each deliverable per the architecture into the declared code folder. For `[spec-kit]` tasks, set up a spec-driven pass in that repo rather than dumping code inline. If reality forces a design change, make it, update `plan.md`'s architecture to match what was actually built, and flag the deviation for `/research.analyze`.
   - **Eval** - for each eval task: scaffold `./eval/NN-slug.md` from `.research/templates/eval-template.md` (hypothesis, linked claim, reproducible setup, metric with variance, expected vs actual, status); run it; fill actual results - surprising ones included, never dropped. Maintain `./eval/index.md` (NN-slug | claim | metric | status | one-line result). Update `./.research/claims.md` (create from `.research/templates/claims-template.md` if absent): per claim, its eval ids and verdict `supported / partial / refuted / pending`. Claim with no eval = overclaim to rescope; eval with no claim = scope creep.
   - **`[HUMAN]` (Paper)** - do not execute. Note it and point to `/research.paper`.
   - **Polish** - artifact README, reproduction pass, figure cleanup.
4. **Tick as you go.** Check off each completed task in `tasks.md` with a one-line `done: <what landed, where>`; mark blockers `[ ] BLOCKED: <reason>`. Reference file paths, never paste source into `.research/`.

## Validate (short checklist)
- Code lives in the declared folder, never inside `.research/`.
- Each eval tests one falsifiable claim; setup is reproducible from its file alone; baselines are fairly tuned.
- `claims.md`, `eval/index.md`, and the eval files agree; no orphan claims or evals.
- Checkboxes in `tasks.md` reflect reality; deviations from `plan.md` are flagged, not silently absorbed.
- No `[HUMAN]` task was executed.

## Completion
Report what landed (code paths, eval ids, claim verdict changes) and the queue state (done / blocked / remaining). End with: `Next: /research.paper` (the `[HUMAN]` tasks, using the fresh claims) or `/research.analyze` (sync check) - or rerun `/research.implement` to continue the queue.
