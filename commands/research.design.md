---
description: Implement the system from tasks/design.md into actual code (in the project's ./design/ folder), following the architecture and layout. The build lane; eval evaluates what this produces.
argument-hint: which component(s) to build or update — or paste a build result / blocker to record
---

## User input

The user request arrives via the $ARGUMENTS placeholder. It may name a component to build, an existing one to revise, or report a blocker. If empty, work the build task list in `./.research/tasks/design.md` top to bottom.

## What this phase is

This is the **build lane** — the spec-kit `implement` analogue. It reads the architecture and build task list in `./.research/tasks/design.md` and produces **actual code** in the project's **`./design/`** folder — a sibling of `.research/` at the project root (the project is one repo under `~/Projects`, outside the vault). Keep the split clean: `.research/` holds the tracking docs (the plan and build status), `./design/` holds the code. The system this produces is exactly what `/research.eval` then evaluates.

**Paper-type aware.** This lane is heavy for systems/defense (a full system), medium for attack (a PoC / exploit) and benchmark (a construction harness + dataset). For **measurement / SoK** papers there is usually nothing to build — if `tasks/design.md` is absent or empty, say so and point the user to `/research.eval` rather than inventing a system.

## Steps

1. **Read context.**
   - Read `./.research/memory/constitution.md` if present (skip silently otherwise) and honor its principles.
   - Read `./.research/tasks/design.md` (required upstream). If it is missing or empty, tell the user this paper type has no design lane and route to `/research.eval`. Otherwise pull the architecture, the components, the project layout & naming, and the build task list.
   - Read `./.research/proposal.md` for the paper type and the contribution the system must embody.

2. **Locate the `./design/` folder.** Build into `./design/` at the project root (sibling of `.research/`), following the layout & naming in the Project-layout section of `tasks/design.md`. Create `./design/` if it does not exist yet. Never write code inside `.research/` (that is for tracking docs only).

3. **Build, following the design.** Work the build task list in order, implementing each component per the architecture and the repo's folder / naming conventions. Honor `$ARGUMENTS` if it names a specific component. Keep the build faithful to `tasks/design.md`; if reality forces a design change, make it, but **note the deviation** so the design doc and the other lanes can be re-synced (step 5).
   - For a task flagged `[spec-kit]`, treat it as a heavy build that warrants its own spec-driven-development pass in that repo — set it up there rather than dumping code inline.

4. **Record status, not prose.** Check off completed build tasks in `./.research/tasks/design.md` (`[x]` with a one-line "done: <what landed, where>"). Do not paste source code into `.research/`; reference file paths under `./design/`. Leave a blocked task as `[ ] BLOCKED: <reason>`.

5. **Surface design drift.** If building changed the architecture (a component split, a flow reordered, an interface changed), update the System-overview / decisions in `tasks/design.md` to match what you actually built, and flag that `/research.eval` (it may now test the wrong thing) and `/research.paper` (the System Design section) need re-syncing. Do not edit those lanes yourself — `/research.analyze` detects the drift and routes the re-runs.

## Validate (short checklist)

- The code lives in `./design/` (project root, sibling of `.research/`), never inside `.research/`.
- What was built matches the architecture + project layout in `tasks/design.md` (or the doc was updated to match reality, with the deviation noted).
- Build tasks are checked off with a one-line "done"; blockers are explicit.
- For measurement / SoK with no design lane, the command correctly did nothing and routed to `/research.eval`.
- Any design change is flagged for re-sync, not silently absorbed.

## Completion

Report what landed under `./design/` and which build tasks are now done / blocked, and update `./.research/tasks/design.md`. Then: `Next: /research.eval` (evaluate what you built) and `/research.paper` (write the System Design section from `tasks/design.md`). If the design changed, add: run `/research.analyze` to re-sync eval + paper.
