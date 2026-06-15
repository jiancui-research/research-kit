> Loaded by /research.paper when drafting the abstract or introduction. Cross-cutting craft (applies to every paper type).

# Abstract & introduction

**TL;DR:** These are the two most-read sections - often the *only* ones read. Make each self-contained: a reader who stops after the intro should be able to state the gap, your idea, and your headline result in one sentence each.

---

## Abstract

Follow the arc: **problem -> method -> result (a number) -> implication.** One paragraph, ~150-250 words.

- **One-number rule:** put your single strongest quantitative result in the abstract (the win rate, the speedup, the number of bugs found, the accuracy delta). One concrete number beats three vague adjectives.
- **Shape:** 1-2 sentences problem, 1-2 method, 1-2 result, 1 implication. No citations, no acronyms you don't expand, no "in this paper we".
- **Headline-first option:** if your result is surprising, you may lead with it ("We show that X, widely assumed secure, leaks Y") and backfill the setup. Use when the surprise *is* the contribution.
- **Closing scope qualifier:** end with one clause that pre-empts "but does it work on real systems?" - name the real artifacts, scale, or setting you validated on (e.g., "across N production deployments / M real-world targets").

### Abstract skeleton (fill in)
```
[Domain/system] is [important because <concrete stake>], yet [the gap / what
fails today]. We present [name], which [core mechanism in one clause]. We
[evaluate / measure / attack / defend] on [real artifacts, scale]. [Name]
achieves [SINGLE STRONGEST NUMBER vs. baseline], [+ one secondary result].
This [implication / what it changes], demonstrated on [real-world scope].
```

---

## Introduction

Four moves, in order. Roughly one paragraph each; the whole intro is ~1 page.

1. **Why the target matters** - open with something concrete: a dated incident, a real deployment, a number (users affected, dollars, prevalence). Not "X is increasingly important."
2. **Name the violated assumption / gap** - state what people *thought* was true, safe, or solved, and where that breaks. This is the tension the paper resolves; make it falsifiable, not generic.
3. **Core idea in ONE sentence** - the single insight that closes the gap. If it takes two sentences, it isn't sharp yet.
4. **Demonstration scope + contributions + roadmap** - one sentence on what you built/measured and on what scale, then a numbered contributions list, then a one-sentence "Section N covers..." roadmap.

### Intro skeleton (fill in)
```
[Concrete motivating example / incident / number].
The prevailing assumption is [X is secure / solved / understood]. We show
[where and why that fails].
Our key insight is [ONE sentence].
We demonstrate this by [scope: system + scale + setting].

We make the following contributions:
- ...
- ...
- We release [artifact].

Section 2 ... Section N ...
```

---

## Contribution bullets

Each bullet names something that will **exist** and is **measurable** and **scoped** - a system, a dataset, a measured effect, a theorem. Not activities ("we study", "we explore").

- Good: "A [system] that [does X], achieving [number] on [benchmark]."
- Good: "The first measurement of [phenomenon] across [N real targets], revealing [finding]."
- Weak: "We investigate the security of [Y]." (no artifact, no number, unscoped)
- **End the list with an artifact-release bullet:** "We release code, data, and [models] at [URL]." Reviewers reward reproducibility; the release also caps the list cleanly.

---

## Quality checklist

- [ ] After the intro, a reader can state **the gap in one sentence**.
- [ ] The core idea is **one sentence**, not a paragraph.
- [ ] The abstract contains **at least one concrete number**.
- [ ] The motivation opens with a **concrete** example/incident/number, not a platitude.
- [ ] Every contribution is **something that exists** and is **measurable** (not an activity).
- [ ] The contribution list ends with an **artifact-release** bullet.
- [ ] A **scope qualifier** pre-empts "does this work on real systems?"
- [ ] No unexpanded acronyms; abstract has no citations.
