# research-kit — design (v0.3.0)

## Vision

Writing a research paper is a long-lived, multi-stage process with the same failure modes as building software: vague problem statements, untracked assumptions, claims that drift from evidence, and rework caused by skipping steps. **Spec-Driven Development** addresses these in code by making intent explicit before execution. research-kit applies the same discipline to papers.

It is an agent-agnostic toolkit: a set of slash commands plus Markdown templates and a default research "constitution", installable for Claude Code, Codex CLI, or GitHub Copilot CLI. Each command turns one fuzzy stage of paper writing - proposal, related work, feasibility, tasks, experiments, drafting, rebuttal - into a concrete, reviewable artifact on disk. The artifacts form a chain, so later stages inherit the decisions made earlier instead of re-deriving them, and a claim-to-evidence matrix keeps the eventual paper honest.

Simplicity is the top priority: Markdown in, Markdown out, no runtime.

For the full pipeline diagram and the input/output of every command, see [workflow.md](workflow.md).

## Spec-kit → research mapping

research-kit mirrors the spec-kit pipeline (constitution → specify → plan → tasks → implement), remapped to research stages, then extends it with stages unique to academic work. The idea is folded into `proposal` (the pipeline entry point) and the old standalone plan is folded into `tasks`.

| research-kit stage | spec-kit analogue | What it maps to |
|---|---|---|
| `constitution` | constitution | Research quality principles, writing voice, and venue norms that govern every later stage. |
| `proposal` | specify | The "spec" of the paper and the pipeline entry point: problem, motivation (NABC), gap, measurable contributions, testable research questions, approach, venue, paper type. The raw idea is the input; the idea is folded in here. |
| `relatedwork` | (specify, positioning) | Survey of prior work that positions the contribution and names the closest baselines. |
| `feasibility` | (de-risk gate) | A GO/NO-GO/PIVOT gate that de-risks the result before committing to the full build; a no-go or pivot points back to `proposal`. |
| `tasks` | plan + tasks | Three parallel plans: the design/build plan (`tasks/design.md`), the experiment-evaluation plan (`tasks/experiment.md`), and the paper-section plan (`tasks/paper.md`). The old planning step is folded in here. |
| `design` | implement | Builds the system as actual code (in the project's `./design/` folder) from `tasks/design.md`. Paper-type aware; skipped for measurement / SoK. |
| `experiment` | implement (evaluation) | Trackable experiments that **evaluate** the built system, kept in sync with the claim-evidence matrix; writes verdicts to `claims.md`. |
| `paper` | implement (writing) | Section-by-section drafting (human-led) where every claim traces back to evidence; the System Design section is sourced from `tasks/design.md`. |
| `analyze` | analyze | Read-only cross-artifact consistency + review-readiness audit, AND the **sync checker** across the design/experiment/paper lanes (detects drift, routes the re-run). |
| `review` | — (research extension) | A self-review panel that routes findings and loops until no high-severity findings remain. |
| `rebuttal` | — (research extension) | Evidence-backed response to reviewer comments, fitted to the venue limit. |
| `ae` | — (research extension) | Artifact-evaluation package: reproducibility checklist, README, badge plan, archival link. |

## Commands

All commands are invoked as `/research.<name>` (in Copilot CLI, as the `research.<name>` custom agent).

- `/research.init` — One-time per paper repo: copy the bundled templates into `.research/templates/` so commands can load them.
- `/research.constitution` — Establish or update the research constitution (quality principles, writing voice, venue norms).
- `/research.proposal` — Pipeline entry point: turn a raw idea into a sharp, falsifiable `proposal.md` (NABC, gap, measurable contributions, testable RQs, approach, venue + paper-type).
- `/research.relatedwork` — Survey prior work and position the contribution against the closest baselines.
- `/research.feasibility` — De-risk the result with a quick check and emit a GO/NO-GO/PIVOT verdict; a no-go or pivot routes back to `/research.proposal`.
- `/research.tasks` — Produce the three plans (paper-type aware): the design/build plan (`tasks/design.md`), the experiment-evaluation plan (`tasks/experiment.md`), and the paper-section plan (`tasks/paper.md`).
- `/research.design` — Build lane (the spec-kit `implement` analogue): implement the system from `tasks/design.md` into actual code in the project's `./design/` folder (a sibling of `.research/`). Skipped for measurement / SoK.
- `/research.experiment` — Run trackable experiments that evaluate the built system and keep the claim-evidence matrix (`claims.md`) current, writing verdicts back.
- `/research.paper` — Outline or critique paper sections (human-led), paper-type aware, with every claim traceable to `claims.md`; the System Design section is sourced from `tasks/design.md`.
- `/research.analyze` — Read-only cross-artifact consistency + review-readiness audit, and the sync checker across the design/experiment/paper lanes; routes findings and stale-lane re-runs to the owning commands.
- `/research.review` — Simulate a reviewer panel, write mock reviews + scores, route findings, and loop until no new high-severity findings.
- `/research.rebuttal` — Draft a prioritized, evidence-backed rebuttal to reviewer comments, fitted to the venue word limit.
- `/research.ae` — Prepare an artifact-evaluation submission (reproducibility checklist, artifact README, badge plan, archival link).

## Working-directory model

The project is one repo (under `~/Projects`, outside the vault). research-kit's **tracking docs** all live under `./.research/`; the actual **work products** (code, data, paper source) live in sibling root folders. The split is deliberate: `.research/` is the control plane (what we decided + what we're tracking), the root folders are the work itself.

