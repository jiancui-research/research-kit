---
description: Cross-artifact consistency + review-readiness audit AND the sync checker across the design/eval/paper lanes. Read-only; outputs a prioritized gap report to .research/analyze-report.md.
argument-hint: optional focus (e.g. sync, claims, related-work, overclaims) — omit for a full audit
---

## User input

The user request arrives via the `$ARGUMENTS` placeholder. It may narrow the audit to one axis (e.g. `sync`, `claims`, `evaluation`, `related-work`, `overclaims`, `desk-reject`) or be empty for a full pass. Use `sync` for a fast "what drifted and what do I re-run" check during active work.

## What this phase is

Two jobs in one command, both **read-only**:

1. **Sync checker (run anytime).** The three lanes — `design` (`tasks/design.md` + the code in `./design/`), `eval` (`claims.md` + `./eval/`), and `paper` (the manuscript root from `.research/paper-repo`, fallback `./paper/`) — drift apart whenever you change one without the others. This command detects that drift and tells you **exactly which lane is stale and which command to re-run** (e.g. "design changed → re-run `/research.eval 03` and `/research.paper system-design`"). It never edits another lane to "fix" the drift; each owning command re-runs and updates its own artifact.
2. **Review-readiness audit (near submission).** Read the project the way a skeptical reviewer will and surface gaps before submission.

It inspects `proposal.md`, `feasibility.md`, `tasks/design.md`, `tasks/eval.md`, `tasks/paper.md`, `claims.md`, `eval/`, `related-work.md`, and `paper/`, but the **only** file it writes is `./.research/analyze-report.md`. Never edit a claim, eval, design, or section to make the audit pass; report the gap and route it to the command that owns the fix.

## Steps

1. **Read everything (read-only).**
   - Read `./.research/memory/constitution.md` if present (for venue, paper-type, voice); skip silently if absent.
   - Read all artifacts that exist: `./.research/proposal.md`, `./.research/feasibility.md`, `./.research/tasks/design.md`, `./.research/tasks/eval.md`, `./.research/tasks/paper.md`, `./.research/claims.md`, `./eval/` (files + `index.md`), `./.research/related-work.md`, and the manuscript. For a build-paper, also note the `./design/` folder (the built code lives there). For any missing artifact, note it as a gap rather than failing.
   - Determine the paper type (measurement / attack / defense / benchmark / systematization (SoK)) from `proposal.md` so type-specific checks apply.
   - If `feasibility.md` exists, confirm it reached a **GO** verdict; flag a `NO-GO`/`PIVOT` that was never resolved.

2. **Contribution → evidence trace.** For each contribution and research question in `proposal.md`, find the supporting claim(s) in `claims.md` and the eval(s) backing those claims. Flag any contribution with **no supporting claim**, or any claim whose verdict in `claims.md` is `pending` / `partial` / `refuted` while the paper states it as settled.

3. **Claim ↔ result consistency.** For each claim, check that its verdict matches the actual eval results in `eval/` and that the paper text (the manuscript root from `./.research/paper-repo`, fallback `./paper/`) states it no stronger than the evidence allows. Flag mismatches in both directions: paper overclaims a `partial`/`refuted` result, or paper under-sells a fully `supported` one.

4. **Overclaim audit.** Scan the abstract and intro verbs (`enables`, `solves`, `guarantees`, `proves`, `demonstrates`, `first`). For each, ask whether the evidence is as strong as the verb and whether the scope qualifier is present. Flag any verb that outruns its data, and any bare `first`/novelty claim missing a qualifier.

5. **Cross-artifact agreement.** Check that `proposal.md`, `tasks/design.md`, `tasks/eval.md`, `tasks/paper.md`, and the manuscript tell the same story: same problem framing, same contributions, same baselines/datasets/metrics, same threat model. Flag drift (e.g. a metric in the paper that never appears in `tasks/eval.md`, a baseline planned but never tested, a contribution in the intro absent from `proposal.md`).

6. **Lane sync (design ↔ eval ↔ paper).** This is the staleness check. For build-papers, verify the three lanes still agree on the *same system*:
   - **design → eval**: every component / interface in `tasks/design.md` that an eval depends on still exists as built; flag evals that test a since-changed or removed part of the design.
   - **design → paper**: the System Design / Implementation section in the manuscript describes the architecture currently in `tasks/design.md`, not an old one.
   - **eval → paper**: result sections match the current `claims.md` verdicts.
   For each drift, name the **stale lane** and the **exact command to re-run** (e.g. "design changed component X → re-run `/research.eval 03` (tests X), then `/research.paper system-design`"). Do not edit the stale lane yourself; the re-run is how it re-syncs. (Skip this step for measurement / SoK papers, which have no design lane.)

7. **Reviewer-objection pre-emption.** Walk the five recurring review axes — **motivation, contribution, evaluation, related work, presentation** — and for each, write the single most specific, justified objection a reviewer could raise, then note whether the current artifacts already answer it. Also surface the common unfair-but-likely reactions (`obvious`, `too simple`, `too narrow`, `no SOTA win`) and whether the framing defuses each. Check evaluation rigor explicitly: fairly tuned baselines, variance reported, anomalies explained, no train/test leakage, and any automated/LLM judge validated against ground truth on this task.

8. **Desk-reject gate (binary).** Check the mechanical, fatal items: scope fit, length/format compliance, anonymization (no self-deanonymizing links or phrasing), required sections present (limitations, ethics/disclosure), and an honest reproducibility/artifact statement (code/data/proof released or its absence justified, with hyperparameters/prompts/seeds/hardware). Any failure here is top priority.

9. **Related-work positioning.** Confirm each closest prior work has an explicit delta (how this work differs and why a new approach was needed), and that no citation is unsupported, mischaracterized, or marked `[cite?]`/unresolved.

## Write the report

Write **only** `./.research/analyze-report.md`, overwriting the prior report. Structure it as prioritized, actionable gaps — not prose:

- **Summary line**: counts by severity, plus a one-line sync status (in sync / N stale lanes).
- **Out-of-sync lanes** (list first — this is the sync output): one row per drift as `stale lane | what changed upstream | exact re-run command`. Empty when the lanes agree.
- **Critical** (desk-reject or invalidates a core claim) → **Major** (overclaim, unsupported contribution, missing variance) → **Minor** (presentation, polish).
- Each gap: one line stating the gap, the artifact + location, and the single command to fix it (e.g. "rescope in `/research.paper intro`", "add eval via `/research.eval`", "tighten delta in `/research.relatedwork`").
- A short **claim-evidence ledger** table: `contribution | claim id | eval id | verdict | scope OK? (Y/N)`.
- A **rebuttal-readiness** note: the top 3–5 likely decision-driving concerns, each with a one-line evidence-backed response stub, prioritized.

## Validate (short checklist)

- Every contribution traced to a claim and an eval, or flagged.
- For build-papers, the design/eval/paper lanes were checked for drift and every stale lane names the exact re-run command.
- Every flagged gap names a location and a concrete next command.
- Gaps are specific ("X unsupported because Y"), never vague ("evaluation is weak").
- Report is sorted by severity; desk-reject failures are surfaced first.
- No other artifact was modified.

## Completion

Report the path `./.research/analyze-report.md`, the sync status (in sync / which lanes are stale), and the count of critical/major gaps. Then: route each gap and each stale lane to the command that owns the fix (most often `/research.design`, `/research.eval`, or `/research.paper`), and once routed, `Next: /research.review`. This command is read-only and safe to run **anytime** — use it as a quick `sync` check whenever you change one lane, not just near submission.
