---
description: Turn the proposal + feasibility into the study's technical design at .research/plan.md - architecture, evaluation design, key decisions, project layout. Stable; tasks derive from it.
argument-hint: optional steering (e.g. "security venue, coverage over severity" or "code goes in ./src/core")
---

## User input
The user request arrives via the $ARGUMENTS placeholder: steering for the design (venue emphasis, layout conventions, constraints). May be empty.

## What this phase is
The spec-kit `plan` analogue for research: the **study design**, separated from the work queue. `plan.md` holds what a reviewer would interrogate - architecture, evaluation methodology, decisions with rejected alternatives - and stays stable while `tasks.md` (next stage) churns. It is also the source for the paper's System Design section and the contract `analyze` checks reality against.

## Steps
1. Read `./.research/memory/constitution.md` if it exists; skip silently otherwise.
2. Read the upstream artifacts: `./.research/proposal.md` (required - stop and route to `/research.proposal` if missing; extract paper type, venue, gap, contributions, RQs, and assign claim ids C1, C2, ... if absent) and `./.research/feasibility.md` (required - stop and route to `/research.feasibility` if missing; a NO-GO means do not plan). Read `./.research/related-work.md` if present (baselines, closest prior systems).
3. **Legacy migration.** If `./.research/tasks/design.md` or `tasks/eval.md` exist from the pre-0.7 layout and `plan.md` does not, offer to migrate: pull their plan halves (architecture, decisions, evaluation-design header, layout) into `plan.md` and leave the old files untouched for reference.
4. Write `./.research/plan.md` from `.research/templates/plan-template.md` (`mkdir -p ./.research` first; never overwrite silently - re-runs refine and report changes). Paper-type aware throughout: architecture heavy for systems/defense, medium for attack/benchmark, minimal or absent for measurement/SoK; layer `.research/templates/paper/<type>.md` into the evaluation design.
5. **Declare the project layout**, including where implementation code lives - default `./src/`, or the project's own convention from $ARGUMENTS; honor an existing `./design/` folder as legacy. `/research.implement` will build exactly there.

## Validate (short checklist)
- Architecture shows the end-to-end path, or states "nothing built" for measurement/SoK.
- Every metric ties to a claim id; baselines include the default AND a fairly tuned SOTA.
- Each key decision names its rejected alternative.
- The code-folder declaration is explicit and honors legacy layouts.
- No task list in this file - tasks belong to `/research.tasks`.

## Completion
Report `./.research/plan.md` and the declared code folder. End with: `Next: /research.tasks` (derive the work queue from this plan).