```
<project>/                 one repo under ~/Projects, outside the vault
  .research/               ALL research-kit tracking docs:
    memory/constitution.md   research principles + writing voice
    templates/               skeletons + craft guides (copied by /research.init)
    proposal.md              problem, motivation (NABC), gap, contributions, RQs, approach, venue, paper-type
    related-work.md
    feasibility.md           de-risk result + GO/NO-GO/PIVOT
    tasks/design.md          system architecture + project layout + build task list (build-papers)
    tasks/experiment.md      experiment-design header + experiment task list (evaluation)
    tasks/paper.md           paper-section task list (READY vs BLOCKED-on-claim)
    claims.md                claim ↔ evidence matrix (written by experiment; read by paper/analyze/review)
    experiments/             one file per experiment + index.md (tracking)
    paper/                   section-by-section outlines/drafts (tracking)
    analyze-report.md        consistency + sync + desk-reject report
    review/round-N.md  rebuttal/  ae/   outputs of those commands
  feasibility/             throwaway probe code
  design/                  THE SYSTEM CODE (built by /research.design)
  experiment/              evaluation scripts, data, results
  paper/                   the actual paper source (LaTeX, figures)
```

Command contract:

1. Read `./.research/memory/constitution.md` if it exists (skip silently otherwise).
2. Read its upstream artifacts (e.g. `tasks` reads `proposal.md` + `feasibility.md`; `design` reads `tasks/design.md`; `paper` reads `tasks/paper.md` + `tasks/design.md` + `claims.md`).
3. Take user input via `$ARGUMENTS`.
4. Produce or update only its own artifact(s) — the design lane's code is the one output written outside `.research/` (in `./design/`); end by reporting the path(s) and a one-line `Next: /research.<x>`.
5. Be paper-type aware where relevant (measurement / attack / defense / benchmark / systematization (SoK)) via `.research/templates/paper/<type>.md` (copied from the bundle by `/research.init`).

Commands `mkdir -p` as needed and never overwrite user content without saying so.

## Pipeline order

```
constitution → proposal → relatedwork → feasibility → tasks → (design ∥ experiment ∥ paper) → analyze → review (loop)
            (+ rebuttal post-submission, ae once results exist, init for setup)
```

