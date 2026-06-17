---
description: Establish or update the research constitution (quality principles + writing voice + venue norms) at .research/memory/constitution.md
argument-hint: optional focus areas, e.g. "security venue, measurement, strict reproducibility"
---

## User input

The user's focus areas (paper field, target venue family, priorities such as
reproducibility/ethics/honest reporting, or "tighten the voice section") arrive
via the `$ARGUMENTS` placeholder. Treat it as optional steering, not a full spec.

## What this command owns

This is the FIRST command in the pipeline. It creates the `.research/` scaffold
and writes ONE artifact: `.research/memory/constitution.md`. Every later command
reads this file, so keep it durable, paper-type-agnostic, and project-wide.

## Steps

1. **Scaffold.** `mkdir -p` the working tree if missing:
   `.research/memory`, `.research/tasks`, `.research/review`, `.research/rebuttal`,
   `.research/ae`.
   (`proposal.md`, `related-work.md`, `feasibility.md`, `claims.md`, and
   `analyze-report.md` are flat files at `.research/` root - no dirs needed. Each
   lane's actual work lands in a root-level folder created by its own command -
   `feasibility/`, `design/`, `eval/`, `paper/` - never inside `.research/`.)

2. **Read existing constitution if present.** If `.research/memory/constitution.md`
   already exists, read it and treat this run as an UPDATE: preserve the user's
   edits, fold `$ARGUMENTS` in, and report a short diff of what changed. Never
   silently overwrite hand-written principles.

3. **Seed from the default below if absent.** If no constitution exists, write the
   default template in this file's "Default constitution" section, then specialize
   it using `$ARGUMENTS` (set the venue family, foreground the user's stated
   priorities). If `$ARGUMENTS` is empty, write the default verbatim and say so.

4. **Specialize, do not bloat.** Keep it readable in one screen-scroll per section.
   Add at most a few user-specific bullets; do not invent project facts, names,
   datasets, or results. Venue norms are a MENU, not a fixed template - flag which
   conventions apply to the user's venue family (security expects an explicit
   threat-model beat and a roadmap sentence; ML venues front-load related work and
   often omit both). When in doubt, tell the user to read 3 recent accepted papers
   from their target venue.

5. **Validate** against the checklist below, then write the file.

## Default constitution

Write the following to `.research/memory/constitution.md`, adapting the bracketed
slots to `$ARGUMENTS` where given.

```markdown
# Research constitution

> Project-wide principles read by every /research.* command. Edit freely;
> this file is the source of truth for quality bar and writing voice.

Focus areas: [field / target venue family / priorities from user, or "general"]

## Quality principles

- **Rigor.** Every claim is falsifiable, scoped, and backed by a pointer (a number,
  figure, proof, or citation). Conclusions never outrun the evidence: do not claim a
  general capability from a narrow proxy, and bound explicitly what was not shown.
- **Reproducibility.** Each contribution is backed by a releasable artifact (code,
  data, proof) or by method detail complete enough to reproduce the headline result
  from the paper alone: hyperparameters, hardware, prompts, seeds, licenses, access.
- **Honest reporting.** Report variance (error bars / CIs / significance), tune
  baselines fairly, explain anomalous results, and never train on test data. Report
  negative and null results rather than burying them. Validate any automated or
  LLM-as-judge metric against ground truth on this specific task before trusting it.
- **Ethics.** State what was done AND why it was the ethical choice, in self-contained
  prose. Identify stakeholders, acknowledge dual-use and second-order harms, and for
  work touching real systems include responsible disclosure (who was notified, how
  they responded). If ethics review was post-hoc, label it as such, do not disguise it.
- **Integrity.** Every citation genuinely supports its sentence; related work states
  how each neighbor differs rather than just listing it. No fabricated, hallucinated,
  or mischaracterized references.

## Writing voice

- **Motivation first (NABC).** Lead with why the target matters - a named example, a
  dated incident, or a concrete number - then surface the tension, then the method.
  Before drafting, be able to state Need, Approach, Benefits (quantified, substantially
  better), and Competition as a sub-one-minute pitch. If you cannot, the framing is not
  ready.
- **Unmissable gap.** After motivation, state plainly what is not yet known or done so a
  reader can recite the gap in one sentence. Escalate it ("nobody has even tried to
  detect/mitigate/exploit X") to widen the contribution space.
- **Scoped novelty.** Qualify every novelty claim (first *systematic* study of X *on* Y,
  first *large-scale* measurement of Z). The qualifier is what makes it defensible.
- **Active "we" voice.** Use "we show / discover / design / measure" for what you did;
  reserve impersonal voice for stated facts and system behavior.
- **Evidence-bound emphasis.** Pair every statistic with a named, recognizable instance
  and its absolute count. Reserve "surprisingly" for genuinely surprising results, and
  attach a number to every superlative or performance adjective.
- **Name the artifact early.** Give the system/attack/threat a short memorable name on
  first mention, then reuse it in headers and topic sentences.
- **Translate results into stakes.** Close each key finding with a "so what" sentence -
  who is affected, what practice it questions, what it implies for defense or policy.
- **Related work is positioning.** Synthesize prior work into themes, treat the closest
  2-3 baselines generously (no strawmen), and end each paragraph with an explicit delta
  ("Unlike these, we..."). Name the single closest prior work in the intro itself.

## Venue norms (a menu, not a template)

- Tailor structure to genre (attack / defense / measurement / benchmark) and to the
  target venue. Read 3 recent accepted papers from that venue before fixing structure.
- Security venues: expect an explicit, labeled threat/adversary model (capabilities,
  knowledge, goals), a disclosure/ethics paragraph, and a roadmap sentence ending the
  intro. ML venues: often front-load related work and omit the threat-model beat and
  roadmap sentence. Inherit the host venue's conventions and translate the rest.
- Pass the desk-reject gate as a binary pre-flight: scope fit, page/format limits,
  anonymization, required sections (limitations, ethics), reproducibility checklist.

## Self-review stance

- Before submission, write a mock review of your own draft across the five axes:
  motivation, contribution, evaluation, related work, presentation. Each axis must
  yield one concrete, specific weakness - then fix it or pre-empt it in the text.
- Maintain a claim <-> evidence ledger: every abstract/intro claim mapped to the exact
  result that supports it. Any unsupported row is an overclaim to rescope or back up.
```

## Quality checklist

- Scaffold created; only `.research/memory/constitution.md` written by this command.
- Existing user edits preserved on update; changes reported, nothing silently clobbered.
- Quality principles cover rigor, reproducibility, honest reporting, ethics, integrity.
- Voice section is motivation-first / NABC, gap framing, scoped novelty, active voice.
- Venue norms framed as a menu; security-vs-ML differences flagged; no invented facts.
- Readable, paper-type-agnostic, free of project-specific names/data/results.

## Completion

Report the path `.research/memory/constitution.md` and whether it was created or
updated. Next: /research.proposal
