---
description: "Write or revise a manuscript section in the paper's style; also learn and maintain writing preferences from samples, instructions, and edits."
argument-hint: "section and optional mode, or style work (e.g. \"draft intro\", \"revise evaluation\", \"style learn from ./samples\", \"style remember: use direct sentences\")"
---

## Preparation

Resolve `<bundle>` from the enclosing installed plugin directory (the skill adapter
supplies it), else `${CLAUDE_PLUGIN_ROOT}`, else the enabled OMP `installPath` in
the nearest project `.omp/plugins/installed_plugins.json` or `~/.omp/plugins/installed_plugins.json`,
else `${RESEARCH_KIT_HOME:-$HOME/.research-kit}`. Use the first candidate containing
`guides/setup.md` and `templates/`; name the installation problem if none resolves.
Read `<bundle>/guides/setup.md` and complete its setup for this command, then resume
the request. Internal guides use this bundle; artifact templates use local copies.

## User input and dispatch

`$ARGUMENTS` names section work (`outline`, `revise`, `critique`, `draft`), a
consistency `check`, or a request to learn/remember writing preferences. Recognize
natural-language style requests as well as a leading `style` keyword. If empty,
ask which section or style task; never pick a section silently.

## Style work

Follow `<bundle>/guides/writing-style.md`. Keep the existing paths
`./.research/writing/style.md` and `./.research/writing/samples/`. Style-only work
needs no manuscript, proposal, plan, or queue and stops after reporting preferences.
For a combined request, maintain the style file first, then work on the section.

## Section work

1. Read project preferences from `./.research/memory/constitution.md` and writing
   preferences from `./.research/writing/style.md` when present.
2. Resolve the manuscript from an explicit path in the request, then a valid path
   on line 1 of `./.research/paper-repo`, then the current repo if it contains the
   manuscript, then `./paper/`. Ask for an existing path only when these fail.
   Do not create or reorganize a manuscript as a side effect of section writing.
3. For an explicit check-only request, follow `<bundle>/guides/consistency.md`,
   report the findings, and stop without editing the manuscript or queue.
4. Before outlining, drafting, or revising, follow **Before section writing** in
   `<bundle>/guides/writing-style.md`: use 2–3 relevant example papers or the user's
   explicit skip. Reuse the project choice; if undecided, ask and wait. Critique-only
   work bypasses this step. The current command's requirement takes precedence over
   older local templates that say to continue without choosing examples.
5. Read the required `.research/templates/sections/manuscript-procedure.md` and
   follow it end to end. Setup fills missing templates; if the required file is
   still unavailable, name the path and stop instead of improvising the procedure.
   Read the whole paper including tables/captions. Show its argument and quote
   three to five real sentences before writing. Load the cross-cutting rhetoric,
   paper-type moves/skeleton, and section craft. Pin the section's claim, evidence,
   objection, and boundary. Outline by default; full prose requires an explicit
   drafting request. Revisions assess affected claims, references, and definitions.
6. Write into the manuscript's actual section file, following its directory,
   extension, naming, macro, and inclusion conventions. For a new LaTeX section,
   wire its inclusion into the manuscript in reading order. Scratch `.outline.md`
   and `.critique.md` outputs stay beside the section and are never included in TeX.
7. Before finishing, follow `<bundle>/guides/consistency.md` for the section and its
   dependencies. Fix within the authorized scope; report broader gaps and remaining
   `[UNVERIFIED]` / `[cite?]` markers. Writing-only projects need no pipeline artifacts.
8. When the user asks to remember a correction, use the writing-style guide to
   update the same style file. Inferred preferences need evidence and confirmation;
   explicit instructions to remember a preference need no second confirmation.
9. Keep `tasks.md` unchanged. For work tied to a queued Paper task, point to
   `/research.implement <task-id>` to perform the work with queue bookkeeping.

## Validate

- Outline/draft/revise work used selected, analyzed examples or an explicit skip;
  the choice and its scope were preserved in the same style file.
- The whole manuscript was read; the argument brief includes real quoted sentences.
- New prose matches sentence construction, terms, person, tense, numbers, and macros.
- Definite noun phrases, comparisons, and partitives have explicit referents.
- Relevant rhetoric and section guides were loaded; missing optional guides were named.
- The section's job and evidence were settled before prose, with no invented results.
- A revision reports its reason and affected passages; existing prose is never overwritten silently.
- Style refreshes preserve Standing instructions and Learned from edits.
- Consistency was checked; no unrelated artifact or queue state was changed.

## Completion

Report paths written or changes proposed, style updates if any, loaded guidance,
consistency findings, and unresolved gaps. Suggest `/research.write <next section>`
or `/research.review` for a paper ready for an outside reader. Style-only work
suggests `/research.write <section>`. Do not run the next stage automatically.
