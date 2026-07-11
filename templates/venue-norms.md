# Venue norms: choosing a venue and adapting to its conventions

> Consulted by /research.proposal (when choosing a target venue + paper type) and /research.paper (for structure conventions).

**TL;DR:** Pick the venue *before* you draft - it sets your structure, your review game, and your obligations. The biggest split is **security** (USENIX Security, IEEE S&P, ACM CCS, NDSS) vs **AI/ML** (NeurIPS, ICML, ICLR, ACL/EMNLP via ARR). Same finding, different paper.

## Choosing a venue - decision checklist
- **Fit first.** Match topic, *method*, and *audience*. A measurement of model misuse reads as security at CCS and as an evaluation paper at EMNLP - the contribution framing changes, not the data.
- **Tier honestly.** Top-tier rejection costs a cycle. Weigh acceptance odds against the deadline you can actually hit with the evidence you have *now*.
- **Timeline.** Map the deadline to your eval plan. Rolling/multi-deadline venues (ARR, USENIX cycles) trade flexibility for longer end-to-end time; one-shot conferences (NeurIPS, ICML) are higher-variance.
- **Page limit.** Security venues run long (roughly a dozen+ pages, body excludes references/appendix); ML venues run shorter with hard main-paper caps and unlimited appendix. This decides how much fits in the body vs the appendix.
- **Review model.** Single vs multi-round, rebuttal format, score axes, shepherding, revision option. Know what you're signing up to defend.

## Security venues - what reviewers expect
- **Labeled threat / adversary model**, as its own beat: explicit *goal*, *knowledge* (black- vs white-box, interface touched), *capabilities*, and an **out-of-scope** sentence. Implicit assumptions read as a flaw.
- **Disclosure + ethics paragraph**, often a standalone section: who was notified, embargo, CVEs, IRB/data handling. Treated as a gating requirement, not a courtesy.
- **Roadmap sentence** ending the introduction ("The rest of the paper is organized as...").
- **Artifact evaluation + badges** (Available / Functional / Reproduced) as a separate, post-acceptance track with a permanent archival link.
- **Multi-round review**, major/minor **revision** decisions, and **shepherding** toward camera-ready.
- **Rebuttal**: a short author response to specific reviewer points; aim to flip the on-the-fence reviewer, not relitigate everything.

## AI/ML venues - what reviewers expect
- **Front-loaded related work** - positioning early is the norm; the contribution is read against the literature up front.
- **Usually no standalone threat-model beat and no roadmap sentence.** State assumptions inline where they bind.
- **Numeric multi-axis scores** (soundness, contribution, presentation, confidence) plus a **reviewer-author discussion** thread - dialogue, not a single fixed-length reply.
- **Reproducibility checklist** at submission (code, hyperparameters, compute, data access, broader-impacts statement) rather than a separate badge program.
- **Rebuttal / discussion phase**: post results, answer questions, update the PDF; reviewers may raise scores during discussion.

## Comparison

| Dimension | Security (USENIX Sec, S&P, CCS, NDSS) | AI/ML (NeurIPS, ICML, ICLR, ARR) |
|---|---|---|
| Structure | Roadmap sentence; longer body | No roadmap; tighter main paper + appendix |
| Threat model | Explicit labeled section | Inline assumptions, no fixed beat |
| Related work | Late by default | Front-loaded |
| Rebuttal mechanic | Short one-shot author response | Multi-turn discussion + PDF update |
| Artifact / repro | Artifact eval + badges + archival link | Reproducibility checklist + code release |
| Ethics | Disclosure + ethics section, gating | Broader-impacts / ethics statement |

## How the choice changes your paper
Same result, two papers. For **security**, lead with the threat it enables, add the labeled threat model and disclosure beats, and budget space for the roadmap and artifact track. For **AI/ML**, lead with the gap in the literature, front-load related work, fold assumptions inline, and prepare for a discussion-phase dialogue plus a reproducibility checklist. Pick the venue, then let its norms drive section order and emphasis.

## Quality checklist
- [ ] Venue chosen on fit + tier + a timeline you can actually meet.
- [ ] Paper type and section order match the venue's expected structure.
- [ ] Security: labeled threat model, disclosure/ethics, roadmap sentence, artifact/badge plan present.
- [ ] AI/ML: front-loaded related work, reproducibility checklist, broader-impacts statement, discussion-phase plan.
- [ ] Page budget split between body and appendix per the venue's limits.
- [ ] You know the review model and what you'll be asked to defend.

---
**Next**: feed the chosen venue + paper type back to `/research.proposal`, then `/research.paper` for the matching skeleton.
