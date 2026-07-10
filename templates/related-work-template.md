# Related work: [short working title]

> Produced by `/research.relatedwork`. Lives at `./.research/related-work.md`.
> Reads `./.research/proposal.md` for the problem, gap, contributions, RQs, venue, and
> paper type. The section turns those into a positioned survey, not a citation dump.
> Fill every bracket. Each themed paragraph must end with an explicit delta sentence.
> Paper type from `proposal.md` ([measurement | attack | defense | benchmark | SoK]) decides
> whether the comparison table below is required - consult `.research/templates/paper/<type>.md`
> for the dimensions that matter.

## Organizing structure (pick one, justify in one line)
[Do NOT default to a flat survey. Choose the structure the idea's framing implies:]
- [ ] Thematic - prior work spans different formulations of the problem (3-5 works per theme).
- [ ] Methodological - the contribution is a method (e.g., classical vs learning-based vs hybrid).
- [ ] By generation - the work is a clear successor to a visible progression.
- [ ] Funnel - broad area -> themes -> your niche (safe default).
- Why this structure: [...]

## Themed synthesis paragraphs
[One paragraph per group. Synthesize, never list. Use the scaffold and end each on a delta:]
[`<Theme topic sentence>. A line of work approaches this by <shared idea>, differing
mainly in <axis>. These methods, however, all assume <constraint> / stop at <boundary>.
In contrast, our work <delta>.`]

### Theme 1: [name]
[...]

### Theme 2: [name]
[...]

### Theme 3: [name]
[...]

## Closest baselines (treat generously, no strawmen)
[Name the 2-3 nearest prior works and contrast each directly on the axis that matters.]
- Closest #1: [work] - shares [...]; differs in [...]; we [delta].
- Closest #2: [work] - shares [...]; differs in [...]; we [delta].
- Closest #3: [work] - shares [...]; differs in [...]; we [delta].
- Single closest prior work: [work] -> forward-reference it in the Introduction.

## Comparison table (required for benchmark / measurement / systems papers)
[Rows = prior work; columns = the dimensions that make your gap visible. Pull dimensions
from `.research/templates/paper/<type>.md`. The empty cell that only your row fills is the gap.]

| Prior work | [dimension 1] | [dimension 2] | [dimension 3] | [dimension 4] |
|------------|---------------|---------------|---------------|---------------|
| [work A]   | [yes/no/...]  | [...]         | [...]         | [...]         |
| [work B]   | [...]         | [...]         | [...]         | [...]         |
| **Ours**   | [...]         | [...]         | [...]         | [...]         |

## Gap-closing paragraph (one sentence the reader can restate)
[Use the scaffold:]
[`To our knowledge, no prior work addresses <the specific cell>: existing systems either
<do A but not B> or <do B but not A>. We close this gap by <one-line contribution>.`]

## Background vs Related Work (venue note)
[Keep concepts needed to follow the technical sections (Background) separate from closest
prior systems and the delta (Related Work). Whether to merge or split should match the
target venue's recent papers - flag the chosen convention for the user to confirm.]
- Decision: [merge | split], because [venue convention]: [flag for user to check].

## Quality checklist
- [ ] A reader can state the gap in one sentence after the section.
- [ ] Every paragraph synthesizes (groups + delta); no `A did X, B did Y, C did Z` paragraphs.
- [ ] The closest 2-3 baselines are named and contrasted generously, no strawmen.
- [ ] The single closest prior work is flagged for an Introduction forward reference.
- [ ] A comparison table is present for benchmark / measurement / systems papers.
- [ ] Background and Related Work are not conflated; venue convention is flagged for the user.
- [ ] Limitations are not apologized for here (those belong in the Limitations section).

---
Next: `/research.feasibility`
