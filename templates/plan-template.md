# Plan: [short working title]

> Produced by `/research.plan`. Lives at `./.research/plan.md`.
> Reads `./.research/idea.md` (and `related-work.md` if present). The plan turns the
> idea's RQs and contributions into a concrete, runnable methodology.
> Fill every bracket. An empty slot means the experiment is not yet specified.
> Paper type from `idea.md` ([measurement | attack | defense | benchmark]) decides
> emphasis and which optional sections matter - consult `templates/paper/<type>.md`
> for the section skeleton this plan feeds into.

## Paper type and what it demands
- Type: [measurement | attack | defense | benchmark]
- Load-bearing proof obligation for this type (the thing this plan must discharge):
  [measurement -> defensible dataset + method + a surprising finding;
   attack -> a working exploit + evidence it is not a corner case;
   defense -> a mechanism that stops the threat + a quantified cost;
   benchmark -> concrete task + dataset + metric + baselines.]
- If any part of that obligation is hand-waved below, the paper is rejectable. Name it now.

## Methodology
[The procedure that produces your results, in enough detail that a peer could re-run it.
State the core approach in 2-4 sentences, then the steps. Name the mechanism, not "we use ML".
Show the smallest concrete instance (a worked example / minimal POC) before the full pipeline.]
- Approach: [...]
- Steps / pipeline: [step 1 -> step 2 -> ...]
- Key design decisions and why: [decision -> reason; each should trace to an RQ or a constraint]
- Implementation: [language / framework / hardware / where the artifact will live]

## System / threat model (if applicable)
[Required for attack and property-defense work at security venues; fold informally into
the intro at AI venues; skip for pure measurement unless an adversary is central.]
- Adversary goal: [what the attacker wants to achieve]
- Adversary knowledge / access: [black-box | white-box]; [interface and capabilities assumed]
- Trust boundaries / assumptions: [what is trusted, what is not]
- Out of scope (explicit): [capabilities or settings you deliberately exclude - one sentence]
- (Deployed-system defense only) Backward-compatibility / non-disruption clause: [...]

## Datasets
[Where credibility is earned. Be concrete: a vague dataset is a rejection.]
- Source(s): [names, sizes, dates, how obtained]
- Construction / quality gates: [what is excluded, deduplicated, validated, and why]
- Ground truth: [how labels are produced; inter-annotator agreement or validation against known labels]
- Bias and coverage: [selection / survivorship / coverage limits stated openly]
- Leakage / contamination check: [how you ensure no overlap with model training data or test reuse]
- Ethics / access: [IRB or equivalent, consent, license, redaction - see Risks below]

## Baselines
[Must include the unmodified default (do-nothing) AND a fair state of the art.
For benchmarks, 3-5 baselines spanning a sensible axis: open vs closed, small vs large, general vs domain.]
- B0 (default / no-op): [...]
- B1 (state of the art): [...]
- B2..Bn: [...]
- Fair-tuning note: [how each baseline is tuned so a reviewer cannot call it a strawman]

## Metrics
[One operational definition per metric: what is measured and what counts as success.
Pair every aggregate with a concrete anchor when reported (absolute count beside the percentage).]
- M1: [name] = [one-sentence operational definition]; success / direction: [...]
- M2: [...]
- Variance reporting: [error bars / CIs / significance tests - plan this in, not after]
- (If using an automatic / LLM judge) Validation: [how you show it correlates with human/ground-truth on this task]

## Experimental design (RQ -> experiment mapping)
[Every RQ from `idea.md` maps to at least one experiment; every experiment answers a claim.
Each row should be runnable as written. One file per experiment will live under
`./.research/experiments/`.]

| RQ | Experiment | Dataset(s) | Baselines | Metric(s) | Predicted result / falsifier |
|----|-----------|------------|-----------|-----------|------------------------------|
| RQ1 | E1: [...] | [...] | [...] | [...] | [direction; wrong if <observable>] |
| RQ2 | E2: [...] | [...] | [...] | [...] | [...] |
| RQ3 | E3: [...] | [...] | [...] | [...] | [...] |

- Ablations / sensitivity: [which design choices you will turn off to isolate their effect]
- (Defense) Two-sided evaluation: [security experiment - does it stop the threat | performance experiment - what it costs]
- (Attack) Severity vs coverage: [how-bad experiment | where-it-applies experiment]
- (Benchmark) Case studies: [one success, one informative failure, one striking discovery]

## Risks
[What could make the plan fail or the result not transfer, and the mitigation for each.]
- Technical risk: [what might not work] -> mitigation / fallback: [...]
- Validity threat (internal): [confound] -> control: [...]
- Validity threat (external): [setting / population you did not cover] -> stated as a limitation
- Ethics / disclosure risk: [harm, dual-use, sample handling] -> who is notified, how, and when
- Negative-result plan: [if the headline prediction fails, is the negative finding itself a contribution?]

## Rough sequencing
[Order the experiments by dependency and by what is decision-driving. Front-load the
experiment that, if it fails, kills the paper - learn that first.]
1. [pilot / smallest end-to-end slice that validates the pipeline]
2. [core experiment that tests the headline claim]
3. [coverage / ablation / cost experiments]
4. [hardening: variance, robustness checks, artifact packaging]

## Quality checklist
- [ ] The plan discharges this paper type's proof obligation; nothing load-bearing is hand-waved.
- [ ] Every RQ in `idea.md` appears in the mapping table with a runnable experiment.
- [ ] Each experiment names dataset, baselines, metrics, and a falsifier.
- [ ] Baselines include the unmodified default and a fairly tuned state of the art.
- [ ] Each metric has a one-sentence operational definition and a variance-reporting plan.
- [ ] Datasets state sizes/dates/sources, ground-truth quality, bias, and a leakage check.
- [ ] Threat model is present (and venue-appropriate) if the work is attack/defense.
- [ ] Any automatic / LLM-judge metric has a validation step against human/ground truth.
- [ ] Risks name a mitigation; external-validity gaps are routed to limitations, not hidden.
- [ ] Sequencing front-loads the experiment that would kill the paper if it fails.

---
Next: `/research.experiment`
