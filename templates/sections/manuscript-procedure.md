> The shared procedure for working on one manuscript section. Loaded by
> `/research.write <section>` and by `/research.implement paper <section>`; both follow this
> file so the procedure has one source. The commands own what happens around it - `implement`
> also updates the Paper task in `tasks.md`.

# Working a manuscript section

The rule underneath all of it: **a section is an argument, not a summary of what you ran.** The
experiments were run for a reason; the section exists to make that reason land. Prose written
from whatever happens to be in context produces a report, not a paper.

---

## 1. Read the whole paper, then say what it argues

Read **every** section of the manuscript, following `\input`/`\include` from the main file, plus
the tables and figure captions - that is where the evidence lives. Reading only the target
section is what produces prose that restates the experiment.

Also read `./.research/proposal.md`, `related-work.md`, `claims.md`, and `plan.md` **when they
exist**. When they do not - normal for a paper already in flight - derive the argument from the
abstract and the contribution list instead. Never demand the pipeline retroactively.

Then show an **argument brief**, and stop for confirmation if any line is guesswork:

- the paper's thesis in one sentence, and its contribution list as the paper currently states it;
- where this section sits in that argument, and what breaks without it;
- the evidence this section can actually use - quote the real numbers, table, or figure.

A number the section needs but the paper does not contain is a gap to **report now**, never one
to invent. Missing claims make result beats `[UNVERIFIED]`.

## 1b. Take a voice sample from the prose that already exists

The paper already has a voice. Match it. A section that switches register is more obvious to a
reviewer than a weak one, and this matters most on a revision, where the new prose sits directly
against the old. Read the existing sections for these and record them **before writing**:

- **House terms.** What the paper calls its system, its adversary, its dataset, its unit of
  analysis. Copy them exactly, including capitalization and italics. Never introduce a synonym
  for a term the paper has already fixed - not for variety, not to avoid repetition.
- **Person and tense.** Almost always `we` / `our study`; past tense for what was run, present
  for what the paper does. Follow whatever the paper does, not the genre default.
- **How numbers are written.** Percentage-then-count or count-then-percentage, thousands
  separators, `\SI{}`/`\num{}` or plain digits, and whether every percentage carries a named
  instance.
- **The paper's own labelled beats.** `**Roadmap.**`, `**Our study.**`, `**Adversary model.**`,
  `**Takeaway.**` - reuse the labels the paper already uses, in its formatting.
- **Citation and macro habits.** `~\cite{}` placement, `\system{}` / `\name{}` macros, custom
  environments. Use the macros; never inline what a macro expands to.

Show the sample as part of the argument brief - a handful of lines is enough. When the
manuscript has no prose yet, say so and take the register from the guides and the constitution
instead.

## 2. Load the craft for this section

Infer the paper type from the manuscript (threat model and adversary -> attack; a detection or
mitigation system -> defense; corpus, RQs and findings -> measurement; dataset, baselines and
leaderboard -> benchmark; taxonomy over prior work -> SoK). State which and why in one line.
Load `.research/templates/paper/<type>.md` for the section skeleton, and read your type's block
in `.research/templates/sections/moves-by-type.md` for the rhetoric that only that type uses.

Always load `.research/templates/sections/rhetorical-moves.md`, then route:

| Section | Guide |
|---|---|
| abstract, intro, contributions, roadmap | `sections/abstract-intro.md` |
| related work | `sections/related-work.md` |
| ethics, disclosure | `sections/ethics-disclosure.md` |
| limitations, future work | `sections/limitations-future-work.md` |
| figures, tables | `sections/figures-tables.md` |

A guide that is not in this repo is a gap to **name**, not to fill from memory. Say which one was
unavailable, suggest `/research.init`, and proceed without it - never paraphrase what you assume
it says.

## 3. Pin the section's job

Four lines, settled before any prose. Ask when the manuscript does not answer one; do not write
around it.

1. **Claim** - what the reader must believe after this section. One sentence.
2. **Evidence** - which specific number, table, figure, or eval file carries it.
3. **Objection** - what a reviewer attacks here, phrased as they would phrase it. The defence
   belongs inside the prose, not bolted on afterwards.
4. **Boundary** - what this section deliberately does not cover.

For a revision, add a fifth: **why the change was asked for** (new result, reframing, reviewer
response). Restate it in your own words and confirm before proceeding - a revision that serves
the wrong reason is worse than none.

## 4. Choose the mode

- **OUTLINE** (default) - one line per paragraph, each naming that paragraph's job in the
  argument and the evidence behind it. A paragraph that advances nothing gets cut here, not
  after it is written. Hand back a skeleton, not prose.
- **REVISE** - when the section already has prose and the request is to change it. Run the blast
  radius below, then propose a located change list (`file:line` -> what changes and why). New
  sentences must be indistinguishable from the surrounding prose - same terms, same person and
  tense, same number formatting as the voice sample. **Never apply in the same turn as the
  proposal.**
- **CRITIQUE** - located findings on voice, claim traceability, overclaim, and tightening. Do
  not rewrite the user's prose.
- **DRAFT** - full prose, only on the explicit word `draft`, in the user's voice, every
  empirical statement scoped to a claim.

## 5. Blast radius (REVISE only)

A changed result rarely touches one place. Before proposing the edit, check each of these
against the change and report the result **even when nothing else is affected**:

- the abstract's numbers and its claim verbs;
- the contribution list in the introduction;
- any related-work delta that leaned on the old number;
- the conclusion;
- any other section citing this result as support.

A number that disagrees between the abstract and the body costs the paper its credibility with
a reviewer. This check is the main value of a revision pass.

## 6. Write, and report honestly

Apply the loaded craft guides and the constitution's writing voice. Use a move only where it
fits the section's job - a move applied for its own sake reads as pastiche, and a reviewer who
knows the genre notices.

**Where the manuscript and a guide disagree, the manuscript wins.** The guides describe the
genre; the voice sample describes this paper. Consistency inside one paper beats conformity to
the genre, so never "correct" an established term, formatting habit, or heading style to match a
guide. If the paper's habit looks like a real problem, say so in the report and leave it.

Non-negotiable regardless of mode: motivation before method; every novelty claim scoped; active
`we`; each statistic paired with a named instance and an absolute count; a "so what" after each
major finding; effectiveness and cost reported together; related-work themes ending in explicit
deltas.

Never invent a number, a citation, or a system name. Where the prose needs one the paper does
not have, write `[UNVERIFIED]` or `[cite?]` and list it in the summary. Never silently overwrite
existing prose - show what is being replaced.

Close by reporting: what was written or proposed, which craft guides were loaded, every gap left
behind, and anything the blast radius surfaced that you did not touch.
