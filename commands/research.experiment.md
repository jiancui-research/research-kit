---
description: Break the plan into trackable experiments and keep the claim-evidence matrix current.
argument-hint: which experiment(s) to add, run, or update — or paste a result to record
---

## User input

The user request arrives via the $ARGUMENTS placeholder. It may name a new experiment to scaffold, an existing one to update, or paste results to record. If empty, derive the experiment list from `.research/plan.md`.

## What this phase is

This is the run-and-track phase. Each experiment is one falsifiable test of one claim. You scaffold it before running, fill in actual results after, and keep `.research/claims.md` honest as evidence arrives. Do not write paper prose here.

## Steps

1. Read `./.research/memory/constitution.md` if present (skip silently otherwise). Read `./.research/plan.md` (methodology, baselines, datasets, metrics, threat model) and `./.research/idea.md` (contributions, RQs). Read `./.research/claims.md` if it exists.
2. `mkdir -p ./.research/experiments`.
3. Decide the action from $ARGUMENTS:
   - **Scaffold** — for each experiment implied by the plan (or named by the user), create `./.research/experiments/NN-slug.md` from `.research/templates/experiment-template.md`. Number sequentially (`01`, `02`, …); `slug` is a short kebab-case name. Never overwrite an existing file without saying so.
   - **Update** — open the matching `NN-slug.md` and fill the actual result, status, and any deviation from setup.
4. In every experiment file make sure these are concrete and present:
   - **Hypothesis** — a single falsifiable statement, not a topic.
   - **Linked claim** — the exact claim id/text from `claims.md` this test supports or refutes (one experiment, one primary claim).
   - **Setup** — baselines (and how each is tuned, fairly), datasets, hardware, hyperparameters, prompts, seeds — enough to reproduce from the file alone.
   - **Metric** — the specific measure(s), including variance reporting (error bars / CIs / significance) where applicable.
   - **Expected vs actual** — the prediction before running, then the observed result after.
   - **Status** — `planned` / `running` / `done` / `blocked`.
5. Maintain `./.research/experiments/index.md`: a table of `NN-slug | linked claim | metric | status | one-line result`. Regenerate the row for any file you touched; keep ordering by number.
6. Update `./.research/claims.md` (the claim ↔ evidence matrix). If `./.research/claims.md` does not exist, create it from `.research/templates/claims-template.md`. For each claim, list the experiment id(s) that support it and the current verdict: `supported` / `partial` / `refuted` / `pending`. Flag any claim with no experiment as an **overclaim** to rescope, and any experiment that tests no claim as **scope creep**.

## Validate (short checklist)

- Each experiment tests exactly one primary claim with a falsifiable hypothesis.
- Setup is reproducible from the file alone; baselines are fairly tuned, not strawmen.
- Metric matches the claim — no proxy passed off as the real thing.
- Surprising/anomalous actual results are noted, not silently dropped.
- `claims.md` and `index.md` agree with the experiment files; no orphan claims or orphan experiments.

## Completion

Report the experiment file path(s), `./.research/experiments/index.md`, and `./.research/claims.md`. Then: `Next: /research.paper` (or rerun `/research.experiment` to record results as they land).
