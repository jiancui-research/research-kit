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
3. Read `.research/templates/sections/manuscript-procedure.md`. It is **required**: if it is
   missing, say so, route to `/research.init` (it is no-clobber, so it only fills the gap), and
   stop - never reconstruct the procedure from memory or context. Then follow it end to end. That file holds the
   procedure: read the whole paper, show the argument brief **and a voice sample of the paper's
   own terms, person, tense, and number formatting**, load the paper-type skeleton plus the
   cross-cutting, per-type, and per-section craft guides, pin the section's job in four lines,
   choose the mode, run the blast radius on a revision, and write.
4. Write to the section's own file in the manuscript's existing layout (typically
   `sections/<name>.tex`, named the way `main.tex` names its siblings), or to a labeled
   `.outline.md` / `.critique.md` beside it. A new section file also needs its `\input` line in
   `main.tex`. Never silently overwrite existing prose.
5. If `./.research/tasks.md` has a Paper task for this section, note that its status was **not**
   updated - say so, and point at `/research.implement <task-id>` for the run that does. This
   command deliberately does not touch the queue.

## Validate

- The whole manuscript was read, and the argument brief plus voice sample were shown before any
  prose, including three to five sentences quoted verbatim from the manuscript.
- New prose reuses the paper's established terms, person, tense, and number formatting; no term
  the paper already fixed was swapped for a synonym.
- Sentences are built the way the paper builds them - no cleft construction, aphorism, or
  literary connective the manuscript itself never uses.
- The cross-cutting moves, the paper type's own moves, and the section guide were all applied.
- The section's claim, evidence, objection, and boundary were settled first.
- Default was outline; full prose only after the explicit word `draft`.
- A revision restated why the change was asked for, reported the blast radius, and proposed
  before applying.
- No number, citation, or system name was invented; gaps are marked `[UNVERIFIED]` / `[cite?]`.

## Completion

Report the path written, which craft guides were loaded, every gap left behind, and anything the
blast radius surfaced. End with `Next: /research.write <next section>`, or `Next:
/research.analyze` when the draft is complete enough to audit.
