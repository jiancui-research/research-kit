# Related work: [short working title]

> Produced by `/research.relatedwork`. Lives at `./.research/related-work.md`.
> Reads `./.research/proposal.md` for the problem, gap, contributions, RQs, venue, and
> paper type. The section turns those into a positioned survey, not a citation dump.
> Clarity and the argument come first, not filling the form: write only what positions this paper,
> cut the rest, and end each themed paragraph with an explicit delta sentence.
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
[One paragraph per group (~4-6 sentences). Synthesize, never list. Use the scaffold and end each on a delta:]
[`<Theme topic sentence>. A line of work approaches this by <shared idea>, differing
mainly in <axis>. These methods, however, all assume <constraint> / stop at <boundary>.
In contrast, our work <delta>.`]

> **Argued positioning: craft moves (shape every paragraph with these; guidance, not text to paste).**
> The scaffold above is hygiene; these are the moves that make a positioning paragraph win a crowded field.
> 1. **Lead with the shared blind spot, not a roster.** Make the limitation the whole family shares the subject of the topic sentence, so the reader sees the gap before the list of systems. ("Existing agent defenses operate at the tool-call level" beats "Runtime defenses guard the agent in two ways.")
> 2. **Group by failure-axis, not one paragraph per system.** Bucket prior work under the 2-3 underlying reasons it falls short; each bucket is a "differs in kind" claim. Two buckets are easier to hold than five papers.
> 3. **Concede shared costs, then win elsewhere.** If a "why not just do X?" objection rests on something that also burdens you, grant it out loud, then attack the axis where you genuinely differ. Never lean on a differentiator that boomerangs onto your own system.
> 4. **Attack the strongest form; prefer the competitor's own admission.** Go at the best member ("even the ones with formal proofs...") and cite their paper's own reported limitation as evidence, not your speculation.
> 5. **Name the load-bearing mechanism with the exact word.** Make the pivotal link concrete and pick the technical term that carries the logic (the code is the *argument* of a tool call, not its *output*); imprecision here reads as not understanding the model.
> 6. **Keep design rationale out of the gap.** "Why we built it this way" belongs in the proposal's Key idea, not here - each idea appears once.

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

## Comparison table (expected for benchmark / measurement / defense / SoK papers)
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

---
Next: `/research.feasibility`
