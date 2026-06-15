# speckit-research — design

## Vision

Writing a research paper is a long-lived, multi-stage process with the same failure modes as building software: vague problem statements, untracked assumptions, claims that drift from evidence, and rework caused by skipping steps. **Spec-Driven Development** addresses these in code by making intent explicit before execution. speckit-research applies the same discipline to papers.

It is a Claude Code toolkit: a set of slash commands plus Markdown templates and a default research "constitution". Each command turns one fuzzy stage of paper writing - idea, related work, plan, experiments, drafting, rebuttal - into a concrete, reviewable artifact on disk. The artifacts form a chain, so later stages inherit the decisions made earlier instead of re-deriving them, and a claim-to-evidence matrix keeps the eventual paper honest.

Simplicity is the top priority: Markdown in, Markdown out, no runtime.

## Spec-kit → research mapping

speckit-research mirrors the spec-kit pipeline (constitution → spec → plan → tasks → implement), remapped to research stages, then extends it with stages unique to academic work.

| speckit-research stage | spec-kit analogue | What it maps to |
|---|---|---|
| `constitution` | constitution | Research quality principles, writing voice, and venue norms that govern every later stage. |
| `idea` | specify | The "spec" of the paper: problem, motivation (NABC), gap, measurable contributions, testable research questions, venue, paper type. |
| `relatedwork` | (specify, positioning) | Survey of prior work that positions the contribution and names the closest baselines. |
| `plan` | plan | Methodology, baselines, datasets, metrics, threat model, and evaluation design. |
| `experiment` | tasks | The plan broken into trackable experiments, kept in sync with a claim-evidence matrix. |
| `paper` | implement | Section-by-section drafting where every claim traces back to evidence. |
| `analyze` | analyze | Read-only cross-artifact consistency and review-readiness audit. |
| `rebuttal` | — (research extension) | Evidence-backed response to reviewer comments, fitted to the venue limit. |
| `review` | — (research extension) | A fair, specific peer review of someone else's paper. |
| `proposal` | — (research extension) | The idea + plan retargeted as a proposal or fellowship pitch. |
| `ae` | — (research extension) | Artifact-evaluation package: reproducibility checklist, README, badge plan, archival link. |

## Commands

All commands are invoked as `/research.<name>` in Claude Code.

- `/research.constitution` — Establish or update the research constitution (quality principles, writing voice, venue norms).
- `/research.idea` — Turn a rough idea into a sharp, falsifiable `idea.md` (NABC, gap, measurable contributions, testable RQs, venue + paper-type).
- `/research.relatedwork` — Survey prior work and position the contribution against the closest baselines.
- `/research.plan` — Produce a paper-type-aware plan (methodology, baselines, datasets, metrics, threat model, evaluation design).
- `/research.experiment` — Break the plan into trackable experiments and keep the claim-evidence matrix current.
- `/research.paper` — Draft paper sections, paper-type aware, with every claim traceable to `claims.md`.
- `/research.analyze` — Read-only cross-artifact consistency and review-readiness audit; outputs a prioritized gap report.
- `/research.rebuttal` — Draft a prioritized, evidence-backed rebuttal to reviewer comments, fitted to the venue word limit.
- `/research.review` — Write a fair, specific, actionable peer review of another author's paper.
- `/research.proposal` — Turn the idea and plan into a proposal or fellowship pitch (NABC + Heilmeier lenses, audience-aware).
- `/research.ae` — Prepare an artifact-evaluation submission (reproducibility checklist, artifact README, badge plan, archival link).

## Working-directory model

Every command reads and writes under `./.research/` in the user's own paper repo. Nothing lives outside the project; the directory is portable and version-controllable alongside the paper.

```
.research/
  memory/constitution.md   research principles + writing voice
  idea.md                  problem, motivation (NABC), gap, contributions, RQs, venue, paper-type
  related-work.md
  plan.md                  methodology, baselines, datasets, metrics, threat model
  claims.md                claim ↔ evidence matrix (kept by experiment + analyze)
  experiments/             one file per experiment + index.md
  paper/                   section-by-section drafts
  review/  rebuttal/  proposal/  ae/   outputs of those commands
```

Command contract:

1. Read `./.research/memory/constitution.md` if it exists (skip silently otherwise).
2. Read its upstream artifacts (e.g. `plan` reads `idea.md`; `paper` reads `plan.md` + `claims.md`).
3. Take user input via `$ARGUMENTS`.
4. Produce or update only its own artifact(s); end by reporting the path(s) and a one-line `Next: /research.<x>`.
5. Be paper-type aware where relevant (measurement / attack / defense / benchmark) via `templates/paper/<type>.md`.

Commands `mkdir -p` as needed and never overwrite user content without saying so.

## Pipeline order

```
constitution → idea → relatedwork → plan → experiment → paper → analyze
            (+ rebuttal, review, proposal, ae as needed)
```

## Form factor

Pure Claude Code commands. Each command is a Markdown file at `commands/research.<name>.md` with minimal YAML frontmatter (`description`, optional `argument-hint`) and a prompt body that reads the user's free text from `$ARGUMENTS`. `install.sh` (POSIX sh, idempotent, prints what it does) copies them into `~/.claude/commands/`. Templates and the default constitution ship as plain Markdown.

There is no Python CLI, no daemon, no build step. The model does the work; the files are the interface.

## Scope (v1)

Full paper lifecycle: from a rough idea through related work, planning, experiments, drafting, and the self-audit, plus the surrounding academic tasks of rebuttal, peer review, proposal/fellowship writing, and artifact evaluation. Paper-type awareness covers measurement, attack, defense, and benchmark papers.

## Non-goals

- No Python CLI or any other CLI - commands run inside Claude Code.
- No extensions, hooks, or plugin machinery.
- No daemon, server, or hosted state.
- No speculative abstractions. If a feature is not needed for the lifecycle above, it is out.

## Open-source and privacy stance

- **License**: MIT. The toolkit is public and meant for anyone writing research papers, not a single author.
- **Distilled, not copied**: all shipped guidance is original and generalizable. The templates and constitution capture transferable principles of good research writing - they never carry verbatim sentences, personal drafts, unpublished analyses, advisor-attributed style notes, person names, or other identifying details from any source material.
- **User content stays local**: everything a user generates lives in their own `./.research/` directory; the toolkit defines structure and prompts, not a repository of anyone's work.
