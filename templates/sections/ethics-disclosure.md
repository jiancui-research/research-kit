> Loaded by explicit `/research.implement paper ethics` mode. Craft for the ethics and
> responsible-disclosure section. Check the target venue's current CFP - several major security
> venues now require this section and evaluate it during review.

# Ethics and disclosure

**TL;DR:** "This work raises no ethical considerations" is not an acceptable answer, and neither
is a bare assertion that you behaved ethically. The section must say **what you did** and **why
that was the ethical choice**, in self-contained prose a reader outside your subfield can follow.

---

## Why a blanket "not applicable" fails

Work with any application to real systems carries ethical implications, positive and negative.
Even a primitive with no human subjects has application-level consequences: the same
capability that protects private communication can shield criminal coordination; a privacy
technique can improve user outcomes while carrying an environmental cost. Reviewers now read
for this, so a claim of "no considerations" reads as not having looked.

## What a strong section contains

- **Stakeholders, named.** Users, subjects, operators, vendors, third parties, the research
  team, and the broader public. Say who can be affected and how.
- **Concrete actions taken.** Disclosure to affected parties, IRB or ethics-board review, data
  minimization, anonymization, rate limiting during measurement, opt-out paths, deletion after
  analysis, withholding exploit details.
- **A justification per action.** *Why* was this the right choice given the alternatives? The
  action alone is not an argument.
- **Honest trade-offs**, including harms the work enables. Dual-use is not disqualifying;
  pretending it is absent is.
- **A post-facto label where it applies.** See below.

## The three failures reviewers call out

1. **"No ethical considerations."** Covered above.
2. **Assertion without justification.** "We used only public data" is not an argument - some
   public datasets were collected without consent. The *why* is the content.
3. **Post-facto reflection dressed as a priori analysis.** This is the one reviewers treat as a
   candour problem rather than a rigour problem. If the ethical analysis happened after the
   work, say so plainly, label it, and reflect on what you would do differently. An honest
   post-hoc paragraph is respected; a disguised one is not.

## Disclosure

Where the work found real vulnerabilities or live abuse, a disclosure paragraph does double
duty: it demonstrates ethics and it is the strongest available evidence that the work mattered
outside the paper.

```
We reported our findings to [named parties] on [date]. [What they did: acknowledged,
patched, awarded, took action.] [Any concrete downstream consequence.]
```

Name recognizable parties and give the outcome. A vendor confirming the issue, a fix shipping,
or a bounty awarded is worth more than a paragraph of process. A vague "we disclosed
responsibly" is worth nothing.

Where a fix is not yet deployed, say what you withheld and until when.

## Write it for a reader outside the area

The working test: someone reading their first paper in your subfield should be able to follow
both the actions and their justification, with no assumed community knowledge. That rules out
naming a process and expecting the reader to infer why it was sufficient.

## Checklist

- [ ] Stakeholders identified, not just "users".
- [ ] Every action paired with the reason it was the ethical choice.
- [ ] Harms the work enables are acknowledged, not omitted.
- [ ] Post-facto analysis is labelled as such where it applies.
- [ ] Disclosure names parties, dates, and outcomes where relevant.
- [ ] Self-contained: no forward reference needed to understand the argument.
- [ ] Checked against the target venue's current CFP wording, not last year's.
