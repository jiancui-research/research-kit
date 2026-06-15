---
description: Prepare an artifact-evaluation submission (reproducibility checklist, artifact README, badge plan, permanent archival link).
argument-hint: optional — venue (e.g. usenix, acm), badge targets, or notes about what the artifact contains
---

## User input
The user request arrives via the $ARGUMENTS placeholder. Treat it as venue hints (USENIX / ACM / other), which badges to target, and what the artifact actually contains (code, data, models, proofs).

## Steps
1. Read `./.research/memory/constitution.md` if present. Read upstream artifacts when available: `./.research/claims.md` (which results need to be reproducible), `./.research/plan.md` (datasets, baselines, hardware, hyperparameters), and `./.research/experiments/` (concrete commands and configs).
2. Start from `templates/ae-checklist.md`. Work through it venue-agnostically; apply the venue-specific notes below only where $ARGUMENTS names a venue.
3. Map the paper's headline claims to artifact components: for each claim in `claims.md`, identify the script/dataset/config that regenerates its result, and flag any claim with no runnable backing as a reproducibility gap.
4. Pick a badge plan and be explicit about what each tier requires:
   - **Available** — artifact is publicly archived at a permanent location (see step 5). Lowest bar; no functionality review.
   - **Functional** — artifact is documented, complete, and runs (it does what the paper says), but reviewers need not reproduce the exact paper numbers.
   - **Reproduced / Results Reproduced** — reviewers regenerate the paper's key results independently. Requires per-claim commands, expected outputs, and tolerances.
5. Plan the permanent archival link: deposit a versioned snapshot in an archival service that issues a DOI (e.g. Zenodo, figshare, or an institutional repository). A bare GitHub URL is NOT permanent — link the DOI in the camera-ready, and keep GitHub only as the development mirror. Note any GitHub↔Zenodo release automation if used.
6. Write the artifact README and the reproducibility checklist into `./.research/ae/` (see outputs). Never overwrite existing user content there without saying so.

## Outputs (under `./.research/ae/`)
- `README.md` — the artifact's top-level guide: what it is, claims it supports, directory layout, hardware/OS/software requirements with exact versions, setup/install steps, a smoke test, and one runnable block per reproducible claim with expected output and runtime.
- `reproducibility-checklist.md` — the filled checklist from the template (availability, license, dependencies pinned, data access + licenses, seeds/configs, hardware, est. compute/time, known nondeterminism).
- `badge-plan.md` — target badges, the evidence each requires, the DOI/archival plan, and any remaining gaps to close before submission.

## Validate
- Every headline claim either has a reproduce command + expected output, or is explicitly listed as a known gap with a reason.
- A clean-machine reader could install and run the smoke test from the README alone (no missing step, no implicit local state).
- All dependencies, datasets, and the artifact itself have a stated license and access path; nothing requires private credentials without a documented alternative.
- The permanent link is a DOI-bearing archive, not just a repo URL, and matches the version described in the paper.

## Venue notes (apply only if named)
- **USENIX Security / OSDI / NSDI**: badges are Available, Functional, Reproduced. "Available" needs a stable, publicly accessible archive; cite the permanent link in the camera-ready.
- **ACM (CCS, SIGCOMM, etc.)**: badges are Artifacts Available, Artifacts Evaluated — Functional, Artifacts Evaluated — Reusable, and Results Reproduced. "Reusable" is a higher bar than "Functional": expect clean docs, modularity, and adaptability beyond a single run.
- Other venues: keep the three-tier mental model (archived / runs / reproduces) and rename to match the venue's badge labels.

## Completion
Report the paths written under `./.research/ae/`. Next: `/research.review`.
