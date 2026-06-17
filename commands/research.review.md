---
description: Self-review panel. Simulate reviewers reading ONLY the submitted paper, score it, and list specific findings each with a suggested fix command. Writes .research/review/round-N.md only; never edits the paper or any other artifact.
argument-hint: optional focus (e.g. evaluation, related-work, a specific section) — omit for a full panel
---

## User input

The user request arrives via the `$ARGUMENTS` placeholder. It may narrow the round to one lens or section (e.g. `evaluation`, `related-work`, `intro`) or be empty for a full panel pass.

## What this phase is

This is the **self-review loop**: review your draft the way a skeptical program-committee panel will, **before** submission. A real reviewer sees **only the submitted paper**, so this command reads **only `./paper/`** (plus venue/paper-type context). It never opens your `claims.md`, `eval/`, `proposal.md`, or task lists — judging from internal docs would give it insider knowledge a reviewer does not have and make the simulation less faithful.

It is **report-only**: it writes mock reviews + scores to `review/round-N.md` and nothing else. It does not edit the paper and does not write into any other lane (no auto-appending to `tasks/`). Each finding carries a **suggested fix command** so you can route it yourself, then re-run `/research.review` for the next round.

Division of labor: `/research.analyze` is the *internal* audit with full access to every artifact (claims, eval, design) — "do our own docs agree and stay in sync?" `/research.review` is the *external* reviewer simulation, paper-only — "how will an outsider react to what we submitted?"

## Steps

1. **Read the paper only.**
   - Read `./.research/memory/constitution.md` if present, for venue, paper-type, and voice (a reviewer knows the venue and its norms); skip silently if absent.
   - Read `./paper/` — the submitted manuscript. This is the *only* artifact you review. If a section is missing or still an outline, treat it exactly as a reviewer would: a gap in the submission.
   - Determine the **paper type** (measurement / attack / defense / benchmark / systematization (SoK)) from the constitution, or failing that the paper itself, and load `.research/templates/paper/<type>.md` if present so venue-appropriate expectations apply. Do **not** open `claims.md`, `eval/`, `proposal.md`, `related-work.md`, or the task lists.
   - Determine the round number **N**: the next integer after the highest existing `./.research/review/round-*.md` (start at 1).

2. **Convene the panel.** Simulate **3–4 reviewers, each with a distinct lens**, so findings do not collapse into one voice. Each judges **from the paper alone**:
   - **R1 — Domain expert / contribution:** is the novelty real and delimited from prior work *as the paper's related-work section argues it*?
   - **R2 — Empiricist / evaluation:** do the experiments *as presented* test each claim? fair tuned baselines, reported variance, no leakage, validated automatic/LLM judges — judged from the paper's tables, figures, and text?
   - **R3 — Skeptic / scope & overclaim:** does any verb (`solves`, `proves`, `guarantees`, `first`) outrun the evidence shown in the paper? any claim stated as settled but not backed by the paper's own results?
   - **R4 — Outsider / presentation & desk-reject:** is it self-contained and readable on one pass? scope-fit, length/format, anonymization, required sections (limitations, ethics), reproducibility statement.

3. **Each reviewer applies the specificity + fairness rules.** Every weakness must read `<X> is <weak/unsupported/unclear> because <concrete cause> (location in the paper); fix: <concrete change>.` Drop or justify the unfair reflexes (`obvious in hindsight`, `too simple`, `too narrow`, `doesn't beat SOTA`, `I'd have done it differently`) — a criticism that could apply to any paper is not a finding. Separate fatal flaws (invalidate a core claim) from fixable issues from minor nits.

4. **Score.** Give each reviewer a recommendation in the venue's terms (`reject` / `weak reject` / `borderline` / `weak accept` / `accept`) with a 2–3 sentence rationale that traces to its findings, plus a confidence level. Summarize the panel verdict (range + the single biggest driver up or down).

5. **Suggest a fix command per finding (do not run it or write to its file).** For each finding, name the one command the *user* would run to fix it — a suggestion in the report, not an action this command takes:
   - unsupported / overclaimed text, framing, voice → `/research.paper <section>`
   - weak related-work delta → `/research.relatedwork`
   - a claim that needs new or stronger evidence → `/research.eval` (add / run the experiment)
   - a number that looks wrong or internally inconsistent → `/research.eval` (re-check) or `/research.analyze` (trace it across artifacts)
   - a contribution or feasibility concern → `/research.proposal` or `/research.feasibility`
   This command writes none of those files; the user routes the findings by hand and loops.

## Write the round file

Write `./.research/review/round-N.md` (start from `.research/templates/review-template.md` if it exists), creating `./.research/review/` as needed and **never overwriting an existing round file**. This is the **only** file this command writes. Structure it as the panel output, not prose:

- **Panel verdict line**: per-reviewer recommendation + the score range + the biggest driver.
- One block per reviewer (R1–R4): summary, strengths, weaknesses (ordered by severity, specificity rule applied), score + rationale + confidence.
- **Findings table**: `finding | severity (fatal/major/minor) | location in paper | suggested fix command`.
- **Desk-reject gate** (binary, all must pass): scope, length/format, anonymization, required sections, reproducibility statement.

## Validate (short checklist)

- Only `./paper/` (+ venue context) was read; `claims.md` / `eval/` / `proposal.md` / task lists were not opened.
- 3–4 distinct reviewer lenses, not one voice repeated.
- Every weakness is specific, located in the paper, and paired with a concrete fix; none could apply to any paper.
- The unfair reflexes are absent or explicitly justified; fatal flaws separated from fixable and minor.
- Every finding carries exactly one suggested fix command.
- Only `review/round-N.md` was written — no other artifact (paper, claims, eval, tasks) was touched.

## Completion

Report the path `./.research/review/round-N.md`, the panel score range, and the counts (fatal / major / minor findings). Then end with: `Next: resolve findings via their suggested commands (/research.paper, /research.relatedwork, /research.eval, ...), then re-run /research.review for round N+1; loop until no high-severity findings remain. (/research.rebuttal is auxiliary — post-submission.)`
