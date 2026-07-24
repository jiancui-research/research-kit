---
description: Derive the single work queue .research/tasks.md from plan.md - Setup/Build/Eval/Paper/Polish sections, T-ids, claim links; re-runs refine and preserve checkbox states.
argument-hint: optional steering (e.g. "prioritize the kill-shot eval" or "paper tasks for sections 1-3 only")
---

## User input
The user request arrives via the $ARGUMENTS placeholder: steering for the queue (priorities, scope, what to defer). May be empty.

## What this phase is
The spec-kit `tasks` analogue: one ordered, checkable work queue for the whole study, derived from the stable `plan.md`. The queue is **expected to churn** - that is why it is separate from the plan. `/research.implement` works every section except **Paper**, whose `[HUMAN]` tasks belong to you via `/research.paper`.

## Steps
1. Read `./.research/memory/constitution.md` if it exists; skip silently otherwise.
2. Read `./.research/plan.md` (required - stop and route to `/research.plan` if missing) and `./.research/proposal.md` (contributions + claim ids). Read `./.research/claims.md` if present.
3. **Legacy migration.** If pre-0.7 `tasks/design.md` / `tasks/eval.md` / `tasks/paper.md` exist and `tasks.md` does not, offer to fold their task lists (with current checkbox states) into the new single file; leave the old files untouched.
4. Write `./.research/tasks.md` from `.research/templates/tasks-template.md`:
   - **Setup** - environment, repos, data access.
   - **Build** (paper-type aware) - what must exist before evaluation: system / PoC / harness+dataset / collection pipeline; absent for SoK with a one-line note. Code targets the folder `plan.md` declares. Tag heavy builds `[spec-kit]`.
   - **Eval** - one task per eval, kill-shot first, each `-> C#`, naming dataset/baselines/metric/falsifier from `plan.md`'s evaluation design.
   - **Paper `[HUMAN]`** - one task per section in the paper-type skeleton's order, tagged READY or BLOCKED on its claim id.
   - **Polish** - artifact, reproduction pass, figures.
   - Continuous T-ids, `[P]` for parallelizable, `(after Txxx)` dependencies.
5. **Re-run = refine.** Preserve existing checkbox states and done-notes; add/remove/reword tasks to match the current `plan.md`; report what changed in one short list. Never renumber a task that has a state.

## Validate (short checklist)
- Every task has a done-when criterion; every BLOCKED paper task names a claim id that also appears on an Eval task.
- Build matches the paper type; dependencies exist where Eval needs Build.
- No plan content restated here - methodology and architecture live in `plan.md`.
- Re-runs preserved states and reported the diff.

## Completion
Report `./.research/tasks.md` (sections + task counts, and the diff if refining). End with: `Next: /research.implement` (work the queue) - and `/research.paper` for the `[HUMAN]` tasks, in parallel.
