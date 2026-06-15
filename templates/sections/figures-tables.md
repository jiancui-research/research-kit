> Loaded by /research.paper when designing figures, tables, or results presentation. Cross-cutting craft.

# Figures and tables

TL;DR: every float earns its space by carrying one idea and stating its takeaway in the caption. Figure 1 sells the contribution; tables prove it.

## Figure 1: the money figure

The opener that conveys the core idea or system architecture *before* the reader hits the machinery. It is the most-looked-at object in the paper after the title.

- Show the smallest concrete instance first - one real input flowing to one real output - not an abstract block diagram of every component.
- Make the contribution visible: what is new should be the thing the eye lands on.
- A reader who sees only Figure 1 and its caption should be able to state what you built and why it matters.

## Self-contained captions

Every figure and table caption states its one-sentence takeaway, so a skimmer gets the point without reading the body.

- Lead with the claim ("X cuts error in half vs. the baseline"), then explain how to read the float.
- Define axes, units, and any non-obvious symbol in the caption, not only in prose.
- A caption that just names the figure ("System overview.") is a wasted caption.

## Comparison / delta tables

A prior-work comparison table makes the gap visual.

- Rows = systems (prior work + yours, yours last); columns = properties; cells = check / cross / partial.
- Choose columns = the axes that actually matter for this paper type, so your contribution is the column others miss. Do not pad with dimensions where everyone scores the same.
- The table should make the reader think "nothing before had all of these" without you saying it.

## Results tables

- Bold the headline number so the eye finds the result instantly.
- Always pair a number with its baseline; an absolute number with nothing to compare against is noise.
- Report variance: error bars, confidence intervals, or std over seeds. A point estimate with no spread invites disbelief.
- Never dump raw numbers without a takeaway - if a row has no story, cut it or move it to an appendix.

## General

- One idea per figure. If a figure needs two paragraphs to explain, it is two figures.
- Reference every float from the text and tell the reader what to notice in it.
- Prefer a **figure** when the relationship is spatial or structural (flow, architecture, trend); prefer a **table** when it is a precise comparison (exact numbers, feature matrices).
- Keep visual encoding honest: zeroed axes where it matters, consistent scales across compared plots, colorblind-safe palettes.

## Quality checklist

- [ ] Figure 1 conveys the core idea via a small concrete instance, before any machinery.
- [ ] Every caption states a one-sentence takeaway and defines its axes/units.
- [ ] A comparison table exists with rows = systems, columns = the axes that matter, and your row stands out.
- [ ] Headline numbers are bolded and each is paired with a baseline.
- [ ] Variance is reported (error bars / CIs / std), not just point estimates.
- [ ] No raw-number dumps without a takeaway; weak rows cut or moved to appendix.
- [ ] One idea per figure; every float is referenced and interpreted in the text.
- [ ] Figure-vs-table choice matches the data (spatial → figure, precise comparison → table).
