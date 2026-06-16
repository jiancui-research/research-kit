# Paper section plan & task list: [project / paper short name]

> Produced by `/research.tasks`. Lives at `./.research/tasks/paper.md`.
> One task per section, in the paper-type skeleton's order (from
> `.research/templates/paper/<type>.md`). Each task is tagged **READY** (write now) or
> **BLOCKED on claim Cx** (waits on a result). This file is the parallel partner of
> `tasks/experiment.md`: experiments fill `claims.md`, and a BLOCKED section unblocks the
> moment its claim is marked supported.

## How to read the tags

- **READY** - framing sections that need no result: intro, related work, method /
  attack-design / construction, threat model, background. Write these immediately, in
  parallel with experiments. They establish the argument the results will land in.
- **BLOCKED on claim Cx** - results-dependent sections: evaluation / findings, abstract,
  conclusion, and any discussion that quotes a number. Name the exact claim id(s) the
  section waits on, so it unblocks as soon as `claims.md` marks them supported.

Keep one task per section, in the skeleton's order. Do not invent sections the skeleton
does not have; drop a skeleton section only with a one-line reason.

## Task list

Pick the block below that matches the paper type from `proposal.md`; delete the others.
Fill each task's claim ids from the contributions in `proposal.md` / `claims.md`.

### measurement

- [ ] Introduction - frame target, gap, RQs, preview headline finding. **READY**
- [ ] Background / related work - themes + per-work delta + the gap. **READY**
- [ ] Methodology - data sources, construction, ground-truth quality, bias. **READY**
- [ ] Findings - one subsection per RQ, bolded takeaways. **BLOCKED on claim C#**
- [ ] Discussion / implications - generalize, limits, per-stakeholder "so what". **BLOCKED on claim C#**
- [ ] Ethics & responsible disclosure - data handling, disclosure outcome. **READY**
- [ ] Conclusion - restate headline number, broader implication. **BLOCKED on claim C#**
- [ ] Abstract - problem -> method -> headline number -> implication. **BLOCKED on claim C#**

### attack

- [ ] Introduction - threat class, violated assumption, attack idea, scope. **READY**
- [ ] Threat model - adversary goal, knowledge, out-of-scope line. **READY**
- [ ] Background - prerequisite internals; reused vs new primitives. **READY**
- [ ] Attack design - organizing pattern, smallest concrete instance first. **READY**
- [ ] Evaluation - severity and/or coverage, named-victim impact line. **BLOCKED on claim C#**
- [ ] Countermeasures & limitations - refute/propose defenses, quantify cost. **BLOCKED on claim C#**
- [ ] Disclosure & ethics - vendors notified, embargo, CVEs. **READY**
- [ ] Conclusion - forward-looking defense sentence, community implication. **BLOCKED on claim C#**
- [ ] Abstract - target -> claim -> demonstration -> scope. **BLOCKED on claim C#**

### defense

- [ ] Introduction - threat, prior-defense gap, mechanism idea, results preview. **READY**
- [ ] Background / threat model - adversary model + what the design must stop. **READY**
- [ ] Design - the mechanism, smallest concrete instance first. **READY**
- [ ] Implementation - what was built, environment, deployment surface. **READY**
- [ ] Evaluation - two-sided: stops the threat + quantified cost. **BLOCKED on claim C#**
- [ ] Discussion / limitations - residual risk, adaptive attacker, bounds. **BLOCKED on claim C#**
- [ ] Related work - themes + per-work delta + the gap. **READY**
- [ ] Conclusion - restate guarantee and its cost, future work. **BLOCKED on claim C#**
- [ ] Abstract - threat -> mechanism -> guarantee + cost. **BLOCKED on claim C#**

### benchmark

- [ ] Introduction - task importance, gap in prior benchmarks, contributions. **READY**
- [ ] Related benchmarks / related work - table of prior benchmarks + delta. **READY**
- [ ] Task formulation - the concrete task tuple (input, output, success). **READY**
- [ ] Design / construction - dataset build, filters, dedup, contamination check. **READY**
- [ ] Validation (is the benchmark sound?) - IAA, ground-truth quality, leakage. **BLOCKED on claim C#**
- [ ] Evaluation protocol - metrics, judge validation, variance reporting. **READY**
- [ ] Experiments / leaderboard - 3-5 baselines, headline gaps. **BLOCKED on claim C#**
- [ ] Discussion - what the scores mean, limits, generalization. **BLOCKED on claim C#**
- [ ] Ethics, responsible disclosure, and artifact - release plan, licenses. **READY**
- [ ] Conclusion - restate the benchmark + headline gap, future work. **BLOCKED on claim C#**
- [ ] Abstract - task -> benchmark -> baselines -> headline gap. **BLOCKED on claim C#**

### systematization (SoK)

- [ ] Introduction - why systematize now, the gap no single paper fills. **READY**
- [ ] Scope & methodology - corpus, selection criteria, what is in/out. **READY**
- [ ] Taxonomy / framework - the novel, MECE-ish axes. **READY**
- [ ] Systematization body - map prior work onto the taxonomy. **READY**
- [ ] Lessons learned / open problems / research agenda - the cross-paper insight. **BLOCKED on claim C#**
- [ ] Related surveys & SoKs - delta vs prior surveys. **READY**
- [ ] Conclusion - restate the taxonomy + top lesson, agenda. **BLOCKED on claim C#**
- [ ] Abstract - scope -> taxonomy -> the lesson found in no single prior paper. **BLOCKED on claim C#**

## Validate before writing

- One task per skeleton section, in order; no invented sections; any dropped section has
  a one-line reason.
- Every BLOCKED task names the exact claim id(s) it waits on; every claim id that gates a
  section here also appears on an experiment task in `tasks/experiment.md`.
- Framing sections (intro, method, threat model, background, related work) are tagged
  READY, not blocked.

---
Next: `/research.experiment` and `/research.paper` (run in parallel, synced by `claims.md`).
