---
description: De-risk the core idea with one small, cheap probe before committing to the full study; write .research/feasibility.md with a GO / NO-GO / PIVOT verdict.
argument-hint: optional steering (e.g. "5 examples is enough", "use the toy dataset", "just check the prototype compiles")
---

## User input

The user request arrives via the $ARGUMENTS placeholder. Treat it as steering on how small the probe can be (sample size, substrate, time budget), not as the probe itself.

## What this phase is

A **single cheap probe that asks "does the core idea survive first contact with reality?"** — run *before* the full eval plan exists, so a dead idea dies here instead of after weeks of work. It is deliberately under-powered: a handful of cases, a toy substrate, a throwaway script. It does not prove the contribution; it only buys the right to keep going. The output is one honest finding plus a **GO / NO-GO / PIVOT** decision. A NO-GO or PIVOT routes back to `/research.proposal` to reshape the idea; only a GO proceeds to `/research.plan`.

It is a self-contained **plan → do → decide**: a short *Probe plan* (a few throwaway tasks), the finding, and the verdict — all in `feasibility.md`. Those probe tasks are deliberately separate from the rigorous evaluation design in `plan.md` / `tasks.md`: they inform GO/NO-GO, not the paper's claims.

## Steps

1. **Read context.**
   - Read `./.research/memory/constitution.md` if present (skip silently otherwise) and honor its principles and voice.
   - Read `./.research/proposal.md` (required upstream). If missing, stop and tell the user to run `/research.proposal` first. Pull the one-sentence thesis, the gap, the core mechanism/claim, and the paper type.
   - Read `./.research/related-work.md` if it exists, to confirm the probe targets the *specific* gap no prior work covers (do not re-validate something already established).

2. **Name the single riskiest assumption.** From the thesis, extract the one belief that, if false, kills the paper — the load-bearing assumption the whole contribution rests on. The probe tests *this one thing*, not the full contribution. State it as a sentence that could be proven wrong.

3. **Design the minimal probe, paper-type aware.** Pull the relevant dimensions from `.research/templates/paper/<type>.md` if present, then pick the matching probe:
   - **attack / technique** — a **minimal validation eval**: the smallest end-to-end run that shows the core mechanism *works at all* (e.g. one exploit fires on one target, one method beats trivial baseline on a toy input). Does the idea function outside the slides?
   - **defense** — a **throwaway prototype**: is the defense *implementable* with reasonable effort, does it *stop the threat* on a single concrete attack instance, and what is the *rough cost* (overhead / false positives) order-of-magnitude?
   - **measurement** — **motivating cases found in the wild**: surface a few real instances of the phenomenon (real URLs, packages, CVEs, accounts) *before* committing to the data-driven study. If you cannot find a handful by hand, the population may not exist.
   - **benchmark** — **a few hand-built task instances + a baseline sanity check**: author 3-5 instances by hand, run one off-the-shelf baseline, and confirm the task is solvable-but-not-trivial (baseline neither 0% nor 100%) and that scoring works.
   - **systematization (SoK)** — **a draft taxonomy on a sample of papers**: apply a candidate taxonomy to ~5-10 papers and check that the axes actually separate them (every paper lands somewhere, the cells are not all empty or all one bucket).

4. **Lay out the Probe plan (the feasibility tasks).** Break the probe into a short checklist of 3-5 concrete, throwaway steps you will actually do or run. Keep them cheap — the smallest sample, the toiest substrate, the shortest time that still gives a real signal; honor any budget in `$ARGUMENTS`; if the plan starts to look like the full study, shrink it. These tasks live in `feasibility.md` and stay separate from the study's real queue — they inform GO/NO-GO, not the paper's claims (rigor is `/research.plan` → `/research.tasks` → `/research.implement`).

5. **Work the plan — run it inline, then fill the blanks.** Actually execute each step you can: write and run the throwaway script, pull the real cases, apply the draft taxonomy. Any throwaway probe code lives in `./feasibility/` at the project root, not in `.research/` (which holds only the `feasibility.md` doc). Only fall back to *specifying* a step for the user when you genuinely cannot reach it (system access, a long run, a human judgment call). **If `feasibility.md` already has a Probe plan the user wrote or edited, treat it as the spec** — execute it as written; do not re-plan or rewrite it. Record what each step revealed including the inconvenient parts: what worked, what surprised you, what assumption cracked. A probe that exposes a fatal flaw is a *success* of this phase, not a failure. Do not launder a bad result into a hopeful one.

6. **Decide: GO / NO-GO / PIVOT.** Map the finding to exactly one verdict:
   - **GO** — the riskiest assumption held; the core idea survives. Proceed to `/research.plan`.
   - **NO-GO** — the assumption is false and no nearby reframing saves it. Stop and route back to `/research.proposal` to find a different problem.
   - **PIVOT** — the assumption is false *as stated*, but the probe revealed a sharper or adjacent idea that does hold. State the new direction in one sentence and route back to `/research.proposal` to re-spec it.
   State the single piece of evidence driving the verdict; a verdict with no evidence behind it is not yet a decision. Also state in one line **what the probe establishes** — a *feasibility-level* claim (e.g. "the core mechanism fires on real targets"). It justifies proceeding; it is NOT a paper claim and never enters `claims.md` — the implement stage re-establishes it rigorously.

## Validate (short checklist)

- The probe tests the one riskiest assumption, not the whole contribution.
- The probe type matches the paper type (validation / prototype / wild cases / hand-built instances / draft taxonomy).
- It is genuinely small and cheap — a reader agrees it is a probe, not the study.
- The Probe plan is a short checklist of throwaway steps, kept in `feasibility.md` (not in `tasks.md`).
- The finding records the inconvenient result, not a sanitized one.
- The verdict is exactly one of GO / NO-GO / PIVOT, with a named piece of evidence behind it.
- "What this establishes" is stated as a feasibility-level claim, kept out of `claims.md`.
- On a re-run, the user's edited assumption/design/Probe plan were preserved; only the blanks were filled.
- A NO-GO/PIVOT names what to change and points back to `/research.proposal`.

## Completion

Write/update `./.research/feasibility.md`, starting from `.research/templates/feasibility-template.md`, creating `./.research/` as needed. **On a re-run, preserve every section the user has written (assumption, probe design, Probe plan) and fill only the blanks — Finding, what-this-establishes, Verdict — from the executed plan; never overwrite their text.** Report the path and the verdict. Then end with: `Next: /research.plan` on a GO, or `Next: /research.proposal` to reshape the idea on a NO-GO / PIVOT.
