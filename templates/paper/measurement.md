# Measurement paper: [system / ecosystem under study]

> Paper-type skeleton for `/research.paper` (paper-type: measurement).
> Read `./.research/proposal.md`, `./.research/tasks.md`, and `./.research/claims.md` first.
> Core question: *what is actually happening?* Proof obligation: a defensible
> dataset + a sound methodology + a surprising, anchored finding.
> Fill every bracket. Drop a section only with a one-line reason why it does not apply.

## Abstract
[6-10 sentences: problem -> method -> headline number -> implication. Lead with the
ecosystem, not the technique. The headline number IS the contribution, so put it here.
Close with a specific call to action, not "more research is needed."]

## 1. Introduction
[Five moves: (1) target importance via a number or named example; (2) a "however"
pivot to the security/social tension; (3) the gap - what is not yet known; (4) "in this
paper, we..." with scope bounded and 2-4 explicit research questions (RQ1, RQ2...);
(5) preview one surprising headline finding. Scope the novelty claim precisely - "first
systematic study of X on Y", with the noun qualified. End with a contribution list and,
at security venues, a roadmap sentence. Each findings subsection later answers one RQ.]

## 2. Background / related work
[Teach only what the reader needs to follow the findings. Place related work late by
default (the contribution is a new finding); move it earlier only if results are
uninterpretable without prior approaches. Synthesize into themes; end each theme with an
explicit delta ("Unlike these, we..."). A prior-work comparison table makes the gap visual.]

## 3. Methodology
[Where credibility is earned. State data sources concretely (sizes, dates, provenance).
Defend construction: what was excluded, deduplicated, or unobtainable, and why. Quantify
ground-truth quality (inter-annotator agreement, validation against known labels). Address
bias openly - coverage, selection, survivorship. Embed ethics/data-handling here or signal
a standalone section below.]

## 4. Findings
[Organize by research question (1:1 with the RQs) or by phenomenon/phase. Open each
subsection with a one-sentence bolded takeaway that could stand alone in the abstract -
the bold headers alone should convey the thesis. Pair every statistic with a recognizable
anchor and always give the absolute count beside the percentage, e.g. "13% (1,306 sites),
including [named instance]." Reserve "surprisingly" for genuinely surprising results.]

## 5. Discussion / implications
[Distinct from the conclusion. Generalize beyond the sample (does it hold elsewhere, and
why). Name limitations honestly. Constrain the defense design space rather than proposing a
full defense. Anticipate adversarial reaction. Address each stakeholder your findings should
reach - developers, platforms, regulators, users - with a concrete "so what" per group.]

## 6. Ethics & responsible disclosure
[Standalone signals seriousness and meets venue rules (or fold into methodology to keep it
near the data decisions). Cover data handling, IRB/redaction if applicable, and a disclosure
paragraph naming who was notified and how they responded (acknowledged / patched / no reply).
One paragraph proves ethics and real-world impact at once.]

## 7. Conclusion
[Under one column. Restate the headline number, name the broader implication, gesture at
future work in one sentence. Do not rehash methodology, list subsections, or add new claims.]

---
**Artifact**: link the public artifact (dataset/code) in an abstract footnote and again in
the intro. **Next**: `/research.analyze` to keep `claims.md` in sync with the findings above.
