> Loaded by `/research.write` or explicit `/research.implement paper related-work` mode. Craft for the paper's
> related-work section. The upstream survey lives in `.research/related-work.md` (produced by
> `/research.relatedwork`); this guide is about turning it into the section reviewers read.

# Related work

**TL;DR:** Related work is **positioning, not a literature review**. Its job is to make your gap
obvious so the contribution lands. If a reader cannot state your gap in one sentence after
finishing the section, it failed - no matter how many papers it covers.

---

## Core principles

- **Identify the knowledge deficit**, do not summarize what is known.
- **No shopping lists.** "Paper A did X. Paper B did Y." is the single most common reviewer
  complaint about this section. Synthesize into themes; never enumerate.
- **Be generous to prior work.** Position against the *closest* two or three baselines, never
  against strawmen. Dismissiveness reads as insecurity and often reaches a reviewer who wrote
  the work you dismissed.
- **Name the closest one or two papers in the introduction itself**, with a forward reference
  to this section. It saves reviewers hunting and pre-empts "you missed X".

## Choose a spine

Pick one and hold it. The default is the funnel.

- **Funnel (default).** Broad area, narrowing themes, then the specific cell your paper
  occupies. The last paragraph restates the gap.
- **Thematic.** Group by problem framing, three to five works per theme. Best when prior work
  frames the problem differently from each other. Each theme ends with what is missing.
- **Methodological.** Group by technique (classical / learning-based / hybrid). Best when the
  contribution is a new method, because it surfaces naturally where yours fits.
- **Generational.** A narrative progression, when your contribution is the clear next step.

Chronological order with no thematic spine is not a structure; it is the shopping list again.

## Where it goes

Two conventions, both fine:

- **Right after the introduction.** Common in security and systems venues. Use this when a
  reviewer would otherwise assume the problem is already solved, or impossible.
- **Just before the conclusion.** Keeps the intro and contributions clean and lets the reviewer
  understand your idea before comparing it to anything.

What matters is not the position but that the gap statement is unmistakable.

## Per-paragraph shape

1. **Topic sentence** naming the thread.
2. **Two to four representative works, synthesized** - what they share, how they differ from
   one another.
3. **Delta sentence.** "Unlike these, we ..." or "These all stop at X; we go further by Y."

The delta sentence is not optional. A paragraph without one is a summary someone else could
have written.

## For empirical security and systems papers

- **A comparison table at the end of the section** makes the gap visual: rows are prior work,
  columns are the dimensions that actually matter for your contribution (dataset, scale,
  language, threat model, artifact availability). Six rows beat two paragraphs.
- **Do not conflate background and related work.** Background is what a reader needs in order
  to follow the rest of the paper. Related work is the closest prior systems and your delta.
  Some venues merge them; check recent papers in your target venue.
- **For benchmark papers, compare benchmarks, not only methods.** Other people's benchmarks
  are the baseline for "why a new one was needed".
- **Answer the hostile reviewer in two sentences.** Imagine the reviewer who already knows the
  area saying "this has been done". If the section cannot answer them briefly, restructure it.

## Common mistakes

- A shopping list with no synthesis.
- Chronology standing in for a thematic spine.
- Citing only friendly prior work and omitting the closest competitor.
- Ending the section without a sentence that states the gap.
- Burying in prose a comparison that a table would settle.
- Using the section to apologise for limitations. Weaknesses belong in limitations, not here.

## Checklist

- [ ] A reader can state the gap in one sentence after this section.
- [ ] The closest two or three baselines are named and explicitly contrasted.
- [ ] Every paragraph ends with a delta sentence.
- [ ] A comparison table exists where the paper type warrants one.
- [ ] The closest prior work is also forward-referenced from the introduction.
- [ ] No paragraph is a list of "A did X, B did Y".