After a GO, `tasks` fans out into three parallel lanes that co-evolve: `design` builds the system as code, `experiment` evaluates it (writing verdicts to `claims.md`), and `paper` writes sections (reading `claims.md` and tagging any unbacked claim `[UNVERIFIED]`). They communicate only through documents they read - `tasks/design.md` and `claims.md` - never by writing into each other. `feasibility` is a GO/NO-GO gate (a no-go or pivot routes back to `proposal`). `analyze` is the sync checker that detects lane drift and routes the re-run (change `design` → it tells you to re-run `experiment` + `paper`), and `review` loops back into the fix-commands until no new high-severity findings remain. The design lane is paper-type aware: present for build-papers, skipped for measurement / SoK.

## Form factor

Pure agent slash commands — no runtime of its own. Each command is a Markdown file at `commands/research.<name>.md` with minimal YAML frontmatter (`description`, optional `argument-hint`) and a prompt body that reads the user's free text from `$ARGUMENTS`. `install.sh` (POSIX sh, idempotent, prints what it does) installs them for one or more agents:

- **Claude Code** — copied (or symlinked) into `~/.claude/commands/`.
- **Codex CLI** — copied (or symlinked) into `~/.codex/prompts/` (honoring `$CODEX_HOME`); same `$ARGUMENTS` form.
- **GitHub Copilot CLI** — transformed into custom agents in `~/.copilot/agents/research.<name>.agent.md`. Copilot CLI has no parameterized slash commands, so each stage becomes an agent (selected via `/agent`) with a generated adapter note mapping `$ARGUMENTS` → the user's message and `Next: /research.<x>` → switching agents. The command body is otherwise verbatim, so the pipeline is authored once.

The default (no flag) installs for Claude Code, preserving the original behavior; `--all` covers every agent. Templates ship as plain Markdown; `install.sh` stages them to `~/.research-kit/` (override with `RESEARCH_KIT_HOME`) and `/research.init` copies them into a paper repo's `.research/templates/`. The default constitution is embedded in `/research.constitution`.

For Claude Code there is also a zero-script path: the repo doubles as a **plugin marketplace**. `.claude-plugin/marketplace.json` lists a single plugin whose source is the repo root, and `.claude-plugin/plugin.json` is its manifest; the existing `commands/` directory is the plugin's command set with no file movement. Users run `/plugin marketplace add jiancui-research/research-kit` then `/plugin install research-kit@research-kit`, which namespaces the stages as `/research-kit:research.<name>`. In this mode the plugin bundle (including `templates/`) is copied to Claude's cache, so `/research.init` reads templates from `${CLAUDE_PLUGIN_ROOT}/templates`, falling back to the `install.sh` staging dir otherwise. This is packaging only — no hooks, MCP servers, or runtime are added.

There is no Python CLI, no daemon, no build step. The model does the work; the files are the interface.

## Scope (v1)

Full paper lifecycle: from a raw idea (via the proposal entry point) through related work, the feasibility gate, task planning, experiments, drafting, the self-audit, and the self-review loop, plus the surrounding academic tasks of rebuttal and artifact evaluation. Paper-type awareness covers measurement, attack, defense, benchmark, and systematization (SoK) papers, with cross-cutting craft guides for abstract/intro, figures/tables, and venue norms.

## Non-goals

- No Python CLI or any other CLI - commands run inside the AI coding agent (Claude Code, Codex CLI, or Copilot CLI).
- No hooks, MCP servers, or runtime machinery. The optional Claude Code plugin packaging (`.claude-plugin/`) is just a manifest around the same command files - no event handlers or background processes.
- No daemon, server, or hosted state.
- No speculative abstractions. If a feature is not needed for the lifecycle above, it is out.

## Open-source and privacy stance

- **License**: MIT. The toolkit is public and meant for anyone writing research papers, not a single author.
- **Distilled, not copied**: all shipped guidance is original and generalizable. The templates and constitution capture transferable principles of good research writing - they never carry verbatim sentences, personal drafts, unpublished analyses, advisor-attributed style notes, person names, or other identifying details from any source material.
- **User content stays local**: everything a user generates lives in their own `./.research/` directory; the toolkit defines structure and prompts, not a repository of anyone's work.
