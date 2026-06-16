---
description: Assist the user's own writing of a paper section — outline it, or critique their draft, every claim traceable to claims.md. Human-led; does not ghostwrite.
argument-hint: section name (e.g. intro, related-work, eval); optionally a pasted draft or path to critique, or "draft <section>" to request full prose
---

## User input
The user request arrives via the `$ARGUMENTS` placeholder. It names one section (e.g. `intro`, `abstract`, `related-work`, `method`, `eval`, `threat-model`, `ethics`, `conclusion`) and may also paste draft prose, point to a draft file, or explicitly ask to `draft` the section. If empty, pick the next section in the type's skeleton order whose `tasks/paper.md` status is not `done`.

## What this phase is
**The paper is human-led — the user writes, you assist.** You do three things and nothing else:
- **OUTLINE (default):** for the named section, produce an argument-skeleton — the beats in order, which `claims.md` ids each beat must hit, which evidence/citations back them — for the *user* to write in their own voice.
- **CRITIQUE:** if the user pasted a draft or pointed to one, review their prose against the constitution voice, claim traceability, overclaims, and tightening. Edit nothing; return specific, located findings.
- **DRAFT (only on explicit request):** generate full prose *only* when `$ARGUMENTS` says so (e.g. `draft intro`). Even then, match the user's voice and keep it tight; never produce walls of generic text.

Runs in **parallel** with `/research.experiment`: experiment writes verdicts into `claims.md`; you read them. Framing sections (intro, related work, method) can be outlined or drafted now; results sections (eval, abstract, conclusion) stay **blocked** until their claims are supported — outline them, but tag every result beat `[UNVERIFIED]` until `claims.md` backs it.

## Steps

1. **Read context.**
   - Read `./.research/memory/constitution.md` if present (writing voice, venue, paper-type); skip silently if absent.
   - Read the upstream artifacts: `./.research/tasks/paper.md` (the section task list + READY/BLOCKED status), `./.research/proposal.md` (problem, gap, contributions, RQs, venue, paper-type), `./.research/related-work.md`, and `./.research/claims.md`. If `claims.md` is missing or empty, warn that result claims are unverifiable, then proceed with framing sections only.
   - Determine the paper type (measurement / attack / defense / benchmark / systematization (SoK)) from the proposal; default to the closest match and say which you chose. Load the matching skeleton from `.research/templates/paper/<type>.md`.
   - Load the relevant craft guide: `.research/templates/sections/abstract-intro.md` for abstract/intro, `.research/templates/sections/figures-tables.md` for results/figures/tables.

2. **Pick the section and the mode.**
   - Section: from `$ARGUMENTS`, else the next non-`done` section in skeleton order (abstract usually last).
   - Mode: **CRITIQUE** if a draft is pasted or pointed to; **DRAFT** if `$ARGUMENTS` explicitly asks; otherwise **OUTLINE**.
   - `mkdir -p ./.research/paper`. Write to `./.research/paper/<section>.md`. Never overwrite the user's existing prose — append your outline/critique under a clearly labeled heading, or write to `<section>.outline.md` / `<section>.critique.md`, and say what you did.

3. **OUTLINE mode (default).** For the named section, lay out the argument the *user* will write:
   - The **beats in order** following the type skeleton (one line each: what this beat must establish).
   - For each result beat, the **claim id(s)** it must hit (e.g. `→ C3`) and the **evidence** (experiment id / figure / table) backing it; if no backing entry exists, mark `[UNVERIFIED — add to claims.md]`.
   - The **citations** to slot in, pulled from `related-work.md` only; mark missing ones `[cite?]`, never invented.
   - The **load-bearing reminders** for this section (see step 5) as short notes against the relevant beat — not prose.
   Hand back a skeleton, not paragraphs. The user fills the words.

4. **CRITIQUE mode.** Read the user's draft and return located, specific findings (file + line/quote), grouped:
   - **Voice** — drift from the constitution voice; passive where active "we" belongs; hedging or filler.
   - **Claim traceability** — every empirical sentence mapped to a `claims.md` id; flag any unmapped sentence `[UNVERIFIED — add to claims.md]` and any claim stated stronger than its verdict in `claims.md`.
   - **Overclaims** — bare `first`/`solves`/`guarantees`/`proves` without a scope qualifier or sufficient evidence; superlatives without a number.
   - **Tightening** — sentences to cut or merge, motivation buried under method, missing "so what" on a finding.
   Do not rewrite the draft. Give the user the findings; they revise.

5. **Load-bearing craft (apply in every mode).**
   - **Lead with motivation, not method.** Open the intro with why the target matters (named example, dated incident, or concrete number), surface the tension, then state the gap in one recitable sentence.
   - **Scope every novelty claim** (first *systematic* / *large-scale* study of X *on* Y). Bare "first" invites counterexamples.
   - **Use active "we" voice** for what you did; reserve passive for stated facts and system behavior.
   - **Pair every statistic with a named, recognizable instance and its absolute count** beside the percentage.
   - **Reserve "surprisingly" for genuinely surprising results;** attach a number to every superlative or performance adjective.
   - **Name the artifact once early** (italicized, with expansion) and reuse it in headers and topic sentences.
   - **Close each major finding with a "so what" sentence** (who is affected / what it implies).
   - **Be honest:** report effectiveness *and* cost/overhead; state limitations plainly; don't inflate confirmatory results into discoveries.
   - In related work, synthesize prior work into themes and end each paragraph with an explicit delta ("Unlike these, we...").

6. **Paper-type and venue awareness.**
   - Place the threat model per venue: a standalone, labeled section (adversary goal, knowledge, capabilities, out-of-scope) at security venues; folded into the intro at ML venues.
   - Include the beats the skeleton marks load-bearing for the type (methodology/ground-truth for measurement, countermeasures for attack, security+performance evaluation for defense, task tuple + construction filters for benchmark, taxonomy axes for SoK).
   - Add the roadmap sentence and standalone ethics/disclosure section when the venue expects them; omit gracefully otherwise.

7. **Update `tasks/paper.md`.** Set the section's status (e.g. `outlined`, `drafted`, `critiqued`, or `blocked`) and note any `[UNVERIFIED]`/`[cite?]` markers blocking it. Don't invent tasks the file doesn't have; just update status for the section you touched.

## Validate (short checklist)
- Default behavior produced an **outline**, not ghostwritten prose; full prose only on explicit `draft` request.
- A reader can state the gap in one sentence after the intro beats (intro/abstract).
- Every novelty claim is scoped; every statistic pairs with a named instance + absolute count.
- Every result beat is tagged to a `claims.md` id or flagged `[UNVERIFIED]`; nothing invented.
- Related work hits a delta per theme; the closest baseline is forward-referenced from the intro.
- Threat model matches venue convention; disclosure + artifact note present if the work touches real systems.
- No user prose was overwritten; critique findings are located, not vague.

## Completion
Report the path(s) touched (e.g. `./.research/paper/intro.outline.md`) and the updated `./.research/tasks/paper.md` status. List any `[UNVERIFIED]` or `[cite?]` markers the user must resolve. Then end with: `Next: /research.analyze` (or `Next: /research.paper <next-section>` if sections remain, and rerun `/research.experiment` to land the evidence that unblocks result sections).
