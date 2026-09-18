# Maintain the writing style file

Loaded by `/research.write` and explicitly selected manuscript work in
`/research.implement`. Before outlining, drafting, or revising a section, complete
the example-paper step below. Explicit `style` input selects preference work
without requiring a manuscript.

The persistent file stays at `./.research/writing/style.md`. Its three sources are:

| Source | Destination | Refresh behavior |
|---|---|---|
| Papers in `./.research/writing/samples/` or user-selected paths/links | Register, openings, outline shapes, sentence habits, vocabulary | Rebuild from samples on request |
| Explicit user instructions | Standing instructions | Preserve; append dated instructions |
| Preferences inferred from the user's edits | Learned from edits | Preserve; propose inferred rules before recording |

## Before section writing: choose example papers or explicitly skip

This is a required decision with an opt-out. Resolve it before outlining, drafting,
or revising, including small revisions. Critique-only, consistency checks,
manuscript setup, and recording an instruction do not require this step.

1. Read the **Example papers** section of `writing/style.md` when present, plus
   enough of the manuscript or available project framing to identify the topic and
   paper type. Reuse selected papers and their recorded analysis for this project;
   do not ask again for every section or reread unchanged samples unnecessarily.
   Honor a recorded project-wide skip. A request to skip only this time applies
   only to that request. Revisit the choice when the user changes the research
   topic or asks to change examples, not merely because they start a new section.
2. Aim for **2–3 distinct papers close to this research topic and paper type**.
   An existing collection of more than three suitable papers is fine. Reuse
   samples already supplied for this project, including a legacy style file's
   identifiable sources. The style file's existence alone is not evidence that
   papers were chosen: instructions-only files and template placeholders do not
   satisfy this step. Papers cited in related work are candidates, not automatically
   approved writing examples. If supplied samples have a different topic or type,
   explain the mismatch and let the user keep them deliberately or choose others.
3. If there is no usable selection or explicit skip, ask once:
   **"Which 2–3 papers on this topic should we learn from? Share titles, links, or
   local paths, ask me to suggest papers with reasons, or say 'skip examples'."**
   Wait for the answer before section work. Silence, urgency, or unavailable
   papers do not mean skip. An explicit skip in the original request already
   answers the question; do not ask again or require a reason.
4. If asked to suggest papers, use the manuscript and any existing literature
   survey as leads. Ask for the topic only when it cannot be established. Search
   and verify primary sources (publisher/proceedings, author page, or preprint),
   and inspect full text before recommending a paper for its writing. Suggest
   2–3 candidates with title, year, source link, topic/type fit, and a concrete
   lesson located in a section or page: how it motivates a gap, orders the
   argument, explains a method, or presents evidence. Do not equate citation count
   or venue prestige with good writing. Label inaccessible full text as unassessed;
   an abstract alone cannot establish its writing quality. Ask the user to select
   from the candidates or skip; suggestions alone are not their selection.
5. Read the selected papers in full and distill their patterns as described below;
   reuse full text already read in this run. At least two readable papers are needed
   for sample-derived common patterns. If fewer are available, name the gap and
   offer replacements or an explicit skip; never invent an analysis. A request to
   proceed with one paper explicitly waives the two-paper requirement; retain its
   individual lessons without calling them shared patterns. Record each
   paper's source, topic/type fit, and specific writing lesson. A useful move seen
   in only one paper may be recorded as that paper's example, not as a shared habit.
6. Keep the decision, date, scope, selected papers, and analysis in the existing
   `.research/writing/style.md` under **Example papers**. Add that section to older
   files without rebuilding their other sections. Set the choice to `selected`
   only after the usable papers have been chosen and analyzed, or to `skipped`
   when the user explicitly declines. Preserve the user's stated scope; an
   unqualified skip applies to this project. Identify a one-request skip by date
   and the requested section/work so it cannot silently carry forward. Do not record a skip as an inferred
   writing preference. With a skip, continue using the manuscript, standing
   instructions, and craft guides; leave sample-derived sections empty if none
   exist. Users can change their choice later.

Learn argument structure, section organization, explanation, and sentence habits.
Borrow patterns, never another paper's prose, findings, or novelty claims. The
manuscript's established terms and formatting still take precedence. Selecting
papers also authorizes recording this analysis in the style file, not changing
the manuscript beyond the requested section work.

## Maintain the style file

1. Read the existing file. If absent, create it from the local
   `.research/templates/style-template.md` when there is a preference or sample
   analysis or an explicit skip to record. Omit template usage notes and unfilled
   placeholders. Do not fill it with guessed preferences.
2. Interpret the request, not just whether its arguments are empty. A bare `style`
   request refreshes from the default samples directory and proposes preferences
   from accessible conversation/edits; absent samples do not block recording an
   explicit instruction. For a more specific request, do only that work:
   - **Suggest examples:** follow the search and recommendation step above without
     requiring a manuscript; use the topic supplied in the request or project notes.
     Await the user's selection before recording candidates as selected or drafting.
   - **Record an instruction:** append it in the user's words with date and context.
     An explicit request to remember it already authorizes that write.
   - **Learn or refresh from samples:** read each supplied sample in full. Follow
     LaTeX includes; count papers, not section files, as independent samples.
     Report unreadable inputs. Distill patterns appearing in at least two samples,
     naming the sample count supporting each pattern. With fewer than two, explain
     the limit and leave the sample-derived sections unchanged. For a new selection,
     record its sources and lessons under Example papers using the decision rules
     above; a style-only analysis can satisfy the next section's prerequisite.
   - **Harvest this conversation or edits:** review only accessible conversation
     and attributable before/after versions. Do not assume every working-tree diff
     was the user's edit. Propose each inferred rule with its evidence; record it
     once confirmed. Skip unavailable history rather than inventing it.
3. Keep Example papers (including the choice and its scope), Standing instructions,
   and Learned from edits during a sample refresh. Preserve the latter two verbatim.
   Update the example choice only when the user changes it or supplies replacement
   papers. A reversal of an instruction is a new dated entry naming what it supersedes.
   Avoid duplicate entries. Keep research findings out of this file.
4. Describe patterns and sentence shapes with slots. Never copy sample sentences
   into this file or the manuscript. Short before/after excerpts from the user's
   own edits may document a preference; full manuscript voice samples stay in the
   conversation, where they are used for comparison rather than reused as prose.
5. If the default samples directory is absent, create it when samples are requested
   and explain the supported formats: `.tex`, `.md`, `.txt`, `.pdf`. Do not copy
   supplied files into the project or commit them unless requested.

Report what was recorded, how many samples were read, and any unconfirmed inferences.
If this was style-only work, stop without drafting or changing the queue. Otherwise
resume the requested section. All later writing loads the same style file.
