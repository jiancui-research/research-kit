# Research constitution

> The default, project-wide principles read by every `/research.*` command.
> `/research.constitution` copies this file into a project at
> `./.research/memory/constitution.md` and specializes it. Edit freely there;
> the copied file is the source of truth for your quality bar and writing voice.

Focus areas: general (set your field, target venue family, and priorities when you specialize this file)

## Quality principles

- **Rigor.** Every claim is falsifiable, scoped, and backed by a pointer (a number,
  figure, proof, or citation). Conclusions never outrun the evidence: do not claim a
  general capability from a narrow proxy, and state explicitly what was not shown.
- **Reproducibility.** Each contribution is backed by a releasable artifact (code,
  data, proof) or by method detail complete enough to reproduce the headline result
  from the paper alone - hyperparameters, hardware, prompts, seeds, licenses, access.
- **Honest reporting.** Report variance (error bars / CIs / significance tests), tune
  baselines fairly, explain anomalous results, and never train on test data. Report
  negative and null results rather than burying them. Validate any automated or
  LLM-as-judge metric against ground truth on this specific task before trusting it.
- **Ethics.** State both what was done AND why it was the ethical choice, in
  self-contained prose. Identify stakeholders, acknowledge dual-use and second-order
  harms, and for work touching real systems include responsible disclosure (who was
  notified, how they responded). If ethics review was post-hoc, label it as such
  rather than disguising it as a-priori planning.
- **Clarity.** The main body must stand alone without the appendix. State the research
  question or contribution in the first pass, define key terms, and prefer precise,
  falsifiable sentences over vague judgments. Replace "X is weak/unclear" with "X is
  weak because <cause>"; apply the same specificity filter to your own prose.

## Writing voice (customizable)

> This section encodes one common empirical-CS voice. It is a starting point, not
> a mandate - rewrite it to match your subfield and taste when you specialize.

- **Motivation first (NABC).** Lead with why the target matters - a named example, a
  dated incident, or a concrete number - then surface the tension, then the method.
  Before drafting, be able to state Need, Approach, Benefits (quantified, substantially
  better not just different), and Competition as a sub-one-minute pitch. If you cannot,
  the framing is not ready.
- **Unmissable gap.** After motivation, state plainly what is not yet known or done so a
  reader can recite the gap in one sentence. Escalating it ("nobody has even tried to
  detect / mitigate / exploit X") widens the contribution space and previews your list.
- **Gap and surprise framing.** Reserve emphasis markers ("surprisingly", "strikingly")
  for results that genuinely defied expectation; on confirmatory results they read as
  hype. Surprise the reader before they can call a finding obvious.
- **Scoped novelty.** Qualify every novelty claim (first *systematic* study of X *on* Y,
  first *large-scale* measurement of Z). The qualifier is what makes the claim defensible.
- **Active "we" voice.** Use "we show / discover / design / measure" for what you did;
  reserve impersonal voice for stated facts and system behavior.
- **Precise, evidence-bound prose.** Pair every statistic with a named, recognizable
  instance and its absolute count. Attach a number to every superlative or performance
  adjective ("strong performance" is empty; "strong performance (95% precision)" is a
  claim).
- **Name the artifact early.** Give the system, attack, or threat a short memorable name
  on first mention (with its expansion), then reuse it in headers and topic sentences.
- **Translate results into stakes.** Close each key finding with a "so what" sentence:
  who is affected, what practice it questions, what it implies for defense or policy.
- **Related work is positioning.** Synthesize prior work into themes, treat the closest
  2-3 baselines generously (no strawmen), and end each paragraph with an explicit delta
  ("Unlike these, we..."). Name the single closest prior work in the intro itself.

## Venue norms (a menu, not a template)

- Tailor structure to genre (attack / defense / measurement / benchmark) and to the
  target venue. Read 3 recent accepted papers from that venue before fixing structure.
- Security venues typically expect an explicit, labeled threat/adversary model
  (capabilities, knowledge, goals), a disclosure/ethics paragraph, and a roadmap
  sentence ending the intro. ML venues often front-load related work and omit the
  threat-model beat and roadmap sentence. Inherit the host venue's conventions and
  translate the rest.
- Pass the desk-reject gate as a binary pre-flight: scope fit, page/format limits,
  anonymization, required sections (limitations, ethics), reproducibility checklist.

## Self-review stance

- Before submission, write a mock review of your own draft across the five axes:
  motivation, contribution, evaluation, related work, presentation. Each axis must
  yield one concrete, specific weakness - then fix it or pre-empt it in the text.
- Maintain a claim <-> evidence ledger: every abstract/intro claim mapped to the exact
  result that supports it. Any unsupported row is an overclaim to rescope or back up.

## How to customize this for your project

1. Set **Focus areas** above to your field, target venue family, and top priorities
   (e.g. "security measurement, USENIX-family venue, strict reproducibility").
2. Keep the **Quality principles** as your non-negotiable floor; add at most a few
   project-specific bullets. Do not weaken rigor, honesty, or ethics to fit a deadline.
3. Treat **Writing voice** as fully editable. Adjust it to your subfield's idiom; drop
   or rewrite any move that does not fit (the motivation-first and NABC framing port
   widely, but the exact rhetoric is yours to set).
4. Under **Venue norms**, keep only the conventions that apply to your venue and delete
   the rest. When unsure, the default answer is: read recent accepted papers and copy
   their spine.
5. Do not paste private results, names, datasets, or unpublished findings here - this
   file is durable, project-wide guidance, not a scratchpad.
