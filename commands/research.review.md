---
description: Write a fair, specific, actionable peer review of another author's paper; write .research/review/<id>.md.
argument-hint: path or notes for the paper under review, the venue, and (optional) the paper type
---

## User input
The user request arrives via the $ARGUMENTS placeholder (e.g., a path/DOI/title of the paper to review, the target venue or review guideline, the paper type, and any focus the editor asked for).

## Steps
1. Read `./.research/memory/constitution.md` if present (skip silently otherwise). This is a review of someone else's paper, so do NOT assume `idea.md`/`plan.md` describe it; treat the paper under review as the sole subject. If the paper content/path was not provided, ask the user for it and stop.
2. Establish the rubric before reading deeply:
   - Pull the venue's review criteria from `$ARGUMENTS` (e.g., a named conference/journal or a guideline the user pasted). If none is given, use the five recurring axes below.
   - Infer the **paper type** (measurement / attack / defense / benchmark / systematization (SoK) / systems / theory) and load its checklist from `templates/paper/<type>.md` if present; otherwise reason about the type-specific bar (e.g., benchmark papers need transparent construction, annotator agreement, baselines, and a maintenance plan).
3. Read the paper in two passes: a skim to recover its claimed research question and contributions, then a deep read to test whether the evidence supports them.
4. Score every paper along the **five axes** and gather specific evidence for each: problem motivation, technical contribution, evaluation rigor, related work, presentation. For each axis, note at least one concrete strength and any concrete weakness with a pointer (section/figure/table/equation).
5. Build a claim-evidence check: list the paper's headline claims and, for each, whether the experiments/proofs actually support it at the claimed scope. Flag overclaims (a general capability inferred from a narrow proxy, "solves" where it only reduces) with the exact location.
6. Audit rigor and integrity: fair and tuned baselines, reported variance (error bars / CIs / significance), explained anomalies, no train/test leakage, validated automatic/LLM judges, accurate and fairly characterized citations, released artifacts or a justified absence, and present limitations/ethics sections.
7. **Be fair, not heuristic.** Do NOT raise criticisms that could apply to any paper ("great at A, but what about B?"), and explicitly avoid the unfair reflexes: "obvious in hindsight", "too simple", "too narrow", "doesn't beat SOTA", "I'd have done it differently". If you cite one of these, justify why it is load-bearing here or drop it.
8. **Specificity rule.** Every weakness must be of the form `<X> is <weak/unclear/unsupported> because <concrete cause> (location); it could be addressed by <concrete change>.` Replace any vague verdict with this shape. Separate fatal flaws (invalidate a core claim) from fixable issues from minor/presentation nits.
9. Write the review from `templates/review-template.md` into the structured sections: summary (neutral restatement the authors would accept), strengths, weaknesses (ordered by severity), detailed comments (per-section), questions for the authors (answerable in a rebuttal), and a score with a rationale that ties the number to the axes above.

## Validate against a short checklist
- The summary is neutral and accurate; authors would agree it describes their paper.
- Every weakness is specific, located, and paired with an actionable fix; none could apply to any paper.
- Strengths are concrete, not boilerplate; the review is not one-sided.
- The unfair-heuristic reflexes (obvious/simple/narrow/no-SOTA/personal-preference) are absent or justified.
- Fatal flaws are separated from fixable issues and minor nits.
- Questions are answerable in a rebuttal and target the decision, not trivia.
- The score rationale traces to the five axes and the claim-evidence check, not to a gut feeling.
- Tone is professional and constructive; no personal or identifying remarks about the authors.

## Completion
Write `./.research/review/<short-id>.md` (start from `templates/review-template.md` if it exists), creating `./.research/review/` as needed and never overwriting an existing review silently. Report the path and end with: `Next: /research.rebuttal (to flip sides and stress-test your own paper)`.
