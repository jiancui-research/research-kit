---
description: Establish or update the research constitution (quality principles + writing voice + venue norms) at .research/memory/constitution.md
argument-hint: optional focus areas, e.g. "security venue, measurement, strict reproducibility"
---

## User input

The user's focus areas (paper field, target venue family, priorities such as
reproducibility/ethics/honest reporting, or "tighten the voice section") arrive
via the `$ARGUMENTS` placeholder. Treat it as optional steering, not a full spec.

## What this command owns

This is the FIRST command in the pipeline. It creates the `.research/` scaffold
and writes ONE artifact: `.research/memory/constitution.md`. Every later command
reads this file, so keep it durable, paper-type-agnostic, and project-wide.

## Steps

1. **Scaffold.** `mkdir -p` the working tree if missing:
   `.research/memory`, `.research/tasks`, `.research/review`, `.research/rebuttal`,
   `.research/ae`.
   (`proposal.md`, `related-work.md`, `feasibility.md`, `claims.md`, and
   `analyze-report.md` are flat files at `.research/` root - no dirs needed. Each
   lane's actual work lands in a root-level folder created by its own command -
   `feasibility/`, the code folder `plan.md` declares (default `src/`, legacy
   `design/`), `eval/`, `paper/` - never inside `.research/`. The manuscript may
   instead live in a dedicated sibling repo recorded in `.research/paper-repo`.)

2. **Read existing constitution if present.** If `.research/memory/constitution.md`
   already exists, read it and treat this run as an UPDATE: preserve the user's
   edits, fold `$ARGUMENTS` in, and report a short diff of what changed. Never
   silently overwrite hand-written principles.

3. **Seed from the template if absent.** If no constitution exists, read
   `.research/templates/constitution-template.md` and write it to
   `.research/memory/constitution.md`, then specialize it using `$ARGUMENTS` (set the
   venue family, foreground the user's stated priorities). If `$ARGUMENTS` is empty,
   write it through unchanged apart from the focus line, and say so.
   The template is **required**: if it is missing, say so, route to `/research.init`,
   and stop - never reconstruct a constitution from memory.

4. **Specialize, do not bloat.** Keep it readable in one screen-scroll per section.
   Add at most a few user-specific bullets; do not invent project facts, names,
   datasets, or results. Venue norms are a MENU, not a fixed template - flag which
   conventions apply to the user's venue family (security expects an explicit
   threat-model beat and a roadmap sentence; ML venues front-load related work and
   often omit both). When in doubt, tell the user to read 3 recent accepted papers
   from their target venue.

5. **Validate** against the checklist below, then write the file.

## Quality checklist

- Scaffold created; only `.research/memory/constitution.md` written by this command.
- Existing user edits preserved on update; changes reported, nothing silently clobbered.
- Quality principles cover rigor, reproducibility, honest reporting, ethics, integrity.
- Voice section is motivation-first / NABC, gap framing, scoped novelty, active voice.
- Venue norms framed as a menu; security-vs-ML differences flagged; no invented facts.
- Readable, paper-type-agnostic, free of project-specific names/data/results.

## Completion

Report the path `.research/memory/constitution.md` and whether it was created or
updated. Next: /research.proposal
