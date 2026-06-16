# Feasibility probe: [short working title]

> Produced by `/research.feasibility`. Lives at `./.research/feasibility.md`.
> Reads `./.research/proposal.md` (thesis, gap, core mechanism/claim, paper type) and
> `./.research/related-work.md` if present. This is ONE cheap probe run before the full
> study, not the study itself. Fill every bracket. End on exactly one GO / NO-GO / PIVOT
> verdict with a named piece of evidence behind it.

## Riskiest assumption (the one belief that, if false, kills the paper)
[State the single load-bearing assumption the whole contribution rests on, as a sentence
that could be proven wrong. Not the full contribution - the one thing the probe tests.]
- Assumption: [...]
- If this is false: [why the paper does not survive].

## Probe design (minimal, cheap, paper-type aware)
[Pick the probe matching the paper type from `.research/templates/paper/<type>.md`:
attack/technique -> minimal validation run; defense -> throwaway prototype; measurement ->
motivating cases in the wild; benchmark -> a few hand-built instances + baseline sanity
check; systematization (SoK) -> draft taxonomy on ~5-10 sample papers.]
- Paper type: [measurement | attack | defense | benchmark | systematization]
- Probe: [the smallest end-to-end thing that produces real signal].
- Budget / scope: [sample size, substrate, time - honor any steering in $ARGUMENTS].
- Why this is a probe, not the study: [one line a reader would agree with].

## Probe plan (the feasibility tasks)
[3-5 concrete, throwaway steps you will actually do or run. Cheap and disposable; they
inform the verdict below, NOT the paper's claims - kept here, never in `tasks/`.]
- [ ] [step, e.g. "wire a 3-line PoC of the core mechanism"]
- [ ] [step, e.g. "run it on one real target / a toy input"]
- [ ] [step, e.g. "eyeball whether the riskiest assumption held"]

## Finding (honest, including the inconvenient parts)
[Record what actually happened. What worked, what surprised you, what assumption cracked.
A probe that exposes a fatal flaw is a SUCCESS of this phase. Do not sanitize.]
- What happened: [...]
- The inconvenient part: [...]

## Verdict: [GO | NO-GO | PIVOT]
[Exactly one. State the single piece of evidence driving it.]
- Evidence behind the verdict: [...]
- What this establishes (feasibility-level — NOT a paper claim; the full experiment re-establishes it in `claims.md`): [one line, e.g. "the core mechanism fires on real targets"].
- GO -> the riskiest assumption held; proceed to `/research.tasks`.
- NO-GO -> the assumption is false and no nearby reframing saves it; route to `/research.proposal`.
- PIVOT -> false as stated, but the probe revealed a sharper adjacent idea:
  - New direction (one sentence): [...]; route to `/research.proposal` to re-spec.

## Quality checklist
- [ ] The probe tests the one riskiest assumption, not the whole contribution.
- [ ] The probe type matches the paper type.
- [ ] It is genuinely small and cheap - a reader agrees it is a probe, not the study.
- [ ] The Probe plan is a short throwaway checklist kept in `feasibility.md`, not in `tasks/`.
- [ ] The finding records the inconvenient result, not a sanitized one.
- [ ] The verdict is exactly one of GO / NO-GO / PIVOT, with a named piece of evidence.
- [ ] "What this establishes" is a feasibility-level claim, kept out of `claims.md`.
- [ ] A NO-GO / PIVOT names what to change and points back to `/research.proposal`.

---
Next: `/research.tasks` on a GO, or `/research.proposal` to reshape the idea on a NO-GO / PIVOT.
