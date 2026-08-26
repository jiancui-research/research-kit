---
description: Self-review panel. Simulate reviewers reading ONLY the submitted paper, score it, and list specific findings each with a suggested fix command. Writes .research/review/round-N.md only; never edits the paper or any other artifact.
argument-hint: optional focus (e.g. evaluation, related-work, a specific section) — omit for a full panel
---

## User input

The user request arrives via the `$ARGUMENTS` placeholder. It may narrow the round to one lens or section (e.g. `evaluation`, `related-work`, `intro`) or be empty for a full panel pass.

## What this phase is

This is the **self-review loop**: review your draft the way a skeptical program-committee panel will, **before** submission. A real reviewer sees **only the submitted paper**, so this command reads **only the manuscript** (plus venue/paper-type context). It never opens your `claims.md`, `eval/`, `proposal.md`, or task lists — judging from internal docs would give it insider knowledge a reviewer does not have and make the simulation less faithful.

It is **report-only**: it writes mock reviews + scores to `review/round-N.md` and nothing else. It does not edit the paper and does not write into any other lane (no auto-appending to `tasks/`). Each finding carries a **suggested fix command** so you can route it yourself, then re-run `/research.review` for the next round.

Division of labor: `/research.analyze` is the *internal* audit with full access to every artifact (claims, eval, design) — "do our own docs agree and stay in sync?" `/research.review` is the *external* reviewer simulation, paper-only — "how will an outsider react to what we submitted?"

## Steps

1. **Read the paper only.**
   - Read `./.research/memory/constitution.md` if present, for venue, paper-type, and voice (a reviewer knows the venue and its norms); skip silently if absent.
   - Read the manuscript — resolve its root from `./.research/paper-repo` (first line is the path; fall back to `./paper/` if the pointer is absent). This is the *only* artifact you review. If a section is missing or still an outline, treat it exactly as a reviewer would: a gap in the submission.
   - Determine the **paper type** (measurement / attack / defense / benchmark / systematization (SoK)) from the constitution, or failing that the paper itself, and load `.research/templates/paper/<type>.md` if present so venue-appropriate expectations apply, plus that type's block in `.research/templates/review/by-type.md` - what to press on for this kind of paper, which is mostly the inverse of the proof obligation the type carries. Do **not** open `claims.md`, `eval/`, `proposal.md`, `related-work.md`, or the task lists.
   - Determine the **venue family** and load its review guide: security (CCS, NDSS, S&P, USENIX Security, RAID, ACSAC) -> `.research/templates/review/security.md`; AI / ML / NLP (ACL and ARR venues, NeurIPS, ICML, ICLR, EMNLP) -> `.research/templates/review/ai-ml.md`. Take the family from the constitution's venue norms, else from the paper itself. When neither names a venue, say which family you assumed and why, in one line, before the panel runs - a security panel and an ML panel weigh the same paper differently. **Always** load `.research/templates/review/unfair-heuristics.md` on top, whatever the family.
   - A guide that is not in this repo is a gap to name, not to fill from memory: say which one was unavailable, suggest `/research.init`, and review without it.
   - Determine the round number **N**: the next integer after the highest existing `./.research/review/round-*.md` (start at 1).

2. **Convene the panel.** Simulate **3–4 reviewers, each with a distinct lens**, so findings do not collapse into one voice. Each judges **from the paper alone**:
   - **R1 — Domain expert / contribution:** is the novelty real and delimited from prior work *as the paper's related-work section argues it*?
   - **R2 — Empiricist / evaluation:** do the experiments *as presented* test each claim? fair tuned baselines, reported variance, no leakage, validated automatic/LLM judges — judged from the paper's tables, figures, and text?
   - **R3 — Skeptic / scope & overclaim:** does any verb (`solves`, `proves`, `guarantees`, `first`) outrun the evidence shown in the paper? any claim stated as settled but not backed by the paper's own results?
   - **R4 — Outsider / presentation & desk-reject:** is it self-contained and readable on one pass? scope-fit, length/format, anonymization, required sections (limitations, ethics), reproducibility statement.

3. **Each reviewer applies the specificity + fairness rules.** Every weakness must read `<X> is <weak/unsupported/unclear> because <concrete cause> (location in the paper); fix: <concrete change>.` A weakness whose "location in the paper" bracket cannot be filled is an impression, not a finding — cut it. Run every candidate weakness against `review/unfair-heuristics.md` and either **drop** it or **convert** it to the specific form that table gives; a criticism that would fire on almost any submission separates nothing. Apply the venue guide's own probes too — the security guide lists the axes a review must cover, the AI/ML guide separates soundness from excitement — and the paper type's probes from `review/by-type.md`. A paper can be polished, honest, and well written and still not discharge its type's proof obligation; that is the finding worth writing. Separate fatal flaws (invalidate a core claim) from fixable issues from minor nits.

4. **Score.** Give each reviewer a recommendation in the venue's terms (`reject` / `weak reject` / `borderline` / `weak accept` / `accept`) with a 2–3 sentence rationale that traces to its findings, plus a confidence level. Summarize the panel verdict (range + the single biggest driver up or down).

5. **Suggest a fix command per finding (do not run it or write to its file).** For each finding, name the one command the *user* would run to fix it — a suggestion in the report, not an action this command takes:
   - unsupported / overclaimed text, framing, voice -> `/research.implement paper <section>`
   - weak related-work delta → `/research.relatedwork`
   - a claim that needs new or stronger evidence → `/research.implement` (add / run the experiment)
   - a number that looks wrong or internally inconsistent → `/research.implement` (re-check) or `/research.analyze` (trace it across artifacts)
   - a contribution or feasibility concern → `/research.proposal` or `/research.feasibility`
   This command writes none of those files; the user routes the findings by hand and loops.

## Write the round file

Write `./.research/review/round-N.md` (start from `.research/templates/review-template.md` if it exists), creating `./.research/review/` as needed and **never overwriting an existing round file**. This is the **only** file this command writes. Structure it as the panel output, not prose:

- **Panel verdict line**: per-reviewer recommendation + the score range + the biggest driver.
- One block per reviewer (R1–R4): summary, strengths, weaknesses (ordered by severity, specificity rule applied), score + rationale + confidence.
- **Findings table**: `finding | severity (fatal/major/minor) | location in paper | suggested fix command`.
- **Desk-reject gate** (binary, all must pass): scope, length/format, anonymization, required sections, reproducibility statement.

## Validate (short checklist)

- Only the manuscript (+ venue context) was read; `claims.md` / `eval/` / `proposal.md` / task lists were not opened.
- 3–4 distinct reviewer lenses, not one voice repeated.
- Every weakness is specific, located in the paper, and paired with a concrete fix; none could apply to any paper.
- The unfair reflexes are absent or explicitly justified; fatal flaws separated from fixable and minor.
- Every finding carries exactly one suggested fix command.
- Only `review/round-N.md` was written — no other artifact (paper, claims, eval, tasks) was touched.

## Completion

Report `./.research/review/round-N.md`, the panel score range, and finding counts. Then: resolve findings via their suggested commands (`/research.implement paper <section>`, `/research.relatedwork`, `/research.implement`, ...), and re-run `/research.review` until no high-severity findings remain. (`/research.rebuttal` is auxiliary and post-submission.)
