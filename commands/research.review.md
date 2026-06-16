---
description: Self-review panel + router. Simulate a reviewer panel, score the draft, route each finding to its owning command, auto-append evidence-gap experiments, and loop until clean. Writes .research/review/round-N.md; never rewrites the paper.
argument-hint: optional focus (e.g. evaluation, related-work, a specific section) — omit for a full panel
---

## User input

The user request arrives via the `$ARGUMENTS` placeholder. It may narrow the round to one lens or section (e.g. `evaluation`, `related-work`, `intro`) or be empty for a full panel pass.

## What this phase is

This is the **self-review loop**: review your OWN draft the way a skeptical program-committee panel will, **before** submission. This command is a **router and tracker**, not an editor. It simulates a panel of reviewers, writes mock reviews + scores to `review/round-N.md`, **routes** each finding to the command that owns the fix, and **auto-appends** new experiment tasks for evidence gaps to `tasks/experiment.md`. It **never rewrites the paper** and never edits a claim, experiment, or section to make a finding go away — it records the finding and hands it off. (Distinct from `/research.analyze`, which is an objective read-only consistency audit; review is subjective panel judgment + routing + a scored loop.)

## Steps

1. **Read the artifacts (read-only on all but the round file and the experiment task list).**
   - Read `./.research/memory/constitution.md` if present (venue, paper-type, voice); skip silently if absent.
   - Read what exists: `./.research/proposal.md`, `./.research/related-work.md`, `./.research/feasibility.md`, `./.research/tasks/experiment.md`, `./.research/tasks/paper.md`, `./.research/claims.md`, `./.research/experiments/`, and `./.research/paper/`. Note any missing artifact as a gap rather than failing.
   - Determine the **paper type** (measurement / attack / defense / benchmark / systematization (SoK)) from `proposal.md` and load `.research/templates/paper/<type>.md` if present so type-specific bars apply.
   - Determine the round number **N**: the next integer after the highest existing `./.research/review/round-*.md` (start at 1).

2. **Convene the panel.** Simulate **3–4 reviewers, each with a distinct lens**, so findings do not collapse into one voice:
   - **R1 — Domain expert / contribution:** is the novelty real and delimited from the closest prior work? (cross-check `related-work.md`).
   - **R2 — Empiricist / evaluation:** do the experiments directly test each claim? fair tuned baselines, reported variance, no leakage, validated automatic/LLM judges? (cross-check `claims.md` and `experiments/`).
   - **R3 — Skeptic / scope & overclaim:** does any verb (`solves`, `proves`, `guarantees`, `first`) outrun the evidence? any `claims.md` row not `supported` but stated as settled?
   - **R4 — Outsider / presentation & desk-reject:** is it self-contained and readable on one pass? scope-fit, length/format, anonymization, required sections (limitations, ethics), reproducibility statement.

3. **Each reviewer applies the specificity + fairness rules.** Every weakness must read `<X> is <weak/unsupported/unclear> because <concrete cause> (location); fix: <concrete change>.` Drop or justify the unfair reflexes (`obvious in hindsight`, `too simple`, `too narrow`, `doesn't beat SOTA`, `I'd have done it differently`) — a criticism that could apply to any paper is not a finding. Separate fatal flaws (invalidate a core claim) from fixable issues from minor nits.

4. **Score.** Give each reviewer a recommendation in the venue's terms (`reject` / `weak reject` / `borderline` / `weak accept` / `accept`) with a 2–3 sentence rationale that traces to its findings, plus a confidence level. Summarize the panel verdict (range + the single biggest driver up or down).

5. **Route every finding to its owning command.** This is the load-bearing step — each finding gets exactly one next action:
   - unsupported / overclaimed text, framing, voice → `/research.paper <section>`
   - missing or weak related-work delta → `/research.relatedwork`
   - a claim that needs new or stronger evidence → an experiment (see step 6) and `/research.experiment` to run it
   - a result that exists but is mis-stated in `claims.md` → `/research.experiment` (re-score the claim)
   - a feasibility / GO-NO-GO concern or a contribution gap → `/research.feasibility` or `/research.proposal`

6. **Auto-append experiment tasks for evidence gaps.** For each finding that needs new evidence, **append** a task to `./.research/tasks/experiment.md` (do not rewrite existing tasks): one line per gap, tagged `from review round N`, naming the claim id it backs and the verdict it must produce. This keeps the experiment/paper loop fed from the review.

## Write the round file

Write `./.research/review/round-N.md` (start from `.research/templates/review-template.md` if it exists), creating `./.research/review/` as needed and **never overwriting an existing round file**. Structure it as the panel output, not prose:

- **Panel verdict line**: per-reviewer recommendation + the score range + the biggest driver.
- One block per reviewer (R1–R4): summary, strengths, weaknesses (ordered by severity, specificity rule applied), score + rationale + confidence.
- **Routing table**: `finding | severity (fatal/major/minor) | owning command | status (open)`.
- **Auto-appended experiments**: the list of tasks added to `tasks/experiment.md` this round (claim id + required verdict + `from review round N`).
- **Desk-reject gate** (binary, all must pass): scope, length/format, anonymization, required sections, reproducibility statement.

## Validate (short checklist)

- 3–4 distinct reviewer lenses, not one voice repeated.
- Every weakness is specific, located, and paired with a concrete fix; none could apply to any paper.
- The unfair reflexes are absent or explicitly justified; fatal flaws separated from fixable and minor.
- Every finding is routed to exactly one owning command in the routing table.
- Every evidence gap was appended to `tasks/experiment.md`, tagged `from review round N`.
- Scores trace to the findings, not to a gut feeling; desk-reject gate checked.
- No paper section, claim, or experiment was rewritten by this command.

## Completion

Report the path `./.research/review/round-N.md`, the panel score range, and the counts (fatal / major / minor findings, and experiments appended). Then end with: `Next: resolve findings via their routed commands (/research.paper, /research.relatedwork, /research.experiment, ...), then re-run /research.review for round N+1; loop until no high-severity findings remain. (/research.rebuttal is auxiliary — post-submission.)`
