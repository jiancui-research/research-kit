---
description: Turn the proposal + feasibility into three ordered plans — a design/build plan, an experiment (evaluation) plan, and a paper section plan — into .research/tasks/.
argument-hint: optional steering (e.g. "security venue, focus coverage over severity" or "system build is heavy, use spec-kit")
---

## User input

The user request arrives via the $ARGUMENTS placeholder. Treat it as steering on emphasis, venue, or how heavy the build is — not the whole task list.

## What this phase is

This is the planning phase. It absorbs the old plan stage and fans out into **three** parallel work plans, one per lane:

- **`tasks/design.md`** — the system's architecture, project layout & naming, and the **build** task list. `/research.design` turns this into actual code. **Paper-type aware:** heavy for systems/defense, medium for attack/benchmark, **skipped or minimal for measurement / SoK** (nothing is built).
- **`tasks/experiment.md`** — the **evaluation** plan: an experiment-design header (methodology, baselines, datasets, metrics, threat model, evaluation design, ethics) plus an experiment task list. Build no longer lives here; it moved to the design lane.
- **`tasks/paper.md`** — one task per section, tagged READY vs BLOCKED-on-claim.

The three are the parallel work plan: `design` builds the system, `experiment` evaluates it (filling `claims.md`), and `paper` writes sections — kept in sync by `claims.md` and `/research.analyze`.

## Steps

1. **Read context.**
   - Read `./.research/memory/constitution.md` if it exists (skip silently otherwise) and honor its principles and writing voice.
   - Read `./.research/proposal.md` (required upstream). If missing, stop and tell the user to run `/research.proposal` first.
   - Read `./.research/feasibility.md` (required upstream — it gates this phase). If missing, stop and tell the user to run `/research.feasibility` first. If its verdict is NO-GO or PIVOT, stop and route back to `/research.proposal` instead of planning.
   - Read `./.research/related-work.md` if present (for baselines and the closest prior systems to compare against).
   - From `proposal.md`, extract: paper type (measurement / attack / defense / benchmark / systematization (SoK)), target venue, the gap, the contributions, the research questions, and assign each contribution a claim id (C1, C2, …) if one is not already assigned.

2. **Load the skeletons.**
   - `tasks/design.md` from `.research/templates/tasks-design-template.md` (skip for measurement / SoK — see step 3).
   - `tasks/experiment.md` from `.research/templates/tasks-experiment-template.md`.
   - `tasks/paper.md` from `.research/templates/tasks-paper-template.md`.
   - Layer in the matching `.research/templates/paper/<type>.md` so all three files inherit that type's proof obligation and section order:
     - measurement -> defensible dataset + methodology + a surprising finding
     - attack -> a working exploit + evidence it is not a corner case
     - defense -> a mechanism that stops the threat + a quantified cost
     - benchmark -> concrete task tuple + dataset + metrics + 3-5 baselines
     - systematization (SoK) -> a novel, MECE-ish taxonomy + lessons found in no single prior paper

3. **Write `tasks/design.md` — the design / build lane (paper-type aware).** For papers that build something (systems, defense, attack tool / PoC, benchmark harness), fill the design template: the **system overview + a workflow diagram**, the **key design decisions + rejected alternatives**, the **project layout & naming** (code goes in the project's `./design/` folder, a sibling of `.research/`; `.research/` stays for docs), and the **build task list** (one task per component, a done-when criterion, `[spec-kit]` / `[dev]` flag on heavy builds). This doc is both the spec `/research.design` implements and the source for the paper's System Design section. **For measurement / SoK** there is no system to build: skip this file and keep any light data-obtain tasks in `tasks/experiment.md` instead (note that choice in one line).

4. **Write the experiment-design header of `tasks/experiment.md`** — the PLAN-KEEP block of `.research/templates/tasks-experiment-template.md`. This is the **evaluation** plan. Fill every dimension it lists (methodology, baselines, datasets, metrics, threat model, evaluation design, ethics/disclosure/artifact); keep it tight and specific — numbers and named artifacts over adjectives — and let the layered `paper/<type>.md` say which dimensions are load-bearing for this type. For a build-paper, reference the system in `tasks/design.md` rather than re-describing its architecture here. Do not restate the dimension definitions; they live in the template.

5. **Write the experiment task list of `tasks/experiment.md`**, sequenced so the experiment that would kill the paper if it fails runs first. One task per experiment, each tied to exactly one primary claim id (`-> C2`); each names dataset, baselines, metric, and the predicted result / falsifier. Every contribution's claim id must appear on at least one experiment task; every experiment task must serve a claim. Flag any contribution with no experiment as an **overclaim to rescope** and any experiment serving no claim as **scope creep**. (The system under evaluation is built by `/research.design`; only measurement / SoK, which have no design lane, may keep a light **obtain / construct data** task here.)

6. **Write `tasks/paper.md`** from its template: one task per section, in the paper-type skeleton's order (from `.research/templates/paper/<type>.md`). Tag each task:
   - **READY** — framing sections that need no result: intro, related work, method / attack-design / construction, threat model, background. These can be written immediately, in parallel with experiments.
   - **BLOCKED on claim Cx** — results-dependent sections: evaluation / findings, abstract, conclusion (and any discussion that quotes a number). Name the exact claim id(s) each section waits on, so it unblocks the moment `claims.md` marks them supported.
   - Keep one task per section, in order; do not invent sections the skeleton does not have, and drop a skeleton section only with a one-line reason.

7. **Validate** against this short checklist before writing:
   - For a build-paper, `tasks/design.md` has a system diagram, design decisions with rejected alternatives, a concrete project layout, and build tasks with done-when criteria; for measurement / SoK, the design lane is correctly skipped.
   - The experiment header discharges the paper type's proof obligation; nothing load-bearing is hand-waved.
   - Every contribution / research question maps to at least one experiment task via a claim id; every experiment task serves a claim.
   - Baselines, datasets, and metrics are concrete (named, sized, operationally defined), not placeholders.
   - Threat model is present and venue-appropriate for attack / defense, with an out-of-scope line.
   - Each metric has a variance-reporting plan; any automatic / LLM-judge metric has a validation step.
   - Heavy builds are flagged `[spec-kit]` or `[dev]` and point at a repo (in `tasks/design.md`); build does not leak back into the experiment task list.
   - `tasks/paper.md` has one task per skeleton section in order, each tagged READY or BLOCKED-on-claim with the right claim ids.

8. **Write** the files (`mkdir -p ./.research/tasks` first): `./.research/tasks/design.md` (unless skipped for measurement / SoK), `./.research/tasks/experiment.md`, and `./.research/tasks/paper.md`. Do not overwrite existing user content silently: if any file exists, preserve its text and clearly mark what you changed.

## Completion

Report the paths written (`./.research/tasks/design.md` if applicable, `./.research/tasks/experiment.md`, `./.research/tasks/paper.md`). End with: `Next: /research.design, /research.experiment, and /research.paper (run in parallel, synced by claims.md + /research.analyze)`.
