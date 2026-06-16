---
description: Draft a prioritized, evidence-backed rebuttal to reviewer comments into .research/rebuttal/, fitted to the venue word limit.
argument-hint: paste the reviews, or pass a path to a file with them (e.g. "reviews.txt, 600-word limit, one reviewer is borderline-positive")
---

## User input

The user request arrives via the $ARGUMENTS placeholder. It holds the reviewer comments (pasted inline or as a file path to read) plus any steering notes: word/character limit, which reviewer is the champion, the meta-review, scores, and the venue's rebuttal rules. If a file path is given, read it. If no reviews are found, stop and ask for them.

## What this phase is

This is the response phase. You turn raw reviews into a tight, prioritized rebuttal that answers first and justifies second, backs every claim with evidence, and fits the word limit. You do not edit the paper here; you commit to specific, deliverable revisions.

## Steps

1. **Read context.**
   - Read `./.research/memory/constitution.md` if it exists (skip silently otherwise) and honor its voice.
   - Read `./.research/proposal.md`, `./.research/tasks/experiment.md`, and `./.research/claims.md` if present, so pointers to sections, tables, and existing evidence are accurate.
   - Parse the reviews from `$ARGUMENTS` (inline or file). Capture each reviewer's id, score/recommendation, and concerns. Note the meta-review/AC items and which reviewer is the champion (most supportive) if identifiable.

2. **Itemize before drafting.** Build a concern grid: one row per distinct concern, columns for which reviewer(s) raised it, severity, and whether evidence already exists in the paper or must be gathered. Merge duplicates across reviewers into one row.

3. **Decide rebut-or-not** and say so in one line. Mixed/borderline: always rebut. Uniformly very low: usually skip (note if the text is still worth reusing for the next venue). Very high: write a short rebuttal anyway, since silence has sunk strong papers.

4. **Prioritize.** Order responses by: meta-reviewer/AC call-outs first, then concerns raised by multiple reviewers, then swayable borderline reviewers, then minor points. Lead with the most damaging concern, not the easiest. Spend disproportionate effort arming the champion with arguments for the committee meeting; in a split, actively re-energize the positive reviewer rather than only fighting the detractors.

5. **Draft the rebuttal** from `.research/templates/rebuttal-template.md`. Group responses by theme with inline reviewer tags in each header (e.g. `**Evaluation scope (R1, R3, AC)**`). For each point:
   - **Answer first**, then justify. Open with the direct factual answer or correction, then a short `First / Second / Further` argument. No buried answers; keep any courtesy opener to one brief line so the budget goes to substance.
   - **Carry evidence for every claim.** For points already in the paper, add a precise pointer (section, figure, table, appendix). For new points, cite a reference or report a result.
   - **Demonstrate over promise.** Where the window allows, run the experiment and report the actual number rather than promising to add it.
   - **Be specific.** Quote the exact statistic, the exact revised paragraph text, the exact section that will change.
   - **Reframe scope instead of conceding** where fair: bound what the contribution claims rather than flatly admitting a weakness. When a limitation is genuine, concede it gracefully as out-of-scope or future work, briefly.
   - For unbounded "what if the attacker does X?" questions, frame X as a general challenge for this class of systems and give its bounded impact on the metric/guarantee, not a shallow yes/no.

6. **Commit to bounded revisions.** State specific, deliverable promises (which section, which table, which discussion). Quote the exact proposed new sentence(s) where it shows the change is small and contained. Only promise what you can actually deliver in camera-ready.

7. **Reference pack.** End with a compact numbered list `[R1]...[Rn]` giving full sources for every non-obvious external claim, including industry/web sources, not only papers.

8. **Final pass.** Trim hard to the word/character limit. Keep tone polite, never defensive or snarky. Run the neutral-third-party test: each concern should be resolvable from the rebuttal alone.

## Validate (short checklist)

- Rebut-or-not decided explicitly (even high scores get a short rebuttal).
- All concerns itemized in the grid; duplicates merged; champion's concerns fully addressed.
- Priority order followed: meta-reviewer > multi-reviewer > swayable borderline > minor; most damaging point led with.
- Every response answers first, then justifies; no obsequious opener.
- Every claim has evidence: a paper pointer for existing points, a reference or fresh result for new ones.
- Specific numbers and exact revised text given where asked; new experiments run in-window where feasible.
- Every commitment is one you can actually deliver in camera-ready.
- Tone polite; neutral-third-party test passes; trimmed to the word limit.

## Completion

Write the result to `./.research/rebuttal/rebuttal.md` (`mkdir -p ./.research/rebuttal` first). Do not overwrite existing user content silently. Report the path and end with: `Next: revise the paper per your revision commitments, then /research.paper`.
