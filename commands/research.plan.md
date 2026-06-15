---
description: Produce a paper-type-aware research and experiment plan (methodology, baselines, datasets, metrics, threat model, evaluation design) into .research/plan.md.
argument-hint: optional notes (e.g. "ML attack at a security venue, focus on transferability")
---

## User input

The user request arrives via the $ARGUMENTS placeholder. Treat it as steering notes (venue, emphasis, constraints), not the whole plan.

## Steps

1. **Read context.**
   - Read `./.research/memory/constitution.md` if it exists (skip silently otherwise) and honor its principles and writing voice.
   - Read `./.research/idea.md` (required upstream). If it is missing, stop and tell the user to run `/research.idea` first.
   - From `idea.md`, extract: paper type (measurement / attack / defense / benchmark / systematization (SoK)), target venue, the gap, the contributions, and the research questions.

2. **Load the skeleton.** Start from `.research/templates/plan-template.md`, then layer in the matching `.research/templates/paper/<type>.md` so the plan inherits that type's proof obligation:
   - measurement -> defensible dataset + methodology + a surprising finding
   - attack -> a working exploit + evidence it is not a corner case
   - defense -> a mechanism that stops the threat + a quantified cost
   - benchmark -> concrete task tuple + dataset + metrics + 3-5 baselines
   - systematization (SoK) -> a novel, MECE-ish taxonomy + lessons found in no single prior paper

3. **Draft the plan**, paper-type aware. Cover the sections below; keep each tight and specific (numbers, named artifacts, exact criteria over adjectives).
   - **Methodology / approach.** The core method or attack/defense design or construction pipeline. Show the smallest concrete instance (a worked example, a 3-line POC) before the full machinery.
   - **Baselines.** 3-5 representative comparison points on a sensible axis (open vs closed, prior SOTA, ablations). Note how each will be tuned fairly. For measurement, baselines may be detection methods or ground-truth references instead.
   - **Datasets / data sources.** Concrete sizes, dates, provenance, and the construction or selection filters (informativeness, validation, deduplication, leakage/contamination check). State known coverage, selection, or survivorship bias.
   - **Metrics.** One operational, one-sentence definition per metric, tied to a claim. Define what counts as a true positive, partial match, and failure. Plan to report variance (error bars / CIs / significance) and, if using an automated or LLM judge, how you will validate it against ground truth on this task.
   - **Threat model (attack and most defense papers).** Standalone and explicit for security venues; inline/informal for AI venues. Use a fixed beat: adversary goal, adversary knowledge (black-box vs white-box), and an explicit out-of-scope sentence. Skip or minimize for measurement and benchmark unless the venue expects it.
   - **Evaluation design.** The experiments themselves: what each one varies, the conditions and ablations, and whether it argues severity (how bad) or coverage (where it applies). Plan to organize results by claim / research question, each with a one-line takeaway.
   - **Claim-to-experiment map.** A table mapping each contribution and research question from `idea.md` to the specific experiment(s) that will substantiate it. Every contribution must have at least one experiment; every planned experiment must serve a claim. Flag any contribution with no supporting experiment.
   - **Ethics, disclosure, and artifact.** Note responsible-disclosure plans (attack/measurement), IRB/consent and redaction (human or sensitive data), and what artifact will be released. These are effectively mandatory at top security venues.

4. **Validate** against this short checklist before writing:
   - The plan's proof obligation matches the paper type from `idea.md`.
   - Every contribution / research question maps to at least one experiment.
   - Baselines, datasets, and metrics are concrete (named, sized, operationally defined), not placeholders.
   - Threat model is present and venue-appropriate for attack/defense papers, with an out-of-scope line.
   - Evaluation plans for variance, fair baseline tuning, and (if applicable) judge validation and leakage/contamination checks.

5. **Write** the result to `./.research/plan.md` (`mkdir -p ./.research` first). Do not overwrite existing user content silently: if `plan.md` already exists, preserve their text and clearly mark what you changed.

## Completion

Report the path `./.research/plan.md` and end with: `Next: /research.experiment`.
