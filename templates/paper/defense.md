# Defense paper — section skeleton

> Loaded by `/research.paper` when `proposal.md` paper type is `defense`.
> Core question: *can we prevent this threat, and at what cost?* The proof
> obligation is a mechanism that stops the threat AND a quantified cost.
> Fill every bracket; delete beats that do not apply to your sub-genre.

## Pick your sub-genre first (it shapes every section)
- **Property defense** — you define and enforce a security property with a
  guarantee (often a proof). Lead with the property; threat model is standalone.
- **Tool defense** — you build a system/checker that finds or blocks the threat.
  Lead with a problem-tool-result triple; report bugs found / adoption.
- **Algorithm defense** — you make a principled algorithmic move (protocol,
  training, scheme) that trades cost for a property. Lead with the move + costs.

If unsure, name the closest sub-genre and say why. The skeleton below is shared;
the per-section notes flag where the three diverge.

---

## Abstract
[6-10 sentences, headline up front. Property: property + its guarantee, then a
precision/recall/coverage number. Tool: problem -> tool (named) -> result, close
with adoption or bug-count. Algorithm: the algorithmic move + cost dimensions,
guarantee before the percentage. Put one or two effectiveness numbers in the
first few sentences - the numbers are the contribution.]

## Introduction
[For property/tool: threat -> severity escalation (who is hit, how badly) ->
limitations of prior mitigations (the "however" pivot) -> *desiderata* (what an
adequate mitigation MUST do) stated BEFORE you name your contribution -> announce
mechanism + numbered contributions. For algorithm: domain importance -> the
misalignment between current practice and the desired property -> prior tradeoffs
briefly -> the principled move -> contributions. End the contribution list with an
artifact-release bullet as its own contribution. Consider a define/design/
propose/show verb cadence.]

## Background / threat model
[Two distinct jobs - keep them separate.
- Background: teach only the concepts a reader needs to follow the design. For an
  algorithm defense give a dedicated background section naming the pillars your
  contribution fuses; for a tool/system defense fold technical background into the
  design. If your design composes known primitives, add a short tutorial that
  pre-teaches them so Design reads without forward references.
- Threat model: standalone and labeled for a property defense (adversary goal,
  knowledge, capabilities, and an explicit out-of-scope sentence); brief for a
  tool defense; usually informal for an algorithm defense. For a deployed-system
  defense, add a backward-compatibility / non-disruption clause to pre-empt "you
  would break the ecosystem."]

## Design
[Open with one key-observation sentence: the intuition for why the design works
("A key observation motivates our design: <regularity>; because <generic method>
ignores it, we build <mechanism> that exploits it"). Then pick a pattern:
property -> mechanism -> proof (the proof is load-bearing, not an appendix);
system overview -> components (a self-contained mini-overview so a reader who
stops early still understands the system); or instrument the attacker's tool
rather than the victim's environment. State the rationale for each design choice.]

## Implementation
[What you actually built: codebase / language / LOC, the system or model it plugs
into, and any engineering needed to make the defense real (integration points,
deployment surface, what you had to change vs. left untouched). Keep it concrete
and brief; this is where "would this run in practice?" is answered.]

## Evaluation
[Two halves, and their order signals your thesis.
- Security: does it actually stop the threat? (attack success driven to ~0,
  coverage across the threat classes from your threat model, false-negative rate.)
- Performance: what does it cost? (overhead, latency, precision/recall, false
  positives, usability burden.)
Performance-first reads as "the property is obviously valuable; here is that it is
affordable"; security-first reads as "the value is what it finds." Pair every
number with a baseline ("vs. the unprotected baseline, overhead is N%"). A shared
benchmark can unify both halves. Tiered variants of one mechanism (lightweight /
heavyweight) count as ONE contribution, not three.]

## Discussion / limitations
[An honesty paragraph naming the key limitation before a reviewer does, or a
dedicated limitations subsection if there are several. State what the defense does
NOT cover (the out-of-scope cases), how an adaptive attacker might respond, and
the deployment cost in practice. A negative finding stated as a contribution
builds credibility. Add ethics / responsible disclosure here or as its own short
section if the work touches real systems or vendors.]

## Conclusion
[Under one column. Restate the headline guarantee + the one or two cost/
effectiveness numbers, then one forward-looking sentence (adoption signal, what
remains open, or what an attacker would have to do to defeat the defense). No new
claims, no methodology rehash.]

## Related work
[Late by default for systems and ML defenses (place after Design/Evaluation).
Move it early only when the contribution is combinatorial (recombining known
primitives) or contrastive (you must summarize the empirical defenses you position
against). Synthesize prior mitigations into themes and end each paragraph with an
explicit delta ("Unlike these, we provide <guarantee> at <cost>"). A prior-work
delta table makes the gap visual.]

---

## Quality checklist
- [ ] Sub-genre named (property / tool / algorithm) and the abstract leads with
      its tuple plus a headline number in the first few sentences.
- [ ] Desiderata for an adequate mitigation are stated BEFORE the contribution.
- [ ] Threat model placed per sub-genre/venue, with an explicit out-of-scope
      sentence (and a backward-compatibility clause for deployed systems).
- [ ] Design opens with a one-sentence key observation; any proof is in-line and
      load-bearing, not deferred to an appendix.
- [ ] Implementation makes the defense concrete (what was built, where it plugs in).
- [ ] Evaluation covers BOTH security (does it stop the threat) and performance
      (what it costs), each against a named baseline.
- [ ] At least one limitation / negative finding is stated honestly.
- [ ] Tiered variants of one mechanism are counted as a single contribution.
- [ ] Ethics + responsible-disclosure note present if the work touches real
      systems or vendors; artifact link given as its own contribution.
- [ ] Related work placed by contribution type and ends each paragraph with a delta.

---
**Next**: `/research.analyze` to keep `claims.md` in sync before you submit.
