> Loaded alongside `sections/rhetorical-moves.md` once the paper type is known. Read **only**
> the block for your type. The cross-cutting moves apply to every paper; these do not.

# Rhetorical moves by paper type

The moves in `rhetorical-moves.md` hold across the genre. These are the ones that only earn
their place in one kind of paper - a "consequences are dire" sentence in a measurement paper
reads as overclaim, and an adversary-model beat in a defense paper reads as filler.

---

## Measurement

### The vivid scenario opener

Most measurement papers open on a statistic or a trend. The stronger opening is concrete and
second-person, or a dated incident:

```
Imagine that you [action a reader can actually perform]. Figure 1 shows what we got on [date].
In [month year], [named incident], causing [observable damage to named parties].
```

The Figure 1 reference comes immediately after, so the reader sees the phenomenon before any
framing. Name the recognizable victims in the first three sentences.

### Pose the research questions explicitly

Measurement papers spell out their questions as a bolded list, usually inside the "Our study"
paragraph of the introduction, and answer them in that order in the findings:

```
More specifically, we aim to answer the following questions: **[RQ1]? [RQ2]? [RQ3]?**
```

A question that the paper does not answer with evidence does not belong in the list. If the
venue expects labelled `RQ1/RQ2/RQ3`, label them and reuse the labels in the section headers.

### Numbers carry named instances

The dominant finding pattern, and the reason the findings are memorable:

```
[percent] ([absolute count]) of [population], including [recognizable named instance],
[recognizable named instance], [exhibit the property].
```

Always the absolute count next to the percentage, and always at least one name a reviewer will
recognize - a top-ranked site, a well-known vendor, a government or university domain. A bare
percentage is forgettable.

### The "we even ..." escalation

One sentence, after the headline finding, that pushes past it:

```
We even [recovered / discovered / identified] [the unexpected artifact].
```

It works because it implies the study went further than it had to. Use it once or twice per
paper, on findings that genuinely exceeded the design, never on a routine result.

### The "tip of the iceberg" landing

Closes a findings section or the conclusion, converting your scope limit into a research agenda:

```
Such findings, which we believe are just a tip of the iceberg, will inspire follow-up
research on [direction].
```

It pre-empts "you did not cover X" by claiming the uncovered space as future work rather than
as a gap. Do not use it if the paper elsewhere claims comprehensive coverage.

### Methodology framing vocabulary

Method sections in this genre introduce the apparatus with a small stock of terms, each making
a specific claim: *systematic approach* (repeatable, not ad hoc), *infiltration framework*
(you became a participant in what you studied), *longitudinal analysis* (repeated over time),
*large-scale measurement* (population, not sample), *unique methodology* (the combination is
what is new). Pick the ones you can defend; each invites the matching reviewer question.

### Suspicion and confirmation in case studies

Case-study paragraphs read as investigation rather than reporting when they show the sequence:

```
[What we observed] led us to suspect [hypothesis]. [What we then did]. [What it confirmed],
[quantified].
```

Label speculation as speculation. "We suspect" is fine once, attached to a hypothesis you then
test; it is not a way to soften a measured result.

---

## Attack

### The consequences sentence

After the headline result, one sentence that makes the impact concrete rather than abstract:

```
The consequences are dire: [named, specific thing an attacker obtains or controls].
Not only does our attack [what it defeats], it also [stronger thing], completely
[defeating / circumventing] [the layered defense].
```

The force comes from the named specifics that follow the colon, not from the adjective. One
such sentence per paper.

### The landing sentence: attack to implication

Attack contributions close by translating the attack into something the community must change:

```
This finding calls into question [the practice / the assumption / the disclosure norm].
These findings highlight [the security implications] and the urgency to [action].
```

Without it, an attack paper reads as a stunt. This is also the sentence a program committee
quotes when arguing for the paper.

### Adversary model as a fixed, labelled beat

Every attack paper needs a labelled paragraph, in the background or design section, that a
reviewer can find in one scan. Three sub-beats, bolded inline:

```
**Adversary's goal.** [What the adversary wants, in the paper's own terms.]
**Adversary's knowledge.** [Black-box or white-box, and over exactly what.]
**Adversary's capability.** [What they may do, and the assumption that bounds it.]
```

State what the adversary may **not** do. An unbounded adversary makes the attack unfalsifiable
and the evaluation meaningless.

### Goal lists for multi-objective attacks

When the attack must satisfy several constraints at once, number them and say **simultaneously**:

```
... whether [the manipulation] can be made such that the following hold simultaneously:
1) [effectiveness goal], 2) [evasion goal], 3) [stealth / utility-preservation goal].
```

The numbered goals then become the evaluation's subsections, in the same order. A goal with no
matching experiment is a reviewer's first target.

---

## Defense

### Performance numbers up front

The abstract carries one or two punchy numbers, not a promise that the evaluation has them:

```
Running on [dataset, sized], [system] achieved [precision / recall / F1 / coverage], which is
[delta] over [named baseline], at [throughput or cost].
```

Effectiveness and cost travel together, always. A defense with unstated overhead reads as
incomplete regardless of its accuracy.

### The "framework and tools" formulation

For tool papers the recurring pivot is `we present a framework and tools for [X]` - it claims
generality (framework) and usability (tools) in one clause, and it commits you to releasing
something. Use it only when you will actually ship the artifact.

### The contribution verb cadence

Defense contribution lists follow a verb progression, one bullet each:

```
We define [the property / the problem formulation].
We design and implement [the mechanism].
We propose [the new component that made it possible].
We are the first to [scoped novelty claim].
We release [code / dataset / models] at [location].
```

The verbs escalate from conceptual to concrete to public. Skipping to `we implement` with
nothing defined first is what makes a defense paper read as engineering.

### The key-observation sentence

One sentence, usually italicized, stating the empirical fact the whole design rests on:

```
A key observation [behind our approach] is that [the regularity in the data that the
technique exploits].
```

Place it before the design section, never inside it. If you cannot write this sentence, the
design has no thesis and the evaluation will not rescue it.

### Artifact release as its own contribution

The last contribution bullet, not a footnote and not only a link in the conclusion. Name what
is released (code, dataset, trained models, prompts, labelled ground truth) and where. In this
genre a released artifact is a claimed contribution and reviewers weigh it as one.

---

## Benchmark and systematization

Neither has a distinct move set here; both borrow.

- **Benchmark:** use the measurement block for evidence patterns (named instances beside every
  number, explicit RQs), and the defense block's front-loaded numbers - restated as coverage,
  task counts, and the spread across baselines rather than precision and recall. The
  key-observation sentence becomes the design rationale for the task suite.
- **Systematization (SoK):** use the cross-cutting gap formula to justify the taxonomy rather
  than a study, and the "tip of the iceberg" landing to scope what the survey excludes. Skip
  the discovery verbs - a SoK organizes what is known and does not bring it to light.
