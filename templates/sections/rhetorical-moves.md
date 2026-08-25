> Always loaded when working a manuscript section - by `/research.write <section>` and by
> explicit `/research.implement paper <section>` mode. Cross-cutting rhetorical craft for
> empirical security and systems papers, independent of paper type. For the moves that belong
> to one type only, read your type's block in `sections/moves-by-type.md`.

# Rhetorical moves

**TL;DR:** A section is an argument, not a summary of what you ran. These are the recurring
moves that make an empirical security paper read like one - a small vocabulary of forms you
can fill in. Use the ones that fit; a move applied where it does not belong reads as pastiche
and reviewers notice.

---

## 1. The four-move opener

Most strong intros in this genre open with the same four moves, in order:

1. **Importance of the target.** Establish that the system matters, with a number or a named,
   recognizable example - not an adjective.
2. **The tension.** Turn with "however" / "less clear is whether" / "yet".
3. **The gap.** State plainly what is not yet known or done (see move 2 below).
4. **The pivot.** "In this paper, we present ..." - and scope the claim (move 3).

Each move is typically one to three sentences. The whole opener is one paragraph or two.

## 2. The gap formula, with an escalating extender

The workhorse gap sentence has two halves, and the second half is what makes it earn its place:

```
So far, little has been done to [understand / characterize] [the phenomenon],
not to mention [any effort to detect / mitigate / exploit] [the harder thing].
```

Variants of the first half: "to our knowledge, little has been done so far", "never before has
any effort been made to", "none of these approaches, however, are designed to".

**Why the extender matters.** It escalates the gap from *understanding* to *action*, which
widens the contribution space and previews your contribution list. A gap sentence without the
extender concedes that someone could have done the easy half already.

## 3. Scope every novelty claim

A bare "first study" invites a reviewer to find a counterexample. Qualify the noun, always:

```
the first [systematic / large-scale / in-depth / empirical] study of [X] on [Y]
```

The qualifier is the defence. "First systematic study of X on Y" survives a reviewer who knows
of an ad-hoc blog post about X; "first study of X" does not.

## 4. Findings are brought to light, not merely found

"We found X" states a fact and stops. The stronger register frames the finding as revealing
something that was there all along:

- "our findings **bring to light** [the thing]"
- "our study **sheds new light on** [the process / the links / the scale]"
- "these findings bring [the threat] **to the spotlight**"

Use it for the headline findings, not every observation - it loses force by repetition.

## 5. Earn the right to be surprised

Authorial reaction is allowed, but only where the data genuinely defied expectation. The
reliable form transitions from tool to finding:

```
Looking into [what the tool/measurement surfaced], we are surprised to find that [finding].
```

This does three things at once: it foregrounds the method, asserts that a human judged the
result, and licenses the striking number that follows. On a confirmatory result the same
sentence reads as hype - use "as expected" or no marker at all.

## 6. Three structural beats in the contribution list

Contribution lists in this genre pattern as three beats, each with a bolded label:

- **New technique / methodology.** What you built and why it was not obvious.
- **New finding / understanding.** What the world now knows that it did not.
- **Released artifacts / disclosure.** Code, dataset, and who you told.

Order can vary (understanding-first is common for measurement, technique-first for defense),
but all three should be present. The third beat is a real contribution here, not a footnote.

## 7. Name the artifact once, then reuse it

Give the system, attack, or threat a short memorable name at first mention and use it
everywhere after - in section headers, in topic sentences, in the abstract.

```
..., which we call *[Name]*        |     ... (called *[Name]* in our research)
..., or *[Name]* for short         |     [Expansion] (*[Name]*)
```

Italicize on first use with the expansion attached. Acronyms, puns, and allusions all work; a
name that can be said aloud is worth more than a precise one that cannot.

## 8. The disclosure paragraph

One paragraph, sometimes its own subsection, and it does double duty: it demonstrates ethics
and it proves real-world impact.

```
We reported our findings to [named parties], who [acknowledged / patched / awarded /
took action]. [One concrete consequence, dated if possible.]
```

Name recognizable parties. A vendor confirming the issue, a bounty awarded, or a fix shipped is
the strongest available evidence that the work mattered outside the paper. Even one sentence
works; a vague "we disclosed responsibly" does not.

## 9. The roadmap paragraph

The last paragraph of the intro, templated and dull on purpose:

```
**Roadmap.** The rest of the paper is organized as follows: Section [N] [verb-s] [topic];
Section [N+1] [verb-s] [topic]; ... and Section [last] concludes the paper.
```

Clauses joined by semicolons, one per section. Skip it only where the venue's page budget
genuinely forbids it (short papers, some workshops).

## 10. Referential clarity

The moves above shape how a sentence sounds. They do not catch a sentence the reader cannot
resolve. A definite noun phrase promises that the reader already holds the referent; when they
do not, the sentence stalls even though every word in it is plain.

Check each noun phrase before delivering it:

- **A definite article with no antecedent.** "the task pairs", when no pair has been introduced.
  Define it in place, or make it indefinite.
- **A comparative with no second term.** "errors fall on different tasks" - different from what?
  Name the other side.
- **A partitive with no whole.** "both halves", "either side", "the remainder", when the thing
  being divided was never stated.
- **Two or more of these in one clause.** One unresolved reference is a stumble the reader
  recovers from. Three in a row is a sentence they give up on.

Define a term where it first does work, in the same sentence, rather than leaning on a table or
an earlier section to have carried it. This is where the failure usually comes from: a term that
read fine while a table defined it becomes undefined the moment that table changes, and no
register check will flag it.

---

## What this register avoids

Just as load-bearing as the moves above. These are the things that mark prose as *not*
belonging to this genre:

- **Bare "we found X"** with no surrounding rhetoric on a headline finding.
- **Hedge stacking.** "We suspect" and "we believe" only where the speculation is labelled as
  such; never as a way to soften a result you actually measured.
- **Superlatives without a number.** "Powerful", "industry-leading", "remarkable performance"
  are empty unless a figure is attached to them.
- **Multi-paragraph abstracts.** One dense paragraph, roughly 150-220 words.
- **First-person singular.** Always "we" and "our study", including on solo-authored work.
- **A related-work paragraph inside the introduction.** Compress prior work into the gap
  sentences instead; the survey belongs in its own section.

---

## Phrase slots

Fill the brackets. These are forms, not sentences to paste.

**Openers**
```
Imagine that you [action]. Figure 1 shows what we got on [date].
In [date], [named incident with named victims], causing [observable damage].
[System] today serves [number] users, providing [what]. However, [tension].
```

**Gap**
```
So far, little has been done to [X], not to mention [harder X].
None of these approaches, however, are designed to [X], not to mention [harder X].
Never before has any effort been made to [X].
```

**Findings**
```
Looking into [tool output], we are surprised to find that [finding].
Our findings bring to light [what], [quantified].
[Percentage] of [population], including [named instance], [exhibit the property].
```

**Landing a finding**
```
These findings [call into question / raise serious concerns about] [practice].
Our study [sheds new light on / brings to light] [what], suggesting [implication for whom].
```

Every statistic gets a named, recognizable instance and an absolute count beside it. A
percentage alone is forgettable; a percentage with a name a reviewer recognizes is not.
