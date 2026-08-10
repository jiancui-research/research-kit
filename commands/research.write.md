---
description: Write or revise one manuscript section - reads the whole paper and states its argument before any prose, then outlines, revises, critiques, or drafts.
argument-hint: section, optionally with a mode (e.g. "related-work", "revise eval - the ASR moved to 31%", "draft intro")
---

## User input

The user request arrives via the $ARGUMENTS placeholder. It names the section to work on, and
may name a mode (`revise`, `critique`, `draft`) or the reason for a change. If it is empty, ask
which section - never pick one silently.

## What this phase is

The section-writing entry point. It is the same work `/research.implement paper <section>` does,
reachable by its own name because writing a section is a thing you do on its own, not only while
walking the task queue. Both commands follow one shared procedure so they cannot drift.

Use this when you want to write or change a section. Use `/research.implement` when you are
working the queue and a Paper task comes up - that path also updates the task's status.

## Steps

1. Read `./.research/memory/constitution.md` if it exists (for venue, paper type, and writing
   voice); skip silently otherwise.
2. Resolve the manuscript: use the valid path on line 1 of `./.research/paper-repo`; else ask for
   an existing local path; else fall back to `./paper/`. If none resolves, say so and stop -
   creating a manuscript repo belongs to `/research.implement`, not here.
3. Follow `.research/templates/sections/manuscript-procedure.md` end to end. That file holds the
   procedure: read the whole paper and show the argument brief, load the paper-type and section
   craft guides, pin the section's job in four lines, choose the mode, run the blast radius on a
   revision, and write.
4. Write to the section's file in the manuscript, or to a labeled `.outline.md` / `.critique.md`
   beside it. Never silently overwrite existing prose.
5. If `./.research/tasks.md` has a Paper task for this section, note that its status was **not**
   updated - say so, and point at `/research.implement <task-id>` for the run that does. This
   command deliberately does not touch the queue.

## Validate

- The whole manuscript was read and the argument brief was shown before any prose.
- The section's claim, evidence, objection, and boundary were settled first.
- Default was outline; full prose only after the explicit word `draft`.
- A revision restated why the change was asked for, reported the blast radius, and proposed
  before applying.
- No number, citation, or system name was invented; gaps are marked `[UNVERIFIED]` / `[cite?]`.

## Completion

Report the path written, which craft guides were loaded, every gap left behind, and anything the
blast radius surfaced. End with `Next: /research.write <next section>`, or `Next:
/research.analyze` when the draft is complete enough to audit.
