# Proposal: [short working title]

> Produced by `/research.proposal`. Lives at `./.research/proposal/proposal.md`.
> Two lenses, one spine. Fill every bracket; an empty slot means the pitch is still a topic.
> Pick the genre, then delete the section that does not apply.

## Genre (pick one, delete the other)
- **Paper pitch / panel** — sells one idea to an expert who reads every word and judges feasibility and credibility. Keep the idea-and-evidence core heavy; cost and timeline are minor. Swap Heilmeier Q6-Q7 for "what have I already done?" and "what is the plan for success?"
- **Fellowship / grant** — pitches a multi-year agenda to a fast-skimming non-specialist who funds the person, not the exact plan. Keep background light (roughly a quarter of the space), lead with significance, and answer cost, timeline, and feasibility. Make a non-specialist care and let a fast reader skim the gist (bold, bullets, one visual).

## One-sentence thesis (write this first, repeat it everywhere)
[One declarative, falsifiable sentence a reader can repeat back after a two-minute read. Use the scaffold:
"<Mechanism X> improves <metric M> relative to <baseline B>, under <condition Z>, at equal <cost / benign performance>."
If any slot is empty, it is not yet a claim. Lead the whole document with significance, never with "X is important [1,2,3]."]

---

## NABC (the 60-second spine)
> Iterate this one-liner dozens of times until it is crisp. It is the verbal version of the whole proposal.

- **Need.** [The specific, sized opportunity. Who needs what outcome, and what can they do once it exists that they cannot today? A sharp question, not a topic area.]
- **Approach.** [The concrete, compelling solution. Name the mechanism and the key insight that makes it work.]
- **Benefit.** [The quantified payoff - better, not just different. A number or a direction, measured how, against what.]
- **Competition.** [The nearest alternative AND the do-nothing default, and why yours wins. Short and memorable.]

NABC one-liner: [You need <outcome> (N). We do <approach> (A). This gives <quantified benefit> vs <alternative> (B). The alternative is <competition>, which <falls short how> (C).]

---

## Need / problem (why now)
[Open on one vivid, concrete molehill the reader can picture, not background.
Importance = consequence x a plausible way in. Argue BOTH in the same breath:
- Consequence: who is hurt or what is at stake if this stays unsolved.
- Tractability: why it is solvable NOW (new data, new tool, new access, new method).
A huge problem with no credible attack is a daydream, not a proposal.]

## Gap (argued, not listed)
[Use the scaffold: "Prior work does X [cite], but X leaves Y open / assumes Z, which fails when <situation>. This idea fills exactly Y."
Name what prior work is missing; do not enumerate it. The gap must be the same size as the hole the idea fills - no wider, no narrower. Avoid "no one has done X" with no reason why X is hard or worth doing.]

## Approach / key idea (what is new and why it will work)
[The mechanism in 2-4 sentences, distinguished from the nearest prior idea. Why it is new and why it is hard, so it is not already done. Avoid "we will build a system that..." with no mechanism.]

## Benefit
[The quantified improvement versus the named Competition above. Prefer a number or a direction over an adjective. Tie it back to the Need: this is the outcome the reader could not get before.]

## Plan and validation (pre-committed, before any results)
[Name the test before the results exist. "We will evaluate it" is not a plan - a plan can prove or disprove the thesis.]
- Hypothesis: [predicted direction, e.g. metric(A) < metric(B)].
- Falsifier: [the observable result that would prove the thesis wrong].
- Experiment / substrate: [what you run it on].
- Metric(s): [measured end-to-end, not via a convenient proxy; if a proxy, argue the link].
- Baselines: [the unmodified default system AND a fairly tuned state of the art - never evaluate only against yourself].
- Trials: [repeated runs with reported variance for any nondeterministic result; never single runs].
- Confounds: [named, each with its control - experimental, statistical, or acknowledged - decided at design time, not post-hoc].

## Risks and feasibility (plan a tree, not a sequence)
[Replace "will do" with "have done": cite at least one pilot number, working prototype, or dataset already in hand - the single strongest, cheapest feasibility signal.]
- Have-done: [the artifact or result already in hand].
- Risk -> fallback: ["If <approach> fails because <reason>, we fall back to <alternative>; if even that fails, the negative result still establishes <what we learn>."]
- Risk -> fallback: [...]

## Contributions (things that will exist, each with evidence)
[Each item is an artifact or measured effect, pointing at where it is shown. Not "we describe a cool system."]
- C1: [release <artifact> / show <measured effect>] -> [evidence: experiment / section]
- C2: [...]
- C3: [...]

## Success criteria (the mid-term and final exams)
[Heilmeier Q8: how will anyone, including you, know it worked? Name observable checkpoints, not vibes.]
- Mid-term exam: [the early signal that says keep going - e.g. pilot result clears threshold T].
- Final exam: [the end-state result that confirms or refutes the thesis - e.g. metric(A) beats both baselines by margin M with variance reported].

---

## Fellowship / grant only (delete for a paper pitch)
- **Significance (lead with this).** [When <specific outcome> exists, <who> can <do what they cannot today>. Today this is blocked because <gap>. This proposal closes it by <approach>.]
- **Cost.** [Resources, people, compute, access required.]
- **Timeline.** [Realistic schedule for one question over the funded period; one question per fellowship.]
- **Intellectual merit / broader impacts.** [Label these if the program requires them.]
- **One coherent story.** [Proposal, personal statement, and CV must reinforce a single narrative; the long-term goal should appear in more than one place. A mismatch is a red flag.]

---

## Heilmeier Catechism (run all eight; every answer must be crisp)
1. **What are you trying to do?** [Plain words, no jargon.]
2. **How is it done today, and what are the limits?** [The status quo and where it breaks.]
3. **What is new, and why will it work?** [The mechanism and the insight.]
4. **Who cares, and what difference will it make?** [The stakeholder and the consequence.]
5. **What are the risks?** [And the fallback for each - see the risk tree above.]
6. **How much will it cost?** [Paper pitch: swap for "What have I already accomplished?"]
7. **How long will it take?** [Paper pitch: swap for "What is the plan for success?"]
8. **What are the mid-term and final exams for success?** [The success criteria above - the most-skipped and most-important question.]

---

## Quality checklist
- [ ] The whole pitch compresses to one declarative, falsifiable sentence with a named metric.
- [ ] The problem is a sharp question illustrated by one concrete example, not a topic area.
- [ ] Importance is argued as consequence x plausible attack, not stakes alone.
- [ ] The gap is argued, not listed, and is exactly the hole the idea fills.
- [ ] The key idea names a mechanism and is distinguished from the nearest prior idea.
- [ ] Validation names experiment, metric, baselines (default + fair SOTA), substrate, and the disconfirming result.
- [ ] Nondeterministic results report repeated trials with variance; confounds are named with controls at design time.
- [ ] Feasibility shows at least one "have done" artifact; risks form a tree with fallbacks.
- [ ] Contributions are things that will exist, each pointing at its evidence.
- [ ] Scope is one idea / one question, realistic for the timeframe.
- [ ] All Heilmeier questions answer crisply, especially Q8 (the success exams).
- [ ] Genre fit: page limits obeyed; for fellowships, background is light and significance leads.
- [ ] A smart non-specialist can restate problem, idea, and test after a two-minute read.

---
Next: `/research.review` (to pressure-test it) or `/research.paper` (to start drafting).
