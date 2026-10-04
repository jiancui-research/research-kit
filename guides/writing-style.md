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

## Before section writing: recover or resolve example papers

Ground section writing in relevant examples unless the user explicitly skips them.
Resolve this before outlining, drafting, or revising. Critique-only, consistency
checks, manuscript setup, and recording an instruction do not require this step.

1. **Recover before asking.** Read **Example papers** in `writing/style.md` and
   enough of the manuscript to identify the topic and paper type. If the record is
   missing or incomplete, check `writing/samples/`, legacy style files, relevant
   project notes, and accessible conversation for prior choices and analysis.
   Reuse papers the user selected or demonstrably used as writing examples in
   approved earlier work; record the evidence in the existing style file.
   A citation or an unapproved candidate list is not a selection. Do not infer
   approval merely because an earlier agent wrote an analysis. Report conflicts
   that would change the topic, paper type, or scope; ask only about that conflict.
   Preserve explicit scope: do not extend an explicit section-only choice to
   unrelated work. Honor a project-wide skip. A request-only skip does not carry
   forward. Missing bookkeeping alone is not a reason to repeat an answered question.
2. **Use what is sufficient.** Aim for 2–3 relevant papers, not a mandatory quota.
   One relevant, selected paper with full-text analysis is enough for section work.
   Do not ask for a waiver or more papers merely to reach a count. Use its individual
   lessons, not claims about a shared style. At least two papers are needed only to
   infer shared patterns. Reuse recorded analysis without rereading unchanged papers
   or asking again for every section. An existing collection of more than three
   suitable papers is fine; respect any stricter requirement the user explicitly set.
3. **Honor delegated research.** Distinguish the user's requested outcome:

   - **Suggest only:** when asked to show candidates before deciding, present them
     and await selection. Suggestions alone are not authorization to choose.
   - **Find and choose:** when asked to find suitable writing examples for the
     requested section or to use your judgment, search, choose, analyze, and record
     appropriate papers without another selection approval. Keep any established
     references and respect the requested topic, scope, and selection criteria.
     An unrelated literature search does not delegate writing-example selection.

   For either route, use existing surveys as leads and verify primary sources
   (proceedings, author page, or preprint). Read full text before assessing writing.
   Give each paper's title, year, source, topic/type fit, and a concrete lesson with
   a section/page pointer. Prestige alone is not evidence of useful writing.
   A request only to suggest or select examples does not authorize manuscript edits.
4. **Ask only when unresolved.** If there is no applicable selection, explicit skip,
   or delegated research, ask once: **"Do you have writing examples to reuse, should
   I find and choose suitable papers, or should we skip examples?"** Wait for the
   answer before section work. Silence and urgency do not mean skip or delegation.
   If only the selection record is missing, finish the bounded recovery in step 1
   first. Do not ask the user to repeat a decision supported by available evidence.
5. **Analyze honestly.** Read selected papers in full if their analysis is not
   already available. Unreadable or abstract-only papers do not count as analyzed
   examples; name the gap without inventing lessons. Continue with any sufficient,
   applicable analyzed example, or seek replacements under delegated research.
   If none is usable and replacements are not authorized, offer replacements or
   an explicit skip. A skipped choice permits writing from the manuscript,
   standing instructions, and craft guides without sample-derived patterns.
6. **Keep one record.** In `.research/writing/style.md`, record the date, scope,
   sources, lessons, and selection basis (user-selected, recovered, or agent-selected
   under delegated research). Include the source of a recovered decision or the
   request that delegated selection. Set the choice to `selected` when usable
   papers have been chosen and analyzed, or `skipped` only for an explicit skip.
   Preserve other style sections and the user's stated scope. An unqualified skip
   applies to the project; a request-only skip names its date and section/work.
   Do not invent earlier approval or turn one-paper lessons into shared patterns.
   Users can change the choice later.

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
   - **Suggest or select examples:** follow the research routes above without
     requiring a manuscript; use the topic supplied in the request or project notes.
     Await selection for suggest-only work; choose and record when delegated.
     Neither route authorizes drafting unless the user also requested section work.
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
   Change the example choice only on the user's instruction or within delegated
   selection. Recovery fills missing records without inventing a new choice.
   A reversal of an instruction is a new dated entry naming what it supersedes.
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
