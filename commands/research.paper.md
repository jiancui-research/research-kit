---
description: Draft paper sections into .research/paper/, paper-type aware, every claim traceable to claims.md.
argument-hint: optional section name (e.g. intro, related-work, eval) — omit to draft the next missing section
---

## User input
The user request arrives via the `$ARGUMENTS` placeholder. It may name one section (e.g. `intro`, `abstract`, `related-work`, `method`, `eval`, `threat-model`, `ethics`, `conclusion`) or be empty.

## Steps

1. **Read context.**
   - Read `./.research/memory/constitution.md` if it exists (for writing voice, venue, paper-type); skip silently if absent.
   - Read upstream artifacts: `./.research/idea.md` (problem, gap, contributions, RQs, venue, paper-type), `./.research/plan.md`, `./.research/related-work.md`, and `./.research/claims.md`. If `claims.md` is missing or empty, warn the user that claims will be unverifiable, then proceed.
   - Determine the paper type (measurement / attack / defense / benchmark / systematization (SoK)) from `idea.md`; default to the closest match and say which you chose. Load the matching skeleton from `.research/templates/paper/<type>.md`.

2. **Pick the section.**
   - If `$ARGUMENTS` names a section, draft only that one.
   - If empty, draft the next missing section in the type's skeleton order (abstract is usually drafted last).
   - `mkdir -p ./.research/paper`. Never overwrite an existing section file without saying so and showing what changed.

3. **Draft the section** following the skeleton beat for that section and the constitution's voice. When drafting the abstract or introduction, also load `.research/templates/sections/abstract-intro.md`; when designing figures, tables, or a results section, load `.research/templates/sections/figures-tables.md`. Apply across all sections:
   - **Lead with motivation, not method.** Open the intro by establishing why the target matters (a named example, dated incident, or concrete number), surface the tension, then state the gap so a reader can recite it in one sentence.
   - **Scope every novelty claim** with a qualifier (first *systematic* / *large-scale* study of X *on* Y). Bare "first" invites counterexamples.
   - **Use active "we" voice** for what you did; reserve passive voice for stated facts and system behavior.
   - **Pair every statistic with a named, recognizable instance and its absolute count** beside the percentage.
   - **Reserve "surprisingly" for genuinely surprising results**; attach a number to every superlative or performance adjective.
   - **Name the artifact once early** (italicized, with expansion) and reuse it in headers and topic sentences.
   - **Close each major finding with a "so what" sentence** (who is affected / what it implies).
   - **Be honest about results.** Report effectiveness *and* cost/overhead; state limitations plainly; do not inflate confirmatory results into discoveries.

4. **Traceability and citations.**
   - Every empirical claim in the draft must map to an entry in `claims.md`. Tag claims inline with their id (e.g. `[claim: C3]`); flag any claim with no backing entry as `[UNVERIFIED — add to claims.md]` rather than inventing evidence.
   - Cite from `related-work.md` only; mark gaps as `[cite?]` instead of fabricating references. In the related-work section, synthesize prior work into themes and end each paragraph with an explicit delta ("Unlike these, we...").

5. **Paper-type and venue awareness.**
   - Place the threat model per venue: a standalone, labeled section (adversary goal, knowledge, capabilities, out-of-scope) at security venues; folded into the intro at ML venues.
   - Include the section beats the skeleton marks as load-bearing for the type (e.g. methodology/ground-truth for measurement, countermeasures for attack, security+performance evaluation for defense, task tuple + construction filters for benchmark).
   - Add the roadmap sentence and standalone ethics/disclosure section when the venue expects them; omit gracefully otherwise.

6. **Validate** the drafted section against a short checklist:
   - Can a reader state the gap in one sentence after the intro? (intro/abstract)
   - Is every novelty claim scoped, and every statistic paired with a named instance + absolute count?
   - Is every empirical claim tagged to a `claims.md` id (or flagged unverified)?
   - Does related work end each paragraph with a delta, and is the closest baseline forward-referenced from the intro?
   - Does the threat model match venue convention, and is there a disclosure + artifact note if the work touches real systems?

## Completion
Report the written path(s) (e.g. `./.research/paper/intro.md`), list any `[UNVERIFIED]` or `[cite?]` markers the user must resolve, and end with: `Next: /research.paper <next-section>` or, when all sections are drafted, `Next: /research.analyze`.
