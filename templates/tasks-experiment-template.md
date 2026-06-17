# Experiment (evaluation) plan & task list: [project / paper short name]

> Produced by `/research.tasks`. Lives at `./.research/tasks/experiment.md`.
> This is the **evaluation** plan. Two parts: a PLAN-KEEP experiment-design header (the
> preserved plan content), then an ordered experiment task list. Keep the header tight and
> specific - numbers and named artifacts over adjectives. Layer in
> `.research/templates/paper/<type>.md` so this discharges the paper type's proof
> obligation.
>
> **Building the system is NOT here.** For build-papers the architecture, repo layout, and
> build tasks live in `tasks/design.md` (implemented by `/research.design`); this file only
> evaluates what was built. Only measurement / SoK papers (no design lane) keep a light
> data-obtain task here.

## PLAN-KEEP: experiment-design header

Fill every dimension below; drop one only with a one-line reason. This is the content
the old plan stage produced - the single source of truth for it now lives here.

- **Methodology / approach.** How the evaluation works - the experimental method and what
  is varied. For a build-paper the system's architecture lives in `tasks/design.md`;
  reference it here, do not re-describe it. Show the smallest concrete instance first - a
  worked example or a 3-line proof-of-concept - before the full machinery.
- **Baselines.** 3-5 representative comparison points (the unmodified default /
  do-nothing AND a fairly tuned state of the art). Note how each is tuned so a reviewer
  cannot call it a strawman. For measurement, baselines may be detection methods or
  ground-truth references.
- **Datasets / data sources.** Concrete sizes, dates, provenance, and the construction /
  selection filters (informativeness, validation, deduplication, leakage / contamination
  check). State known coverage, selection, or survivorship bias openly.
- **Metrics.** One operational, one-sentence definition per metric, each tied to a claim
  id. Define true positive, partial match, and failure. Plan to report variance (error
  bars / CIs / significance); if using an automatic or LLM judge, plan how you will
  validate it against ground truth on this task.
- **Threat model** (attack and most defense papers). Standalone and explicit for security
  venues, inline for AI venues. Fixed beat: adversary goal, adversary knowledge
  (black-box vs white-box), and an explicit out-of-scope sentence. Skip or minimize for
  measurement / benchmark unless the venue expects it.
- **Evaluation design.** What each experiment varies, its conditions and ablations, and
  whether it argues severity (how bad) or coverage (where it applies). Defense gets a
  two-sided design (stops the threat + cost); attack gets severity vs coverage.
- **Ethics, disclosure, and artifact.** Responsible-disclosure plan (attack /
  measurement), IRB / consent / redaction (human or sensitive data), and what artifact
  will be released. Effectively mandatory at top security venues.

## Task list (experiments)

One task per experiment, sequenced so the experiment that would kill the paper if it fails
runs first. Each is tied to exactly one primary claim id (`-> C2`) and names dataset,
baselines, metric, and the predicted result / falsifier. Every contribution's claim id must
appear on at least one experiment task; every experiment task must serve a claim. Flag any
contribution with no experiment as an **overclaim to rescope** and any experiment serving no
claim as **scope creep**.

- [ ] [Experiment] over [dataset] vs [baselines] on [metric]; predicts [result / falsifier]. -> C#
- [ ] ...

> **Measurement / SoK only** (no design lane): add light data-obtain tasks here, e.g.
> `- [ ] Construct [dataset] - done when [criterion].` Build-papers keep all construction in
> `tasks/design.md`.

---
Next: `/research.experiment` (run experiments, fill `claims.md`). The system under
evaluation is built by `/research.design`.
