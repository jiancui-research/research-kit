# Tasks: [project / paper short name]

> Produced by `/research.tasks`, derived from `./.research/plan.md`. Lives at
> `./.research/tasks.md` - the single work queue for the whole study.
> Continuous ids (T001, T002, ...); `[P]` marks tasks that can run in parallel;
> `(after Txxx)` marks dependencies. `/research.implement` owns the whole queue,
> but `[USER-LED]` Paper tasks run only when explicitly selected by task id or
> `paper <section>`; empty/default runs skip them. Re-running `/research.tasks`
> refines the queue while preserving checkbox states and done-notes.

## Setup

- [ ] T001 [env / repo / data access bootstrap] - done when [criterion]. [P]
- [ ] T002 ...
- [ ] T003 [USER-LED] Resolve or create the manuscript repository and record `.research/paper-repo` - done when the confirmed sibling repo uses the official venue template. READY [P]

## Build (paper-type aware)

[What must exist before evaluation can run: full system (systems/defense), PoC/exploit
(attack), construction harness + dataset (benchmark), collection pipeline (measurement),
or nothing (SoK - state so in one line and keep any corpus prep in Eval). Code lands in
the folder `plan.md` declares. Tag a heavy build `[spec-kit]` (own spec-driven pass in
that repo) or `[dev]`.]

- [ ] T010 [component / deliverable] - done when [criterion]. [`[dev]`]
- [ ] T011 ... (after T010)

## Eval

[One task per eval, sequenced so the eval that would kill the paper runs first. Each
ties to exactly one primary claim id and names dataset, baselines, metric, and the
predicted result / falsifier. Every contribution's claim id appears on at least one
task (else: overclaim to rescope); every task serves a claim (else: scope creep).
Verdicts land in `claims.md`; writeups in `./eval/NN-slug.md`.]

- [ ] T020 [Eval] over [dataset] vs [baselines] on [metric]; predicts [falsifier]. -> C1 (after T010)
- [ ] T021 ... -> C2 [P]

## Paper [USER-LED]

[One task per section in the paper-type skeleton's order (from
`.research/templates/paper/<type>.md`). **READY** = framing sections writable now
(intro, related work, method, threat model, background). **BLOCKED on C#** =
results-dependent sections (evaluation/findings, abstract, conclusion) - they unblock
the moment `claims.md` marks their claim supported. `/research.implement` works
these only through explicit Manuscript mode; it never selects them during a default run.]

- [ ] T030 [USER-LED] Introduction - frame gap + preview. READY
- [ ] T031 [USER-LED] Evaluation section. BLOCKED on C1
- [ ] T032 ...

## Polish

- [ ] T040 Artifact README + reproduction pass. (after Eval)
- [ ] T041 Figure / table cleanup per `.research/templates/sections/figures-tables.md`.

## Validate before working the queue

- [ ] Every task has a done-when criterion; ids are unique and continuous.
- [ ] Every BLOCKED paper task names its claim id; that id also appears on an Eval task.
- [ ] Build section matches the paper type (shrunk or absent where nothing is built).
- [ ] Dependencies `(after Txxx)` exist where Eval needs Build.

---
Next: `/research.implement` (work automated tasks, or explicitly select a `[USER-LED]`
task with `/research.implement T030` or `/research.implement paper intro`).
