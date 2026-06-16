# Experiment plan & task list: [project / paper short name]

> Produced by `/research.tasks`. Lives at `./.research/tasks/experiment.md`.
> Two parts: a PLAN-KEEP experiment-design header (the preserved plan content), then
> an ordered task list. Keep the header tight and specific - numbers and named
> artifacts over adjectives. Layer in `.research/templates/paper/<type>.md` so this
> discharges the paper type's proof obligation.

## PLAN-KEEP: experiment-design header

Fill every dimension below; drop one only with a one-line reason. This is the content
the old plan stage produced - the single source of truth for it now lives here.

- **Methodology / approach.** The core method, attack/defense design, or construction
  pipeline. Show the smallest concrete instance first - a worked example or a 3-line
  proof-of-concept - before the full machinery.
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

## Task list

Two buckets, sequenced so the experiment that would kill the paper if it fails runs first.

### Build / obtain

One task per artifact to construct or acquire (system / dataset / tool). For each, name
the deliverable and a done-when criterion. Flag any heavy system build: `[spec-kit]` if
it warrants spec-driven development in its own repo, `[dev]` for normal development, and
name the repo it lives in (under `~/Projects/<repo>`, never inside the vault). Light data
wrangling or a one-off script needs no flag.

- [ ] [Deliverable] - done when [criterion]. [`[spec-kit]` / `[dev]` + repo, if heavy]
- [ ] ...

### Experiments

One task per experiment, each tied to exactly one primary claim id (`-> C2`). Each task
names dataset, baselines, metric, and the predicted result / falsifier. Every
contribution's claim id must appear on at least one experiment task; every experiment
task must serve a claim. Flag any contribution with no experiment as an **overclaim to
rescope** and any experiment serving no claim as **scope creep**.

- [ ] [Experiment] over [dataset] vs [baselines] on [metric]; predicts [result / falsifier]. -> C#
- [ ] ...

---
Next: `/research.experiment` (run experiments, fill `claims.md`).
