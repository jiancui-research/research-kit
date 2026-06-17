# Claim <-> evidence matrix

One row per claim or contribution you make in the abstract and introduction. Every
row must trace to concrete evidence (an eval, figure, table, or proof). A row
without tight support is an overclaim: rescope the claim or add the evidence.

| Claim / Contribution | Supporting eval(s) | Result | Status | Where in paper |
| --- | --- | --- | --- | --- |
| _Claim 1: copy the claim verbatim from the abstract/intro, e.g. "Method X improves Y over the strongest baseline."_ | `eval/01-...` | Replace with the exact number or outcome, e.g. "+8.3 pts vs. best baseline (n=5, 95% CI)" | `pending` | TBD |
| _Claim 2: e.g. "We release a reusable benchmark of N tasks."_ | artifact / `eval/index.md` | e.g. "N tasks, K annotators, IAA=0.81" | `pending` | TBD |

## How to use

- Maintain this file across the pipeline: `/research.eval` adds and updates
  rows as evidence lands; `/research.analyze` audits the whole matrix before drafting.
- Fill columns precisely:
  - **Claim / Contribution** - the claim exactly as it appears (or will appear) in the
    paper. Match the wording so scope mismatches are visible.
  - **Supporting eval(s)** - point to the specific `eval/<id>.md` file(s),
    figure, table, or proof. "General intuition" is not evidence.
  - **Result** - the concrete outcome: the number, delta, or pass/fail, with variance
    (error bars / CI / significance) where applicable. No round-number hand-waving.
  - **Status** - one of `pending` / `partial` / `supported` / `refuted`. Use
    `pending` until evidence lands and `refuted` when the eval contradicts the
    claim. A claim is `supported` only when the evidence backs it with no
    extrapolation. This is the same vocabulary `/research.eval` and
    `/research.analyze` use, so verdicts stay consistent across the pipeline.
  - **Where in paper** - the section/figure/table where the claim and its evidence
    appear, so a reader (and a reviewer) can verify in one hop.
- Scope check each row: does the evidence support the claim with NO extrapolation?
  If a verb in the claim ("solves", "guarantees", "enables", "proves") outruns the
  result, downgrade the verb or run the missing eval.
- Any row left `pending`, `partial`, or `refuted` at draft time is either cut,
  rescoped, or flagged in the limitations section - never quietly shipped.
