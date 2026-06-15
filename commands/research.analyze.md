---
description: Cross-artifact consistency + review-readiness audit. Read-only; outputs a prioritized gap report to .research/analyze-report.md.
argument-hint: optional focus (e.g. claims, related-work, overclaims) — omit for a full audit
---

## User input

The user request arrives via the `$ARGUMENTS` placeholder. It may narrow the audit to one axis (e.g. `claims`, `evaluation`, `related-work`, `overclaims`, `desk-reject`) or be empty for a full pass.

## What this phase is

This is the self-review phase: read the project the way a skeptical reviewer will and surface gaps **before** submission. It is **read-only** on every other artifact — it inspects `idea.md`, `plan.md`, `claims.md`, `experiments/`, `related-work.md`, and `paper/`, but the **only** file it writes is `./.research/analyze-report.md`. Never edit a claim, experiment, or section to make the audit pass; report the gap and let the upstream command fix it.

## Steps

1. **Read everything (read-only).**
   - Read `./.research/memory/constitution.md` if present (for venue, paper-type, voice); skip silently if absent.
   - Read all artifacts that exist: `./.research/idea.md`, `./.research/plan.md`, `./.research/claims.md`, `./.research/experiments/` (files + `index.md`), `./.research/related-work.md`, and `./.research/paper/`. For any missing artifact, note it as a gap rather than failing.
   - Determine the paper type (measurement / attack / defense / benchmark) from `idea.md` so type-specific checks apply.

2. **Contribution → evidence trace.** For each contribution and research question in `idea.md`, find the supporting claim(s) in `claims.md` and the experiment(s) backing those claims. Flag any contribution with **no supporting claim**, or any claim whose verdict in `claims.md` is `pending` / `partial` / `refuted` while the paper states it as settled.

3. **Claim ↔ result consistency.** For each claim, check that its verdict matches the actual experiment results in `experiments/` and that the paper text (`paper/`) states it no stronger than the evidence allows. Flag mismatches in both directions: paper overclaims a `partial`/`refuted` result, or paper under-sells a fully `supported` one.

4. **Overclaim audit.** Scan the abstract and intro verbs (`enables`, `solves`, `guarantees`, `proves`, `demonstrates`, `first`). For each, ask whether the evidence is as strong as the verb and whether the scope qualifier is present. Flag any verb that outruns its data, and any bare `first`/novelty claim missing a qualifier.

5. **Cross-artifact agreement.** Check that `idea.md`, `plan.md`, and `paper/` tell the same story: same problem framing, same contributions, same baselines/datasets/metrics, same threat model. Flag drift (e.g. a metric in the paper that never appears in the plan, a baseline planned but never tested, a contribution in the intro absent from `idea.md`).

6. **Reviewer-objection pre-emption.** Walk the five recurring review axes — **motivation, contribution, evaluation, related work, presentation** — and for each, write the single most specific, justified objection a reviewer could raise, then note whether the current artifacts already answer it. Also surface the common unfair-but-likely reactions (`obvious`, `too simple`, `too narrow`, `no SOTA win`) and whether the framing defuses each. Check evaluation rigor explicitly: fairly tuned baselines, variance reported, anomalies explained, no train/test leakage, and any automated/LLM judge validated against ground truth on this task.

7. **Desk-reject gate (binary).** Check the mechanical, fatal items: scope fit, length/format compliance, anonymization (no self-deanonymizing links or phrasing), required sections present (limitations, ethics/disclosure), and an honest reproducibility/artifact statement (code/data/proof released or its absence justified, with hyperparameters/prompts/seeds/hardware). Any failure here is top priority.

8. **Related-work positioning.** Confirm each closest prior work has an explicit delta (how this work differs and why a new approach was needed), and that no citation is unsupported, mischaracterized, or marked `[cite?]`/unresolved.

## Write the report

Write **only** `./.research/analyze-report.md`, overwriting the prior report. Structure it as prioritized, actionable gaps — not prose:

- **Summary line**: counts by severity.
- **Critical** (desk-reject or invalidates a core claim) → **Major** (overclaim, unsupported contribution, missing variance) → **Minor** (presentation, polish).
- Each gap: one line stating the gap, the artifact + location, and the single command to fix it (e.g. "rescope in `/research.paper intro`", "add experiment via `/research.experiment`", "tighten delta in `/research.relatedwork`").
- A short **claim-evidence ledger** table: `contribution | claim id | experiment id | verdict | scope OK? (Y/N)`.
- A **rebuttal-readiness** note: the top 3–5 likely decision-driving concerns, each with a one-line evidence-backed response stub, prioritized.

## Validate (short checklist)

- Every contribution traced to a claim and an experiment, or flagged.
- Every flagged gap names a location and a concrete next command.
- Gaps are specific ("X unsupported because Y"), never vague ("evaluation is weak").
- Report is sorted by severity; desk-reject failures are surfaced first.
- No other artifact was modified.

## Completion

Report the path `./.research/analyze-report.md` and the count of critical/major gaps. Then: resolve the gaps via the named commands (most often `Next: /research.paper` or `/research.experiment`), and rerun `/research.analyze` until the report is clean.
