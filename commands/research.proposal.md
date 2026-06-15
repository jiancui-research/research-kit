---
description: Turn the research idea and plan into a proposal or fellowship pitch (NABC + Heilmeier lenses, audience-aware, motivation-first) into .research/proposal/.
argument-hint: optional steering (e.g. "fellowship, 2 pages, non-specialist panel" or "conference paper pitch")
---

## User input

The user request arrives via the $ARGUMENTS placeholder. Treat it as steering on audience, genre, and limits, not the whole proposal.

## Audience / genre

Pick the genre from `$ARGUMENTS` (ask only if ambiguous), and set the spine accordingly:

- **Paper pitch / panel** — sells one idea to an expert who reads every word and judges feasibility and credibility. Keep the idea-and-evidence core; cost and timeline are minor.
- **Fellowship / grant** — pitches a multi-year agenda to a fast-skimming non-specialist who funds the person, not the exact plan. Keep background light (roughly a quarter of the space), lead with significance, and answer cost, timeline, and feasibility.

## Steps

1. **Read context.**
   - Read `./.research/memory/constitution.md` if it exists (skip silently otherwise) and honor its principles and writing voice.
   - Read `./.research/idea.md` (required upstream). If missing, stop and tell the user to run `/research.idea` first.
   - Read `./.research/plan.md` if it exists (validation, baselines, metrics, risks). If missing, proceed but note the validation section will be thinner.
   - Pull from these: the one-sentence thesis, problem and motivation, the gap, contributions, research questions, and any "have done" results.

2. **Load the skeleton.** Start from `templates/proposal-template.md`. Shape it to the genre chosen above.

3. **Draft the proposal, motivation-first.** Open on significance and one vivid concrete example, never "X is important [1,2,3]." Cover:
   - **One-sentence thesis.** Falsifiable, with a named mechanism, metric, and direction (`mechanism X improves metric M vs baseline B, under condition Z`). A topic is not a claim.
   - **Need / problem (why now).** A sharp question, not a topic area. Importance = consequence times a plausible attack: argue both "why it matters" and "why it is now tractable."
   - **Gap.** Argued, not listed. Name what prior work is missing and show the idea fills exactly that hole, no wider, no narrower.
   - **Approach / key idea.** The mechanism, distinguished from the nearest prior idea. Why it is new and hard.
   - **Benefit.** Quantified and better, not just different, versus the named alternative (the Competition in NABC).
   - **Plan and validation (pre-committed).** Name experiment, metric, baselines (the unmodified default system and a fairly tuned SOTA), substrate, and the observable result that would disconfirm the hypothesis. Plan a tree, not a sequence: a fallback branch per major risk.
   - **Feasibility.** Replace "will do" with "have done": cite at least one pilot number, prototype, or dataset already in hand.
   - **Contributions.** Artifacts that will exist (dataset, system, theorem, measured effect), each pointing at its evidence.
   - **For fellowship/grant only:** cost, timeline, intellectual merit and broader impacts if required; ensure the proposal, statement, and CV would tell one consistent story.

4. **Run both lenses over the draft** to find holes:
   - **NABC** (60-second version): Need -> Approach -> Benefit -> Competition. Iterate this one-liner until it is crisp.
   - **Heilmeier Catechism:** (1) goal in plain words, (2) how it's done today and the limits, (3) what's new and why it'll work, (4) who cares and the difference, (5) risks, (6) cost, (7) time, (8) the mid-term and final success exams. For a paper pitch, swap Q6-Q7 for "what have you already accomplished?" and "what is the plan for success?" Every question, especially Q8, must answer crisply.

5. **Validate** against this short checklist before finalizing:
   - The whole pitch compresses to one declarative, falsifiable sentence with a named metric.
   - The problem is a sharp question illustrated by one concrete example, not a topic area.
   - The gap is argued and is exactly the hole the idea fills.
   - Validation names experiment, metric, baselines (default + fair SOTA), substrate, and the disconfirming result.
   - Feasibility shows at least one "have done" artifact; risks form a tree with fallbacks.
   - Genre fit: page limits and format obeyed; for fellowships, background stays light and significance leads.
   - A smart non-specialist could restate problem, idea, and test after a two-minute read.

6. **Write** the result to `./.research/proposal/proposal.md` (`mkdir -p ./.research/proposal` first). Do not overwrite existing user content silently: if the file exists, preserve their text and clearly mark what you changed.

## Completion

Report the path `./.research/proposal/proposal.md`. End with: `Next: /research.review` (to pressure-test it) or `/research.paper` (to start drafting).
