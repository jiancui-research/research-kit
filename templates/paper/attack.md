# Attack paper — section skeleton

Core question: *Is this system insecure, and can I prove it?* Proof obligation: a **working exploit** plus evidence it is **not a corner case** (works across configurations, not one lucky setup).

Use this as a section menu, not a fixed mold. Threat-model and related-work placement below assume a security venue; at AI/ML venues fold the threat model into the intro and move related work earlier.

## Abstract
Compress the tuple **target → claim → demonstration → scope**. Optionally lead with the surprise (the conclusion as the first line). End with a scope qualifier (which systems/architectures/model families it works on) to pre-empt "but does it work on real systems?"

## Introduction
Four-ish moves: motivate the threat class, name the prior assumption being violated (what people *thought* was secure), state the attack idea in one sentence, then give the demonstration scope (how many systems/CVEs/how universal) and a numbered contributions list. For multi-result attacks, consider numbered result subsections plus a short outline paragraph.

## Threat model
Standalone section here (a fixed labeled beat): **adversary goal**, **adversary knowledge** (black-box vs white-box, what interface they touch), and an explicit **out-of-scope** sentence. Enumerate capabilities; do not leave them implicit.

## Background
A focused one-page primer on the prerequisite hardware/OS/protocol/model internals the reader needs to follow the attack - do not lean on citations to teach. Separate primitives you *reuse* from prior work from what is *new* here.

## Attack design
Pick one organizing pattern: end-to-end pipeline (phase = subsection, flow diagram), core recipe + variants by adversary knowledge/budget, named-stage pipeline (each stage gets its own per-stage evaluation later), or primitive-composition (two known weaknesses + a novel combination). **Show the smallest concrete instance first** - a three-line proof-of-concept or a single annotated Figure 1 before the full machinery.

## Evaluation
Decide whether you are claiming **severity** (how bad: leak rate, accuracy, time-to-compromise) or **coverage** (where it applies: architectures, datasets, budgets) - the best papers do both with different subsection structure. Include reproducibility signals (code, checkpoints, exact hyperparameters) and add one named-victim / concrete-impact sentence right after the headline result.

## Countermeasures & limitations
Required even if brief - mounting an attack and walking away reads as a rejection signal. Either refute prior defenses (show each fails, and how) or propose mitigations and **quantify their cost**. State the attack's own limitations honestly.

## Disclosure & ethics
Mandatory. Name vendors/parties notified, the embargo timeline, and any CVE assignments. For attacks without a specific vendor, focus on responsible release of attack code and datasets. One disclosure paragraph proves real-world impact and ethical conduct at the same time - keep it visible from the table of contents.

## Conclusion
Short, with a forward-looking sentence about defense even if you propose none: name what would have to change to defeat the attack, and close with a community/policy implication (a norm, vetting process, or default your attack should change).

---
**Next**: `/research.analyze` to keep `claims.md` in sync before you submit.
