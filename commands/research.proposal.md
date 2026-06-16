---
description: Pipeline entry. Turn a raw research idea into a sharp, falsifiable proposal.md (NABC, argued gap, measurable contributions, testable RQs, venue + paper-type).
argument-hint: a sentence or paragraph describing the rough idea (or steering to refine an existing proposal)
---

## User input
The raw idea arrives via the $ARGUMENTS placeholder. It is the INPUT to the whole pipeline. Treat it as raw material to formalize, not a finished pitch. There is no separate idea command - the idea is folded into this proposal.

## Steps
1. Read `./.research/memory/constitution.md` if it exists (research principles + writing voice); skip silently otherwise.
2. **Refine path.** If `./.research/related-work.md` exists, read it and fold its positioning in: use its argued gap, its named closest baseline, and its delta sentence to sharpen the Gap and Competition below rather than re-deriving them. If `./.research/proposal.md` already exists, treat this run as a refine - preserve the user's text and clearly mark what you changed; never silently overwrite.
3. Parse `$ARGUMENTS` into the spine: problem, hinted mechanism, who cares, any prior work named, any venue hinted.
4. Make informed guesses for everything missing. Infer the **paper-type** (measurement / attack / defense / benchmark / systematization (SoK)) and a plausible **target venue** from the problem; consult `.research/templates/venue-norms.md` to choose the venue and inherit its conventions, and if a matching `.research/templates/paper/<type>.md` exists, read it for type-specific framing.
5. Ask **at most 3** clarifying questions, and ONLY for framing-critical unknowns that change the whole pitch (e.g., the core mechanism, the metric, or the threat model). If the proposal is workable without an answer, guess and label it `[ASSUMPTION]` instead of asking.
6. Write/update `./.research/proposal.md`, starting from `.research/templates/proposal-template.md`. `mkdir -p ./.research` first.

## What proposal.md must contain
- **One-sentence thesis** (falsifiable), repeated everywhere: `<mechanism X> improves <metric M> vs <baseline B>, under <condition Z>, at equal <cost>`. Every slot filled, no empty slots. A topic ("make agents safer") is not a thesis.
- **Problem** as a sharp question plus **one concrete motivating example** (a vivid molehill, not "X is important [1,2,3]").
- **NABC**: Need (specific, sized opportunity) -> Approach (concrete mechanism + the insight that makes it work) -> Benefit (quantified, better not just different) -> Competition (nearest alternative AND the do-nothing default, and why yours wins). Iterate the 60-second NABC one-liner until it is crisp.
- **Why now**: importance = consequence x plausibility. Argue BOTH the stakes (who is hurt if unsolved) and why it is newly tractable (new data, tool, access, or method) in the same breath.
- **Gap** as an argument, not a citation list: "Prior work does X but leaves Y open / assumes Z, which fails when <situation>; we fill exactly Y" - no wider, no narrower. On the refine path, inherit this from `related-work.md`.
- **Contributions**: things that will *exist* (dataset, system, theorem, measured effect), each measurable and each pointing at the evidence that will support it.
- **Research questions**: testable. For each RQ name the predicted direction and a falsifier (the observable result that would prove it wrong).
- **Target venue + paper-type**, with a one-line reason.
- Mark every inferred value `[ASSUMPTION]` so the user can correct it.

## Validate before finishing (short checklist)
- The thesis is one declarative, falsifiable sentence with a named metric and named baseline.
- The problem is a sharp question with a concrete example, not a topic area.
- Importance is argued as consequence x plausible attack, not stakes alone.
- The gap is argued (what prior work misses), not a list of citations.
- Each contribution is measurable and tied to evidence; each RQ has a direction and a falsifier.
- Venue and paper-type are stated with a reason; inferred values are marked `[ASSUMPTION]`.
- A smart non-specialist could restate the problem, idea, and test after a two-minute read.

## Completion
Report the path `./.research/proposal.md`. End with: `Next: /research.relatedwork` (survey + position), or `/research.feasibility` if related work is already done.
