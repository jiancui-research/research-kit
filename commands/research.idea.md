---
description: Turn a rough idea into a sharp, falsifiable idea.md (NABC, gap, measurable contributions, testable RQs, venue + paper-type).
argument-hint: a sentence or paragraph describing the rough idea
---

## User input
The rough idea arrives via the $ARGUMENTS placeholder. Treat it as raw material, not a finished pitch.

## Steps
1. Read `./.research/memory/constitution.md` if it exists (research principles + writing voice); skip silently otherwise.
2. Parse `$ARGUMENTS` into the spine: problem, hinted approach, who cares, any prior work named, any venue hinted.
3. Make informed guesses for everything missing. Infer the **paper-type** (measurement / attack / defense / benchmark / systematization (SoK)) and a plausible **target venue** from the problem; consult `templates/venue-norms.md` to choose the venue and inherit its conventions, and if a matching `templates/paper/<type>.md` exists, read it for type-specific framing.
4. Ask **at most 3** clarifying questions, and ONLY for genuinely critical unknowns that change the whole framing (e.g., the core mechanism, the metric, or the threat model). If the idea is workable without an answer, guess and label it `[ASSUMPTION]` instead of asking.
5. Write/update `./.research/idea.md`, starting from `templates/idea-template.md`. `mkdir -p ./.research`. If `idea.md` already exists, say so and merge rather than silently overwriting user content.

## What idea.md must contain
- **One-sentence thesis** (falsifiable): `<mechanism X> improves <metric M> vs <baseline B>, under <condition Z>, at equal <cost>`. Every slot filled, no empty slots. A topic ("make agents safer") is not a thesis.
- **Problem** as a sharp question plus **one concrete motivating example** (a vivid molehill, not "X is important [1,2,3]").
- **NABC**: Need (specific, sized opportunity) -> Approach (concrete mechanism) -> Benefit (quantified, better not just different) -> Competition (nearest alternative and why yours wins).
- **Why now**: importance = consequence x a plausible attack. Argue both the stakes and why the problem is newly tractable.
- **Gap** as an argument, not a citation list: "Prior work does X but leaves Y open / assumes Z, which fails when <situation>; we fill exactly Y" - no wider, no narrower.
- **Contributions**: things that will *exist* (dataset, system, theorem, measured effect), each measurable and each pointing at the evidence that will support it.
- **Research questions**: testable. For each RQ name the predicted direction and a falsifier (the observable result that would prove it wrong).
- **Target venue + paper-type**, with a one-line reason.
- **Feasibility**: at least one "have done" artifact if any exists (pilot number, prototype, data in hand); otherwise the smallest pilot that would de-risk the idea.
- Mark every inferred value `[ASSUMPTION]` so the user can correct it.

## Validate before finishing (short checklist)
- The thesis is one declarative, falsifiable sentence with a named metric and named baseline.
- The problem is a question with a concrete example, not a topic area.
- The gap is argued (what prior work misses), not a list of citations.
- Each contribution is measurable and tied to evidence; each RQ has a direction and a falsifier.
- Venue and paper-type are stated with a reason.
- A smart non-specialist could restate the problem, idea, and test after a two-minute read.

## Completion
Report the path `./.research/idea.md`, then: `Next: /research.relatedwork`.
