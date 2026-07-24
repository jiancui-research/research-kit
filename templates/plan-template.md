# Study plan: [project / paper short name]

> Produced by `/research.plan`. Lives at `./.research/plan.md`.
> The **technical design of the study** - stable and reviewable, with no task list
> (tasks derive from this via `/research.tasks` and churn separately in `tasks.md`).
> This doc is the source for the paper's System Design section and the contract the
> evaluation must satisfy. Change it only when the *study* changes; `/research.analyze`
> flags anything downstream that a change makes stale.

## System architecture (paper-type aware)

[Heavy for systems/defense (full architecture), medium for attack (PoC / exploit) and
benchmark (construction harness + dataset), light or absent for measurement (a
collection pipeline) / SoK (corpus tooling, often nothing). If nothing is built, say so
in one line and delete the diagram.]

[The architecture in one paragraph, then a diagram. Components, and how data / control
flows between them. Show the smallest end-to-end path first.]

```mermaid
[workflow diagram: components + arrows]
```

- **Components.** [one line each: name -> responsibility]
- **Data / control flow.** [the main path, end to end]

## Key decisions & rationale

[The load-bearing choices a reviewer will question. For each: the decision, why, and the
rejected alternative. This is what the paper's design section has to defend.]

- Decision: [...] - chosen because [...]; rejected [alternative] because [...].

## Evaluation design

Fill every dimension; drop one only with a one-line reason. Numbers and named artifacts
over adjectives. Layer in `.research/templates/paper/<type>.md` so this discharges the
paper type's proof obligation.

- **Methodology.** How the evaluation works and what is varied. Reference the
  architecture above; do not re-describe it. Show the smallest concrete instance first.
- **Baselines.** 3-5 comparison points (unmodified default / do-nothing AND a fairly
  tuned state of the art). Note how each is tuned so no reviewer can call it a strawman.
- **Datasets / data sources.** Sizes, dates, provenance, construction filters (dedup,
  leakage / contamination checks). State known bias openly.
- **Metrics.** One operational definition per metric, each tied to a claim id. Plan
  variance reporting (error bars / CIs / significance); plan how any LLM judge is
  validated against ground truth.
- **Threat model** (attack / most defense papers). Adversary goal, knowledge, and an
  explicit out-of-scope sentence. Skip or minimize for measurement / benchmark unless
  the venue expects it.
- **Evaluation design.** What each eval varies, conditions and ablations, severity vs
  coverage. Defense gets a two-sided design (stops the threat + cost).
- **Ethics, disclosure, artifact.** Responsible disclosure, IRB / consent / redaction,
  and what artifact will be released.

## Project layout

[The layout every stage agrees on. **This section declares where the implementation
code lives** - `/research.implement` builds there, nowhere else. Default `./src/`;
existing projects using `./design/` keep it (legacy).]

- Implementation code: `./src/` [or the project's own convention - declare it here]
- Evaluation scripts / data / results: `./eval/`
- Feasibility probe (throwaway): `./feasibility/`
- Manuscript: sibling repo recorded in `.research/paper-repo` (resolved by `/research.paper`)
- Naming conventions: [shared rule for files, modules, eval scripts]

## Paper skeleton

- Paper type: [measurement / attack / defense / benchmark / SoK] (from `proposal.md`)
- Section order: per `.research/templates/paper/<type>.md`[, with deviations + one-line reasons]

## Validate before planning tasks

- [ ] Architecture diagram shows every component and the end-to-end path (or "nothing built" is stated).
- [ ] Each decision names its rejected alternative.
- [ ] Every metric ties to a claim id; baselines could actually beat you.
- [ ] The code-folder declaration is explicit; eval scripts have a home.
- [ ] For measurement / SoK the architecture section is correctly minimal.

---
Next: `/research.tasks` (derive the single task queue from this plan).
