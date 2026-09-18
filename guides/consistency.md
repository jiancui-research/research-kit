# Check consistency before finishing

Loaded by `/research.implement` and `/research.write`. This is part of finishing
their work, not a separate stage and never part of `/research.review`.

## Choose the scope

- **After implementation/evaluation:** inspect the changed code or results, the
  relevant plan/tasks/claims, and manuscript passages affected by those changes.
- **After section writing:** inspect the changed claims, terminology, numbers,
  citations, tables, and references against the whole paper and any available
  project evidence. An existing paper does not need a pipeline created retroactively.
- **Explicit `check` request:** audit all available project artifacts (or the scope
  the user names). Do not run experiments or alter the manuscript or queue. The
  report goes in the conversation unless the user asks for a saved report.

## Checks

1. Trace each affected contribution or RQ through claim IDs to evaluations and their
   actual results. Mark missing evidence, pending/partial/refuted claims presented
   as settled, and evidence that no longer tests the current implementation.
2. Compare headline counts, denominators, metrics, datasets, baselines, threat-model
   assumptions, and scope across the relevant artifacts. Evidence supports only the
   conditions tested. A feasibility GO alone does not establish a paper claim.
3. Check plan-to-code agreement and plan-to-task dependencies. A checked task needs
   its stated deliverable and validation. If the design changes, name downstream
   work or manuscript descriptions that are now stale.
4. Check prose for unsupported novelty/guarantee verbs, undefined referents, stale
   terminology after a float changes, missing citations, and related-work claims
   that misstate the source. Test the strongest claimed result against its evidence.
5. For evaluation work, check fair baseline tuning, variability, leakage, confounds,
   and validation of automated judges. For a complete-paper audit, also check venue
   scope, page/format limits, anonymity, required sections, and reproducibility
   details. Name unavailable checks; do not invent rules or demand every possible
   extension. Missing pipeline files in a writing-only project are not failures.

## Report and act within the selected task

Fix inconsistencies within the already authorized work, then check the affected
links again. Report other gaps with severity, file/section location, evidence, and
the next concrete action. Do not silently expand a section revision into a rewrite
of the paper, or change evidence to make it agree with a claim.

- Framing or contribution gap -> `/research.proposal`
- Literature or baseline positioning -> `/research.relatedwork`
- Unresolved feasibility -> `/research.feasibility`
- Study design or task dependencies -> `/research.plan`
- Missing/invalid experiment or implementation -> `/research.implement <task>`
- Paper wording, figures, or references -> `/research.write <section>`

Close with a short consistency status and remaining gaps. For explicit check-only
work, report findings without fixing them. If the paper is ready for an outside
reader, suggest `/research.review`; do not run that stage automatically.
