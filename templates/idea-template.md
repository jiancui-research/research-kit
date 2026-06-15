# Idea: [short working title]

> Produced by `/research.idea`. Lives at `./.research/idea.md`.
> Fill every bracket. An empty slot means the idea is still a topic, not a claim.

## Title
[Working title. Name the mechanism and the effect, not just the area. Revise last.]

## One-liner (falsifiable thesis)
[One declarative sentence a reader can repeat back. Use the scaffold:
"<Mechanism X> improves <metric M> relative to <baseline B>, under <condition Z>, at equal <cost / benign performance>."
If any slot is empty, keep working - it is not yet a claim.]

## Problem
[A sharp, answerable question, not a topic area. What specifically is broken,
unmeasured, or unprotected? Ground it in one concrete example or scenario the
reader can picture, not "X is important [1,2,3]."]

## Motivation / Need (the N in NABC)
[Importance = consequence x a plausible way in. Argue BOTH:
- Consequence: who is hurt / what is at stake if this stays unsolved.
- Tractability: why it is solvable NOW (new data, new tool, new access, new method).
Size the opportunity: who needs the specific outcome, and what can they do once it exists that they cannot today?]

## Approach (the A in NABC)
[Your concrete, compelling solution in 2-4 sentences. Name the mechanism and the
key insight that makes it work. Why is this new, and why is it hard (so it is not
already done)? Avoid "we will build a system that..." with no mechanism.]

## Benefit (the B in NABC)
[The quantified payoff, better not just different. What improves, by roughly how
much, measured how, against what? Prefer a number or a direction over an adjective.]

## Competition / Related (the C in NABC)
[The nearest alternatives - prior work AND the do-nothing default. State each in
one line and why yours wins. Keep it short and memorable; the full survey is
`/research.relatedwork`.]

## Gap (argued, not listed)
[Use the scaffold:
"Prior work does X [cite], but X leaves Y open / assumes Z, which fails when <situation>. This idea fills exactly Y."
The gap must be the same size as the hole the idea fills - no wider, no narrower.
Do not write "no one has done X" without saying why X is hard or worth doing.]

## Contributions (measurable, each with evidence)
[Each item is a thing that will EXIST and points at where it is shown. Use:
"We will release <artifact> (experiment N)" or "We will show <measured effect> (experiment N)."
Not "we describe a cool system."]
- C1: [artifact or measured effect] -> [evidence: experiment / section]
- C2: [...]
- C3: [...]

## Research questions (testable)
[Each RQ predicts a direction and names what would disconfirm it. Use:
"RQ: <question>. Prediction: <direction, e.g. metric(A) < metric(B)>. Falsifier: if <observable result>, we are wrong."]
- RQ1: [...]
- RQ2: [...]

## Target venue + paper type
- Venue: [target conference / journal and rough deadline]
- Paper type: [measurement | attack | defense | benchmark] (drives `templates/paper/<type>.md`)
- Fit: [one line on why this venue / type matches the contribution]

## Assumptions
[State assumptions explicitly so they can be challenged. Threat model, access,
scope, environment, what is in and out of scope. If multiple readings exist,
name the one chosen and why.]
- [assumption 1]
- [assumption 2]

## Quality checklist
- [ ] The whole idea compresses to one falsifiable sentence with a named metric.
- [ ] Problem is a sharp question with one concrete example, not a topic.
- [ ] Importance is argued as consequence x plausible attack, not stakes alone.
- [ ] Approach names a mechanism and is distinguished from the nearest prior idea.
- [ ] Gap is argued and exactly the size of the hole the idea fills.
- [ ] Each contribution is something that will exist and points at its evidence.
- [ ] Each RQ predicts a direction and names a falsifier.
- [ ] Baselines will include the unmodified default and a fair state of the art.
- [ ] Scope is one idea, realistic for the timeframe.
- [ ] A smart non-specialist can restate problem, idea, and test after a 2-minute read.

---
Next: `/research.relatedwork`
