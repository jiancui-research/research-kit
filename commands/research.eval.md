---
description: Evaluate the system with trackable evals and keep the claim-evidence matrix current. Evaluation only — the system itself is built by /research.design.
argument-hint: which eval(s) to add, run, or update — or paste a result to record
---

## User input

The user request arrives via the $ARGUMENTS placeholder. It may name a new eval to scaffold, an existing one to update, or paste results to record. If empty, derive the eval list from `.research/tasks/eval.md`.

## What this phase is

This is the run-and-track **evaluation** phase. Each eval is one falsifiable test of one claim. You scaffold it before running, fill in actual results after, and keep `.research/claims.md` honest as evidence arrives. Do not write paper prose here, and **do not build the system here** — for build-papers the system is constructed by `/research.design` (from `tasks/design.md`); this phase evaluates what it produced. If the design changed under you, re-run against the new build and let `/research.analyze` flag the drift.

The eval writeups, the index, and the actual scripts / data / results all live in `./eval/` at the project root; only `claims.md` (the shared evidence matrix) stays in `.research/`.

## Steps

1. Read `./.research/memory/constitution.md` if present (skip silently otherwise). Read `./.research/tasks/eval.md` (evaluation-design header + eval task list: methodology, baselines, datasets, metrics, threat model) and `./.research/proposal.md` (contributions, RQs). Read `./.research/claims.md` if it exists.
2. `mkdir -p ./eval`.
3. Decide the action from $ARGUMENTS:
   - **Scaffold** — for each eval implied by `tasks/eval.md` (or named by the user), create `./eval/NN-slug.md` from `.research/templates/eval-template.md`. Number sequentially (`01`, `02`, …); `slug` is a short kebab-case name. Never overwrite an existing file without saying so.
   - **Update** — open the matching `NN-slug.md` and fill the actual result, status, and any deviation from setup.
4. In every eval file make sure these are concrete and present:
   - **Hypothesis** — a single falsifiable statement, not a topic.
   - **Linked claim** — the exact claim id/text from `claims.md` this test supports or refutes (one eval, one primary claim).
   - **Setup** — baselines (and how each is tuned, fairly), datasets, hardware, hyperparameters, prompts, seeds — enough to reproduce from the file alone.
   - **Metric** — the specific measure(s), including variance reporting (error bars / CIs / significance) where applicable.
   - **Expected vs actual** — the prediction before running, then the observed result after.
   - **Status** — `planned` / `running` / `done` / `blocked`.
5. Maintain `./eval/index.md`: a table of `NN-slug | linked claim | metric | status | one-line result`. Regenerate the row for any file you touched; keep ordering by number.
6. Update `./.research/claims.md` (the claim ↔ evidence matrix). If `./.research/claims.md` does not exist, create it from `.research/templates/claims-template.md`. For each claim, list the eval id(s) that support it and the current verdict: `supported` / `partial` / `refuted` / `pending`. Flag any claim with no eval as an **overclaim** to rescope, and any eval that tests no claim as **scope creep**.

## Validate (short checklist)

- Each eval tests exactly one primary claim with a falsifiable hypothesis.
- Setup is reproducible from the file alone; baselines are fairly tuned, not strawmen.
- Metric matches the claim — no proxy passed off as the real thing.
- Surprising/anomalous actual results are noted, not silently dropped.
- `claims.md` and `index.md` agree with the eval files; no orphan claims or orphan evals.

## Completion

Report the eval file path(s) under `./eval/`, `./eval/index.md`, and `./.research/claims.md`. Then: `Next: /research.paper` (runs in parallel, synced by `claims.md`), then `/research.analyze` once claims are filled (or rerun `/research.eval` to record results as they land).
