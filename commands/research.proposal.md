---
description: Pipeline entry. Turn a raw research idea into proposal.md, a readable 1-3 page argument (falsifiable thesis, argued gap, pre-committed validation plan, venue + paper-type).
argument-hint: a sentence or paragraph describing the rough idea (or steering to refine an existing proposal)
---

## User input
The raw idea arrives via the $ARGUMENTS placeholder. It is the INPUT to the whole pipeline. Treat it as raw material to formalize, not a finished pitch. There is no separate idea command - the idea is folded into this proposal.

## Steps
1. Read `./.research/memory/constitution.md` if it exists (research principles + writing voice); skip silently otherwise.
2. **Refine path.** If `./.research/proposal.md` already exists, treat this run as a refine - preserve the user's text and clearly mark what you changed; never silently overwrite. If the existing file follows the old form-style template (an NABC section, a Heilmeier catechism, checklists), offer to restructure it into the 7-part argument, carrying every idea over. (Survey-driven sharpening of the Gap and positioning is owned by `/research.relatedwork`, not here.)
3. Parse `$ARGUMENTS` into the spine: problem, hinted mechanism, who cares, any prior work named, any venue hinted.
4. Make informed guesses for everything missing. Infer the **paper-type** (measurement / attack / defense / benchmark / systematization (SoK)) and a plausible **target venue** from the problem; consult `.research/templates/venue-norms.md` to choose the venue and inherit its conventions, and if a matching `.research/templates/paper/<type>.md` exists, read it for type-specific framing.
5. Ask **at most 3** clarifying questions, and ONLY for framing-critical unknowns that change the whole pitch (e.g., the core mechanism, the metric, or the threat model). If the proposal is workable without an answer, guess and record the guess in the numbered **Open assumptions** block - never as an inline bracket.
6. **Story first.** Draft the 7-part spine as seven plain sentences (one per part) and show them in chat BEFORE writing any prose. If the seven sentences do not tell a story, no amount of polish will fix it - fix the spine first.
7. Expand the spine into `./.research/proposal.md`, starting from `.research/templates/proposal-template.md` (`mkdir -p ./.research` first). Write part 1 (problem & motivation) last. Revise for clarity first, then cut what does not serve the argument: splitting a fused sentence is always allowed; fusing sentences to save space never is.

## What the document contains
The template's shape and nothing more:
- A one-line header (target venue + one-line reason, paper type) and one italic NABC elevator paragraph - the only compressed restatement of the pitch in the document.
- The 7 numbered parts, each within its length budget: problem & motivation (~1 para, written last), gap (~1 para, argued not listed), key idea (thesis as one declarative sentence of at most 35 words naming metric and baseline, plus 1 para of mechanism), why new & hard (~1 para), plan & validation (hypotheses with direction + falsifier, substrate, metrics, baselines, trials, confounds with controls - these hypotheses are the research questions), contributions (bullets with C-ids and evidence pointers), risks & feasibility (~1 para, have-done first, risk tree).
- A footer: the numbered **Open assumptions** block + **References**.

## What the run must verify (report in chat - lens text never enters the document)
After drafting, check the draft against these lenses and report pass/fail in chat. Fix a failure by editing the document, but never paste the lens or checklist into it:
- All 8 Heilmeier questions answer crisply (paper variant: Q6 becomes "what have I already done?", Q7 becomes "what is the plan for success?").
- The thesis is one declarative, falsifiable sentence, at most 35 words, with a named metric and named baseline.
- The gap is argued (what prior work misses, why that matters), not a citation list.
- The baselines could actually beat you: the unmodified default AND a fairly tuned state of the art, never only yourself.
- Nondeterministic results plan repeated trials with variance; every confound is named with its control.
- No sentence carries more than one claim, and the main point lands in the first ten words.
- The whole document is at most 3 pages, and a smart non-specialist can restate problem, idea, and test after a two-minute read.

## Readability gate (clarity and simplicity come first - before length, before completeness)
- One claim per sentence: a sentence asserting two things joined by "and" or a semicolon gets split. Splitting for clarity is always allowed.
- The main point lands in the first ~10 words; elaboration goes after a colon or into a list, never into stacked clauses.
- Each sentence starts from what the reader just learned (given -> new); prefer the concrete example ("a poisoned pull request") to the category label ("poisoned context").
- Plain words; do not jam jargon. Define every term of art at first use, then reuse the same word instead of a synonym.
- Cite by bare name in prose ("unlike SpecEval"); full citations live only in References.
- No inline `[ASSUMPTION: ...]` brackets anywhere in prose - every inferred value goes in the numbered Open assumptions block.
- Each idea appears exactly once; the thesis exactly twice (elevator paragraph + part 3) - satisfied by cutting duplicates, never by fusing claims into one sentence.

## Completion
Report the path `./.research/proposal.md` and the lens verification results. End with: `Next: /research.relatedwork` (survey + position), or `/research.feasibility` if related work is already done.
