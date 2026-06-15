# Rebuttal: [paper short title]

> Produced by `/research.rebuttal`. Lives at `./.research/rebuttal/rebuttal.md`.
> Fill every bracket. Wait at least a day after reading the reviews before drafting -
> the first reaction is rarely a good rebuttal.

## Word budget
- Limit: [venue word/char cap, e.g. 5000 chars]. Track as you write; the final pass
  trims to fit. Spend the budget on substance, not courtesy.
- One brief opening line of thanks is fine; everything after must answer a concern.

## Triage (do this before writing prose)
[Decide and record. A grid of concerns drives the whole rebuttal.]

- **Rebut or not**: [rebut / skip]. Mixed or borderline scores -> always rebut. Uniformly
  very low -> usually skip unless the text is reusable for the next venue. Very high ->
  still write a short rebuttal; silence has sunk strong papers.
- **Champion**: [which reviewer is most supportive]. Spend disproportionate effort arming
  them with arguments for the committee meeting; do not pour all fire on the harshest critic.
- **At-risk positive**: [any borderline-positive reviewer who may drift negative]. Re-energize
  them explicitly rather than only refuting the negatives.
- **Concern grid** (one row per concern; tag every reviewer who raised it):

| Concern | Raised by | Priority | Response block | Evidence |
| --- | --- | --- | --- | --- |
| [concern, in your words] | [R1, R3, AC] | [1=meta/AC, 2=multi-reviewer, 3=swayable, 4=minor] | [#block id] | [paper pointer / ref / new result] |
| [...] | [...] | [...] | [...] | [...] |

Priority order: meta-reviewer call-outs -> area-chair items -> concerns raised by multiple
reviewers -> swayable borderline reviewers -> minor points.

## Opening
[Two or three sentences max. Optional single line of thanks, then the one or two
highest-impact clarifications that frame everything below. No throat-clearing.]

## Responses (ordered by impact, grouped by theme)
[Group shared concerns into one block with inline reviewer tags in the header, so a
reviewer can skim to what affects them. Each block answers first, then justifies.]

### [Theme / sub-question] (R1, R3, AC)
[Direct factual answer in the first sentence - no buried answer, no hedging.]
- First, [evidence: precise pointer to an existing section/figure/table/appendix, OR a
  reference, OR a freshly-run result with the actual number].
- Second, [supporting reasoning or a second concrete number].
- Further, [secondary point or scope clarification, if needed].

### [Theme] (R2)
[Answer first. For a "will it handle X?" question, answer with depth, not a shallow
yes/no. If X is an open challenge for the whole class of systems, say so and bound its
concrete impact: "X is a general challenge for this class rather than a flaw specific to
our design; its effect on [metric/guarantee] is [bounded statement]."]
- First, [...]
- Second, [...]

### [Theme] (R4)
[Reframe scope instead of conceding where fair: "Our method is designed to [intended
role], not to [the broader thing the reviewer measured against]; under that scope,
[result] supports the contribution." Acknowledge a genuine limitation only when real,
framed thoughtfully as out-of-scope or future work.]

## New results run during the response window
[Demonstrate beats promise. Where the window allows, run the experiment and report the
number instead of committing to add it later.]
- [setup] yields [result]; we will add this to [Table/Figure X]. (Concern: [#block])
- [...]

## Revision commitments
[Specific and bounded - which section, which table, which discussion. Quote the exact
new text where it shows the change is small and contained. Only promise what you can
actually deliver in camera-ready; committee members may remember unkept promises.]
- To address [concern], we will add to [Section Z]: "[exact proposed sentence(s)]".
- R[n] asked for [quantity]; it is [value]. We will report it in [Section Y].
- [...]

## Reference pack
[Compact, numbered, full sources for every non-obvious external claim - including
industry/web sources, not only papers. Keep it tight.]
- [R1] [full citation]
- [R2] [...]

## Quality checklist
- [ ] Waited a day or more after reviews before writing.
- [ ] Rebut-or-not decided explicitly (even very high scores get a short rebuttal).
- [ ] All reviewer concerns itemized in the grid before any prose was written.
- [ ] Champion identified; their concerns fully addressed and arguments handed to them.
- [ ] At-risk positive reviewer re-energized, not just the negatives refuted.
- [ ] Priority order followed: meta-reviewer > area chair > multi-reviewer > swayable > minor.
- [ ] Concerns grouped by theme with inline reviewer tags; shared concerns consolidated.
- [ ] Every response answers first, then justifies - no buried answers, no obsequious opener.
- [ ] Every claim carries evidence: a paper pointer for existing points, a reference or
      fresh result for new ones (no claim left unsupported).
- [ ] "Will it handle X?" questions answered with depth, not a shallow yes/no.
- [ ] Specific numbers quoted; exact revised paragraph text given where asked.
- [ ] New experiments run in-window and results reported where feasible.
- [ ] Every commitment is one you can actually deliver in camera-ready.
- [ ] Tone is polite, not defensive, not snarky (a snarky rebuttal can sink a borderline paper).
- [ ] Neutral-third-party test passes: each concern is resolvable from the rebuttal alone.
- [ ] Trimmed to the word limit; only the final draft submitted (drafts may be visible).

---
Next: `/research.paper` (fold accepted revisions into the draft) or resubmit, reusing
this rebuttal text for the next venue.
