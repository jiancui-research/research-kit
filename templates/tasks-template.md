# Tasks: [project / paper short name]

> Produced by `/research.tasks`, derived from `./.research/plan.md`. Lives at
> `./.research/tasks.md` - the single work queue for the whole study.
> Continuous ids (T001, T002, ...); `[P]` marks tasks that can run in parallel;
> `(after Txxx)` marks dependencies. `/research.implement` works every section
> **except Paper**: tasks tagged `[HUMAN]` are yours, via `/research.paper`.
> Re-running `/research.tasks` is a **refine**: checkbox states and done-notes are
> preserved, changes are reported - the queue churns, the plan stays stable.

## Setup

- [ ] T001 [env / repo / data access bootstrap] - done when [criterion]. [P]
- [ ] T002 ...

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

## Paper [HUMAN]

[One task per section in the paper-type skeleton's order (from
`.research/templates/paper/<type>.md`). **READY** = framing sections writable now
(intro, related work, method, threat model, background). **BLOCKED on C#** =
results-dependent sections (evaluation/findings, abstract, conclusion) - they unblock
the moment `claims.md` marks their claim supported. `/research.implement` skips these;
`/research.paper` works them with you.]

- [ ] T030 [HUMAN] Introduction - frame gap + preview. READY
- [ ] T031 [HUMAN] Evaluation section. BLOCKED on C1
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
Next: `/research.implement` (work the queue), in parallel with `/research.paper`
(the [HUMAN] tasks), synced by `claims.md`.
