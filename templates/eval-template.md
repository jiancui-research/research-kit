# Eval [NN-slug]: [short name of what this run tests]

> Produced by `/research.eval`. Lives at `./eval/NN-slug.md`.
> One file per eval. The index is `./eval/index.md`.
> Fill every bracket. An eval that does not test a stated claim is not yet an eval.

## ID
[Stable identifier, e.g. `01`. Never reused. Referenced from `claims.md` and the index.]

## Hypothesis (falsifiable, decided before running)
[One declarative prediction with a direction and a threshold, written BEFORE you look
at results. Use the scaffold:
"<Mechanism / condition A> yields <metric M> <direction, e.g. higher / lower> than
<baseline B>, by at least <effect size>, under <condition Z>."
If you cannot state what result would prove you WRONG, it is not a hypothesis yet.]

## Linked claim / contribution
[Which row of `claims.md` and which contribution (C1, C2, ...) this run supports.
A result here flows back to exactly that claim. If it maps to no claim, either add
the claim or drop the eval - do not run orphan evals.]
- Claim: [verbatim claim from `claims.md`]
- Contribution: [C# from `proposal.md`]
- RQ: [RQ# this answers, if any]

## Setup
[The fixed environment that makes this reproducible from this file alone:
- Models / systems and exact versions or commits.
- Hyperparameters, prompts (or path to them), seeds.
- Hardware, runtime, and any non-default config.
List enough that someone else could re-run it without asking you.]

## Data
[What this runs over: dataset / corpus / trace, version, size, and the exact split.
State source and license. Call out any filtering or sampling. Guard against leakage:
confirm the test data was never seen in tuning or selection.]

## Metric
[The primary metric that decides the hypothesis, defined precisely (units, how
computed, higher-or-lower-is-better). List secondary metrics separately. If a metric
relies on an automatic or LLM judge, note how it is validated against ground truth
for THIS task - an unvalidated judge score decides nothing.]
- Primary: [metric, definition, direction]
- Secondary: [...]
- Variance: [how spread is reported - repeats, error bars, CIs, significance test]

## Baselines
[What the treatment is compared against. Always include the unmodified default
(do-nothing) and a fairly tuned state of the art. State how each baseline was tuned -
an obviously weak baseline reads as cherry-picking.]
- B0: [unmodified default]
- B1: [state of the art, tuned how]

## Procedure
[The ordered steps to produce the result: prepare -> run -> collect -> aggregate.
Number the repeats (N runs / seeds). Name the command or script. Anyone following
these steps must land on the same numbers.]
1. [step]
2. [step]
3. [step]

## Expected result
[What the hypothesis predicts you will see, as a concrete number or direction with
its variance, before running. This is the line you commit to in advance.]

## Actual result
[What you observed: the primary metric with variance, plus secondary metrics. Report
the real numbers, including the inconvenient ones. Anomalies and surprises get an
explanation here, not silence. Link the figure / table / raw output.]
- Primary: [value +/- variance]
- Secondary: [...]
- Artifact: [path to logs / figure / table]

## Status
[One of: planned | running | done | blocked | abandoned.
If blocked or abandoned, say why in one line so the index stays honest.]

## Takeaway
[One sentence on what this means for the linked claim:
- supported: hypothesis held; the claim may stand as scoped.
- refuted: hypothesis failed; rescope or drop the claim, do not bury the result.
- inconclusive: variance too high / confound found; name the next step.
Then state how the claim's wording in `claims.md` should change, if at all.]

## Quality checklist
- [ ] The hypothesis was written before the run and names a result that would refute it.
- [ ] This eval maps to a specific claim and contribution, not a vague theme.
- [ ] Setup, data, and procedure are complete enough to reproduce from this file alone.
- [ ] The primary metric is defined precisely and decides the hypothesis on its own.
- [ ] Any automatic / LLM judge is validated against ground truth for this task.
- [ ] Baselines include the unmodified default and a fairly tuned state of the art.
- [ ] No train / test or selection leakage; the test split was untouched during tuning.
- [ ] Variance is reported (repeats / error bars / CIs / significance), not a single number.
- [ ] Actual result records the inconvenient numbers and explains every anomaly.
- [ ] The takeaway updates `claims.md` honestly - refuted claims get rescoped, not hidden.

---
Next: `/research.eval` (next eval) or `/research.analyze` when the batch is done.
