---
description: "Design the study and maintain its work queue in .research/plan.md and .research/tasks.md, preserving task IDs and progress."
argument-hint: "optional design or queue steering (e.g. \"coverage over severity\", \"prioritize the decisive eval\", \"refresh tasks from the existing plan\")"
---

## Preparation

Resolve `<bundle>` from the enclosing installed plugin directory (the skill adapter
supplies it), else `${CLAUDE_PLUGIN_ROOT}`, else the enabled OMP `installPath` in
the nearest project `.omp/plugins/installed_plugins.json` or `~/.omp/plugins/installed_plugins.json`,
else `${RESEARCH_KIT_HOME:-$HOME/.research-kit}`. Use the first candidate containing
`guides/setup.md` and `templates/`; name the installation problem if none resolves.
Read `<bundle>/guides/setup.md` and complete its setup for this command, then resume
the request. Internal guides use this bundle; artifact templates use local copies.

## User input

`$ARGUMENTS` steers the study design, project layout, or task priorities. Empty input
creates or refines the design and derives its queue. A request to refresh only the
queue leaves a settled design unchanged.

## What this phase owns

Two documents: `./.research/plan.md` holds the stable study design;
`./.research/tasks.md` holds the executable queue. Review the design before deriving
work from it. Keep the two documents separate so queue progress does not obscure
changes to methodology.

## Steps

1. Read the project constitution and `proposal.md` (required), all under `.research/`.
   Missing proposal routes to `/research.proposal`. For design work, require a
   `feasibility.md` GO; missing or unresolved feasibility routes to
   `/research.feasibility`. Existing code/results can supply that assessment, but
   their presence alone is not a GO. Read `related-work.md` when present.
   For a queue-only refresh from an existing plan, skip design steps 3-4 and use
   the existing design; do not demand a new probe simply to maintain its queue.
   Flag a missing feasibility record, and keep work that depends on an unresolved
   NO-GO/PIVOT blocked rather than scheduling it as ready.
2. Read existing `plan.md`, `tasks.md`, and `claims.md` before refining them. Extract
   contribution IDs from the proposal; if absent, assign stable C-IDs in the plan
   and queue without silently editing the proposal.
3. Write or refine `plan.md` from `.research/templates/plan-template.md`. Cover
   architecture where needed, evaluation methodology, datasets, baselines, metrics,
   falsifiers, variability, and key decisions with rejected alternatives. Use the
   paper-type skeleton for relevant proof obligations. Show the design and resolve
   critical unknowns before treating its task list as ready to execute.
4. Declare the code and evaluation directories, honoring the existing project
   layout (default `./src/`; legacy `./design/` is valid). Keep real code, data,
   experiment outputs, and manuscript source outside `.research/`.
5. Follow `<bundle>/guides/task-planning.md` to create or refine `tasks.md` from the
   settled design. Preserve IDs, checkbox states, done-notes, and dependency history.
   Every task has a done-when criterion. Manuscript tasks remain `[USER-LED]` and
   default implementation skips them. Report counts and changes to both files.
6. If legacy `tasks/design.md`, `tasks/eval.md`, or `tasks/paper.md` exist, migrate
   their design/queue content only when requested, carrying state and leaving the
   originals intact. Never replace an existing plan or queue with a blank template.

## Validate

- Every metric and evaluation task ties to a claim ID and a falsifier.
- Baselines include the default and a fairly tuned strong alternative where relevant.
- Design choices name alternatives and the declared layout matches the project.
- The queue matches the design, dependencies resolve, and completed work retains its history.
- Evidence-blocked Paper tasks name the claim and Eval task that will unblock them.
- No experiment or manuscript task was executed as a side effect of planning.

## Completion

Report both paths, design changes, task counts, and unresolved decisions.
End with `Next: /research.implement` when the queue is ready; otherwise name the
upstream decision that needs work. A Next suggestion does not execute the next stage.
