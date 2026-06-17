---
description: Implement the system from tasks/design.md into actual code (in ~/Projects/<repo>), following the architecture and repo layout. The build lane; experiment evaluates what this produces.
argument-hint: which component(s) to build or update — or paste a build result / blocker to record
---

## User input

The user request arrives via the $ARGUMENTS placeholder. It may name a component to build, an existing one to revise, or report a blocker. If empty, work the build task list in `./.research/tasks/design.md` top to bottom.

## What this phase is

This is the **build lane** — the spec-kit `implement` analogue. It reads the architecture and build task list in `./.research/tasks/design.md` and produces **actual code**, in the project repo under `~/Projects/<repo>` (never inside the Obsidian vault, never inside `.research/`). `.research/` only tracks the plan and build status; the code itself lives in its own repo. The system this produces is exactly what `/research.experiment` then evaluates.

**Paper-type aware.** This lane is heavy for systems/defense (a full system), medium for attack (a PoC / exploit) and benchmark (a construction harness + dataset). For **measurement / SoK** papers there is usually nothing to build — if `tasks/design.md` is absent or empty, say so and point the user to `/research.experiment` rather than inventing a system.

## Steps

1. **Read context.**
   - Read `./.research/memory/constitution.md` if present (skip silently otherwise) and honor its principles.
   - Read `./.research/tasks/design.md` (required upstream). If it is missing or empty, tell the user this paper type has no design lane and route to `/research.experiment`. Otherwise pull the architecture, the components, the repo layout & naming, and the build task list.
   - Read `./.research/proposal.md` for the paper type and the contribution the system must embody.

2. **Locate the repo.** Use the repo named in the Repo-layout section of `tasks/design.md` (under `~/Projects/<repo>`). If it does not exist yet, create it there — outside the vault, never inside `.research/` — with the folder structure and naming from `tasks/design.md`. Confirm the path with the user before writing a large amount of new code into a fresh location.

3. **Build, following the design.** Work the build task list in order, implementing each component per the architecture and the repo's folder / naming conventions. Honor `$ARGUMENTS` if it names a specific component. Keep the build faithful to `tasks/design.md`; if reality forces a design change, make it, but **note the deviation** so the design doc and the other lanes can be re-synced (step 5).
   - For a task flagged `[spec-kit]`, treat it as a heavy build that warrants its own spec-driven-development pass in that repo — set it up there rather than dumping code inline.

4. **Record status, not prose.** Check off completed build tasks in `./.research/tasks/design.md` (`[x]` with a one-line "done: <what landed, where>"). Do not paste source code into `.research/`; reference file paths in the repo. Leave a blocked task as `[ ] BLOCKED: <reason>`.

5. **Surface design drift.** If building changed the architecture (a component split, a flow reordered, an interface changed), update the System-overview / decisions in `tasks/design.md` to match what you actually built, and flag that `/research.experiment` (it may now test the wrong thing) and `/research.paper` (the System Design section) need re-syncing. Do not edit those lanes yourself — `/research.analyze` detects the drift and routes the re-runs.

## Validate (short checklist)

- The code lives in `~/Projects/<repo>`, outside the vault and outside `.research/`.
- What was built matches the architecture + repo layout in `tasks/design.md` (or the doc was updated to match reality, with the deviation noted).
- Build tasks are checked off with a one-line "done"; blockers are explicit.
- For measurement / SoK with no design lane, the command correctly did nothing and routed to `/research.experiment`.
- Any design change is flagged for re-sync, not silently absorbed.

## Completion

Report the repo path and which build tasks are now done / blocked, and update `./.research/tasks/design.md`. Then: `Next: /research.experiment` (evaluate what you built) and `/research.paper` (write the System Design section from `tasks/design.md`). If the design changed, add: run `/research.analyze` to re-sync experiment + paper.
