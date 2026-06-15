---
description: Survey prior work and position the contribution; write .research/related-work.md.
argument-hint: optional pointers to key prior work, themes, or the closest baselines
---

## User input
The user request arrives via the $ARGUMENTS placeholder (e.g., names of must-cite works, themes to group by, or the single closest baseline).

## Steps
1. Read `./.research/memory/constitution.md` if present (skip silently otherwise). Read `./.research/idea.md` for the problem, gap, contributions, RQs, venue, and paper type. If `idea.md` is missing, say so and stop, pointing to `/research.idea`.
2. Decide an organizing structure from the idea's framing (do NOT default to a flat survey):
   - **Thematic grouping** when prior work spans different formulations of the problem (3-5 works per theme).
   - **Methodological grouping** when the contribution is a method (e.g., classical vs learning-based vs hybrid).
   - **By generation** when the work is a clear successor to a visible progression.
   - **Funnel** (broad area -> themes -> your niche) as a safe default.
3. For each group, write a synthesis paragraph, never a shopping list. Use the per-paragraph scaffold:
   `<Theme topic sentence>. A line of work approaches this by <shared idea>, differing mainly in <axis>. These methods, however, all assume <constraint> / stop at <boundary>. In contrast, our work <delta>.`
   Every paragraph ends with an explicit delta sentence positioning this paper.
4. Treat the closest 2-3 baselines generously (no strawmen) and contrast them directly. Name the single closest prior work and add a note to forward-reference it in the Introduction.
5. Close with a gap-stating final paragraph the reader can restate in one sentence:
   `To our knowledge, no prior work addresses <the specific cell>: existing systems either <do A but not B> or <do B but not A>. We close this gap by <one-line contribution>.`
6. **Paper-type aware:** for benchmark, measurement, or systems papers, also draft a comparison table (rows = prior work, columns = the dimensions that matter for your contribution) so the gap is visually obvious. Pull dimensions from `templates/paper/<type>.md` if present.
7. Keep Background (concepts needed to follow the technical sections) separate from Related Work (closest prior systems and the delta). Note that the merge-vs-split choice should match the target venue's recent papers; flag this for the user to check.
8. (Optional) For breadth, the user may hand off to a deep-research workflow or skill to gather and cluster citations before you synthesize. This is optional, not required; if used, fold its output back into the structure above rather than pasting raw lists.

## Validate against a short checklist
- A reader can state the gap in one sentence after the section.
- Every paragraph synthesizes (groups + delta); no `A did X, B did Y, C did Z` paragraphs.
- The closest 2-3 baselines are named and contrasted generously.
- The single closest prior work is flagged for an Introduction forward reference.
- A comparison table is present for benchmark/measurement/systems papers.
- Background and Related Work are not conflated; venue convention is flagged for the user.
- Limitations are not apologized for here (those belong in the Limitations section).

## Completion
Write/update `./.research/related-work.md`, starting from `templates/related-work-template.md`, creating `./.research/` as needed and never overwriting user content silently. Report the path and end with: `Next: /research.plan`.
