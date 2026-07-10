# Proposal: [short working title]

> Produced by `/research.proposal`. Lives at `./.research/proposal.md`.
> A proposal is a 1-3 page argument, not a form. Hard rules:
> - **1-3 pages total.** Revise by cutting: each pass removes a sentence, it never adds one.
> - **Each idea appears exactly once.** The thesis appears exactly twice: the elevator paragraph and part 3.
> - **Easy to read.** Plain words, short sentences, no jargon pile-ups; define each term of art at first use, then reuse the same word. A smart non-specialist must be able to restate problem, idea, and test after a two-minute read.
> - **Cite by bare name in prose** ("unlike SpecEval"); full citations live only in References.
> - **No inline `[ASSUMPTION: ...]` brackets.** Everything inferred goes in the numbered Open assumptions block at the end.

**Target venue:** [venue + one-line reason] · **Paper type:** [measurement / attack / defense / benchmark / SoK]

*[The NABC elevator paragraph - the only compressed restatement of the pitch in the whole document. 3-5 sentences, no citations: who needs what outcome (Need), the mechanism and the insight that makes it work (Approach), the quantified payoff (Benefit), and the nearest alternative plus the do-nothing default, and why yours wins (Competition).]*

## 1. Problem & motivation
[~1 paragraph - write it LAST. Open on one vivid, concrete example the reader can picture, not background. Argue consequence (who is hurt if this stays unsolved) and tractability (why it is solvable now: new data, tool, access, or method) in the same breath. A huge problem with no credible attack is a daydream, not a proposal.]

## 2. Gap
[~1 paragraph, argued not listed: "Prior work does X, but X leaves Y open / assumes Z, which fails when <situation>. This idea fills exactly Y." The gap is exactly the hole the idea fills - no wider, no narrower.]

## 3. Key idea
**Thesis:** [one declarative, falsifiable sentence, at most 35 words, naming the metric and the baseline. If a reader cannot repeat it back after a two-minute read, shorten it.]

[Then ~1 paragraph of mechanism: what you actually do and the insight that makes it work, distinguished from the nearest prior idea.]

## 4. Why new & why hard
[~1 paragraph: why this was not already done (what made it hard until now) and how your mechanism gets past that. If it is not hard, it is already done.]

## 5. Plan & validation
[1-2 paragraphs or a compact table, pre-committed before any results exist. These hypotheses are the proposal's research questions. "We will evaluate it" is not a plan - a plan can prove or disprove the thesis.]
- Hypotheses: [H1, H2, ... each with a predicted direction, e.g. metric(A) < metric(B), and its falsifier - the observable result that would prove it wrong].
- Substrate: [what you run it on].
- Metric(s): [measured end-to-end, not via a convenient proxy; if a proxy, argue the link].
- Baselines: [the unmodified default AND a fairly tuned state of the art - never only yourself].
- Trials: [repeated runs with reported variance for any nondeterministic result].
- Confounds: [each named with its control, decided now, not post-hoc].

## 6. Contributions
[Things that will exist (dataset, system, theorem, measured effect), each pointing at its evidence.]
- **C1.** [release <artifact> / show <measured effect>] -> [evidence: which eval / section]
- **C2.** [...]

## 7. Risks & feasibility
[~1 paragraph, have-done first: the pilot number, prototype, or dataset already in hand - the strongest, cheapest feasibility signal. Then the risk tree: "If <approach> fails because <reason>, we fall back to <alternative>; even then, the negative result still establishes <what we learn>."]

---

## Open assumptions
[Every value that was inferred rather than given, numbered so each can be confirmed or corrected. The prose above never carries inline assumption brackets.]
1. [assumption]
2. [...]

## References
[Full citations live here only; the prose above cites by bare name.]

---
Next: `/research.relatedwork` (survey + position), or `/research.feasibility` if related work is done.
