> Loaded by `/research.review` alongside the venue guide, once the paper type is known. Read
> **only** the block for your type. The venue guide says how this community reviews; this says
> what to press on for this kind of paper.

# Reviewer probes by paper type

Each type carries a proof obligation the kit already states in `paper/<type>.md`. Reviewing is
mostly the inverse: find where that obligation was assumed rather than discharged. A paper can
be polished, honest, and well written and still fail its type's obligation - that is the finding
worth writing.

---

## Measurement

**Must prove:** a defensible dataset, a sound methodology, and a finding that is surprising and
anchored.

- **Where the population came from.** Is the corpus the thing the claims are about, or a
  convenience sample standing in for it? A claim about an ecosystem drawn from what one vantage
  point could see is a claim about that vantage point.
- **Ground truth.** Who labelled it, against what definition, with what agreement between
  labellers, and how were disagreements resolved? An unlabelled "we manually verified" is not a
  method.
- **Automated classification.** If a classifier or model produced the numbers, what is its
  measured error on *this* data, and does the headline number survive that error bar?
- **Time.** Was the measurement a snapshot or longitudinal, and does the claim quietly assume
  the other one?
- **Numbers with no denominator.** A count is not a rate. Check that every percentage names the
  population it is over.
- **The "so what".** Findings without an implication are an observation log. Does each headline
  finding say who should do something differently?

## Attack

**Must prove:** a working exploit, plus evidence it is not a corner case.

- **The threat model, bounded on all four sides.** Adversary goal, knowledge, capability, and
  what they may **not** do. Unbounded adversaries make the result unfalsifiable.
- **Does the demonstration match the model?** Papers commonly assume less in the model than the
  exploit actually needed - privileged position, a specific version, a disabled mitigation.
- **Breadth.** One lucky configuration is a demo. Across versions, vendors, and defaults is an
  attack. Which was shown?
- **Defenses that already exist.** Would a deployed mitigation have stopped this? If the paper
  disables one to make the attack work, that must be argued, not omitted.
- **Real-world reachability.** Is the vulnerable path reachable by the adversary the model
  describes, or only from a state the adversary cannot arrange?
- **Ethics and disclosure.** Live systems touched, data collected, parties notified, and how
  long before publication.

## Defense

**Must prove:** a mechanism that stops the threat **and** a quantified cost.

- **Cost stated at all.** Effectiveness without overhead is half a result. Latency, throughput,
  memory, false positives, and human effort where it applies.
- **The adaptive adversary.** Evaluated against an attacker who knows the defense exists? A
  defense tested only on the original attack is tested against the weakest opponent available.
- **Baselines that were actually tuned.** An untuned baseline is a strawman, and it is the most
  common way a defense paper's margin evaporates.
- **False positives in context.** A 1% false-positive rate is disqualifying at some deployment
  scales and irrelevant at others. Does the paper say which it is aiming at?
- **Where the evaluation data came from**, and whether the defense was tuned on data that
  overlaps it.
- **What it does not stop.** A defense with no stated boundary is either untested or overclaimed.

## Benchmark

**Must prove:** a precisely defined task, a defensibly constructed dataset, operationally
defined metrics, and real baselines. Hand-wave any of the four and polish will not save it.

1. **Novelty and gap.** What do existing benchmarks not cover that this one does? "There is no
   benchmark for X" needs the list of what was checked.
2. **Data construction.** Transparent and reproducible collection and annotation; agreement
   between annotators where humans labelled; consent, privacy, and approval where the data is
   about people; and an explicit look at who or what is over- and under-represented.
3. **Validity.** Is the ground truth correct, and does the task measure the capability it is
   named after? A benchmark that names a broad ability and tests a narrow proxy is the standard
   failure here.
4. **Utility.** Baseline results from existing methods, showing the benchmark is both usable and
   **discriminative** - if everything scores the same, it separates nothing. Plus a stated
   metric and protocol, public release, documentation, and a loading path that works.
5. **Scale and sustainability.** Large enough to be meaningful, and is there a plan for
   extension, versioning, and contamination as models train on it?

## Systematization (SoK)

**Must prove:** a novel, defensible taxonomy **plus** lessons that appear in no single prior
paper. Reorganization that produces new understanding - not a literature dump.

- **Is the taxonomy load-bearing?** Do the axes separate the work in a way that changes what a
  reader would do, or is it a table of contents with headings?
- **Selection.** How was the corpus chosen, over what period and venues, and what was excluded?
  An unstated inclusion rule makes every count in the paper unverifiable.
- **New understanding.** Which lesson is genuinely not in any single surveyed paper? If every
  insight traces to one prior work, this is a survey.
- **Fairness to the work surveyed.** Are systems characterized as their authors would recognize?
- **Ethics.** A taxonomy of attacks is an artifact of its own: does organizing this make
  something easier for an adversary, and did the paper engage with that?
