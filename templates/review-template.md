# Mock peer review: [paper short title]

> Produced by `/research.review`. Lives at `./.research/review/[short-name].md`.
> Write this review about your OWN draft, as the most skeptical qualified reviewer
> on the panel would - then fix what it surfaces or pre-empt it in the text.
> Vague criticism ("motivation is weak", "not novel") is worthless from a reviewer
> AND from you. Every line below must be specific: name the cause, point to the
> place, and say what would fix it. If an axis yields no concrete weakness, you have
> not looked hard enough.

## Summary
[2-4 sentences, in your own words as a reviewer: what problem the paper attacks,
what it claims to contribute, and how it argues that. If you cannot restate the
research question and the contribution from the main body alone (no appendix), that
is the first finding - the paper is not yet self-contained.]

## Strengths
[Concrete, specific, tied to evidence. "Solid evaluation" is not a strength; "the
ablation in Table 3 isolates the contribution of component X" is.]
- S1: [strength] -> [the figure / table / section / number that earns it]
- S2: [...]
- S3: [...]

## Weaknesses
[The load-bearing part. Walk the five recurring review axes; each MUST yield at
least one concrete, justified weakness a reviewer could raise. For each, state the
cause and a fix or a pre-emption in the paper.]

- Motivation & problem: [what a reviewer could attack] -> [cause] -> [fix / where to address]
- Technical contribution: [is the novelty real and clearly delimited from prior work?] -> [...] -> [...]
- Evaluation: [do the evals directly test each claim? fair baselines? variance reported? leakage?] -> [...] -> [...]
- Related work: [closest neighbor that is under-cited or mischaracterized] -> [...] -> [...]
- Presentation: [where a first-pass reader gets lost or a term is undefined] -> [...] -> [...]

[Also flag any scope mismatch: a claim whose verb ("solves", "proves reasoning",
"guarantees") outruns what was measured. Cross-check against `claims.md` - any row
not `supported` is a weakness here until rescoped or cut.]

## Detailed comments
[Ordered, specific, actionable - the granular pass. Reference exact locations
(Section / Figure / Table / line). Separate "must fix before this is publishable"
from "would strengthen". Apply the specificity rule to your own prose: replace any
"X is unclear" with "X is unclear because <cause>, fixable by <change>."]
- Major:
  - [M1: location -> issue -> concrete change]
  - [M2: ...]
- Minor:
  - [m1: location -> issue -> concrete change]
  - [m2: ...]

## Questions for authors
[The questions a reviewer would expect answered in the rebuttal. Phrase them as you
would want them phrased about your work: pointed, answerable with a specific result,
not rhetorical. These seed the rebuttal-readiness map below.]
- Q1: [...]
- Q2: [...]
- Q3: [...]

## Score + rationale
[Pick a provisional recommendation and justify it in the venue's terms.]
- Recommendation: [reject | weak reject | borderline | weak accept | accept]
- Rationale: [2-3 sentences. Lead with what drives the score - the single biggest
  reason up or down - then the secondary factors. The rationale must follow from the
  weaknesses above, not from overall vibe.]
- What would move it up one notch: [the single most decision-relevant fix.]

## Confidence
[How sure are you of this assessment, and why.]
- Level: [low | medium | high]
- Basis: [familiarity with the subarea, how carefully you checked the proofs / code /
  numbers, what you did not verify. Low confidence on a key claim is itself a signal
  to add detail so a real reviewer is not left guessing.]

## Desk-reject gate (binary, all must pass)
[Mechanical and fatal if missed. Check before anything above matters.]
- [ ] Scope fits the venue's call.
- [ ] Within page / format limits.
- [ ] Anonymized: no self-citation tells, author-identifying phrasing, or non-anon links.
- [ ] Required sections present (limitations, ethics / broader impact as the venue requires).
- [ ] Reproducibility / responsible-research checklist filled honestly.

## Heuristic-defusal notes (internal - do not put in the paper)
[List the unfair-but-common reviewer reactions this paper might trigger, and one
line each on how the framing already answers them. A criticism that could apply to
ANY paper ("great at A, but what about B?") is not legitimate - do not pad the paper
defending every extension; defend only the choices load-bearing for your claims.]
- "Obvious in hindsight": [how the intro shows the prior expectation was different.]
- "Too simple": [why simplicity is the contribution, not a deficiency.]
- "Too narrow": [why the scope is a deliberate, well-motivated choice.]
- "Doesn't beat SOTA": [why the comparison is fair and what it actually shows.]

## Rebuttal-readiness map
[Anticipate the top 3-5 likely concerns, prioritized. Rebuttals are length-limited;
only the most important points land. Pre-draft a tight, evidence-backed response for
each, leading with the strongest result and citing it exactly.]
- Concern: [likely reviewer point] | Response: [1-2 sentences, cite the exact result] | Priority: [high / med]
- Concern: [...] | Response: [...] | Priority: [...]
- Concern: [...] | Response: [...] | Priority: [...]

## How to use
- Read `./.research/memory/constitution.md` and `./.research/claims.md` first - the
  review is only honest if it is checked against the actual claim-evidence ledger.
- Be paper-type aware: a benchmark paper adds checks (data construction transparency,
  inter-annotator agreement, bias / coverage, baseline results, maintenance plan); an
  attack / defense paper adds threat-model and dual-use checks. Pull the relevant
  `templates/paper/<type>.md` rubric into the weaknesses pass.
- Acknowledged limitations are not weaknesses unless they invalidate a core claim.
  Candor removes a reviewer's ammunition; a hidden flaw invites a harsher finding.
- Turn every finding into an action: fix the draft, rescope a claim, add an
  eval, or write the pre-emption into the text. A review you do not act on is
  wasted.

---
Next: `/research.rebuttal` (pre-draft responses) or back to `/research.paper` to fix what this surfaced.
