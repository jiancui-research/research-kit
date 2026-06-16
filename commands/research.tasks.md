---
description: Turn the proposal + feasibility into two ordered task lists — an experiment-design plan (build/obtain + experiments) and a paper section plan (READY vs BLOCKED-on-claim) — into .research/tasks/.
argument-hint: optional steering (e.g. "security venue, focus coverage over severity" or "system build is heavy, use spec-kit")
---

## User input

The user request arrives via the $ARGUMENTS placeholder. Treat it as steering on emphasis, venue, or how heavy the build is — not the whole task list.

## What this phase is

This is the planning phase. It absorbs the old plan stage: the strong **experiment-design** content (methodology, baselines, datasets, metrics, threat model, evaluation design, ethics) becomes the HEADER of `tasks/experiment.md`, followed by an ordered task list. It also emits `tasks/paper.md`, one task per section. The two files are the parallel work plan: `experiment` builds artifacts and runs tests; `paper` writes sections, blocked only where it needs a result.

## Steps

1. **Read context.**
   - Read `./.research/memory/constitution.md` if it exists (skip silently otherwise) and honor its principles and writing voice.
   - Read `./.research/proposal.md` (required upstream). If missing, stop and tell the user to run `/research.proposal` first.
   - Read `./.research/feasibility.md` (required upstream — it gates this phase). If missing, stop and tell the user to run `/research.feasibility` first. If its verdict is NO-GO or PIVOT, stop and route back to `/research.proposal` instead of planning.
   - Read `./.research/related-work.md` if present (for baselines and the closest prior systems to compare against).
   - From `proposal.md`, extract: paper type (measurement / attack / defense / benchmark / systematization (SoK)), target venue, the gap, the contributions, the research questions, and assign each contribution a claim id (C1, C2, …) if one is not already assigned.

2. **Load the skeletons.**
   - `tasks/experiment.md` from `.research/templates/tasks-experiment-template.md`.
   - `tasks/paper.md` from `.research/templates/tasks-paper-template.md`.
   - Layer in the matching `.research/templates/paper/<type>.md` so both files inherit that type's proof obligation and section order:
     - measurement -> defensible dataset + methodology + a surprising finding
     - attack -> a working exploit + evidence it is not a corner case
     - defense -> a mechanism that stops the threat + a quantified cost
     - benchmark -> concrete task tuple + dataset + metrics + 3-5 baselines
     - systematization (SoK) -> a novel, MECE-ish taxonomy + lessons found in no single prior paper

3. **Write the experiment-design header of `tasks/experiment.md`** — the PLAN-KEEP block of `.research/templates/tasks-experiment-template.md`. Fill every dimension it lists (methodology, baselines, datasets, metrics, threat model, evaluation design, ethics/disclosure/artifact); keep it tight and specific — numbers and named artifacts over adjectives — and let the layered `paper/<type>.md` say which dimensions are load-bearing for this type. Do not restate the dimension definitions here; they live in the template.

4. **Write the ordered task list of `tasks/experiment.md`**, in two buckets, sequenced so the experiment that would kill the paper if it fails runs first:
   - **Build / obtain** (the artifact: system / dataset / tool). One task per artifact to construct or acquire. For each, name the deliverable and a done-when criterion. **Flag any heavy system build**: tag it `[spec-kit]` if it warrants spec-driven development in its own repo, or `[dev]` for normal development, and link or name the repo it will live in (per the global layout: under `~/Projects/<repo>`, never inside the vault). Light data wrangling or a one-off script needs no flag.
   - **Experiments.** One task per experiment, each tied to exactly one primary claim id (`-> C2`). Each task names dataset, baselines, metric, and the predicted result / falsifier. Every contribution's claim id must appear on at least one experiment task; every experiment task must serve a claim. Flag any contribution with no experiment as an **overclaim to rescope** and any experiment serving no claim as **scope creep**.

5. **Write `tasks/paper.md`** from its template: one task per section, in the paper-type skeleton's order (from `.research/templates/paper/<type>.md`). Tag each task:
   - **READY** — framing sections that need no result: intro, related work, method / attack-design / construction, threat model, background. These can be written immediately, in parallel with experiments.
   - **BLOCKED on claim Cx** — results-dependent sections: evaluation / findings, abstract, conclusion (and any discussion that quotes a number). Name the exact claim id(s) each section waits on, so it unblocks the moment `claims.md` marks them supported.
   - Keep one task per section, in order; do not invent sections the skeleton does not have, and drop a skeleton section only with a one-line reason.

6. **Validate** against this short checklist before writing:
   - The experiment header discharges the paper type's proof obligation; nothing load-bearing is hand-waved.
   - Every contribution / research question maps to at least one experiment task via a claim id; every experiment task serves a claim.
   - Baselines, datasets, and metrics are concrete (named, sized, operationally defined), not placeholders.
   - Threat model is present and venue-appropriate for attack / defense, with an out-of-scope line.
   - Each metric has a variance-reporting plan; any automatic / LLM-judge metric has a validation step.
   - Heavy system builds are flagged `[spec-kit]` or `[dev]` and point at a repo; data-only tasks are not over-flagged.
   - `tasks/paper.md` has one task per skeleton section in order, each tagged READY or BLOCKED-on-claim with the right claim ids.

7. **Write** both files: `./.research/tasks/experiment.md` and `./.research/tasks/paper.md` (`mkdir -p ./.research/tasks` first). Do not overwrite existing user content silently: if either file exists, preserve their text and clearly mark what you changed.

## Completion

Report the paths `./.research/tasks/experiment.md` and `./.research/tasks/paper.md`. End with: `Next: /research.experiment and /research.paper (run in parallel, synced by claims.md)`.
