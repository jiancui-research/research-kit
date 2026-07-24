# research-kit — design (v0.3.0)

## Vision

Writing a research paper is a long-lived, multi-stage process with the same failure modes as building software: vague problem statements, untracked assumptions, claims that drift from evidence, and rework caused by skipping steps. **Spec-Driven Development** addresses these in code by making intent explicit before execution. research-kit applies the same discipline to papers.

It is an agent-agnostic toolkit: a set of slash commands plus Markdown templates and a default research "constitution", installable for Claude Code, Codex CLI, GitHub Copilot CLI, or Oh My Pi (OMP). Each command turns one fuzzy stage of paper writing - proposal, related work, feasibility, tasks, evals, drafting, rebuttal - into a concrete, reviewable artifact on disk. The artifacts form a chain, so later stages inherit the decisions made earlier instead of re-deriving them, and a claim-to-evidence matrix keeps the eventual paper honest.

Simplicity is the top priority: Markdown in, Markdown out, no runtime.

For the full pipeline diagram and the input/output of every command, see [workflow.md](workflow.md).

## Spec-kit → research mapping

research-kit mirrors the spec-kit pipeline (constitution → specify → plan → tasks → implement) stage for stage, then extends it with stages unique to academic work. The idea is folded into `proposal` (the pipeline entry point); `plan`, `tasks`, and `implement` map 1:1 to their spec-kit namesakes, with one deliberate exception: the human-led `paper` lane stays outside the implement queue.

| research-kit stage | spec-kit analogue | What it maps to |
|---|---|---|
| `constitution` | constitution | Research quality principles, writing voice, and venue norms that govern every later stage. |
| `proposal` | specify | The "spec" of the paper and the pipeline entry point: problem, motivation (NABC), gap, measurable contributions, testable research questions, approach, venue, paper type. The raw idea is the input; the idea is folded in here. |
| `relatedwork` | (specify, positioning) | Survey of prior work that positions the contribution and names the closest baselines. |
| `feasibility` | (de-risk gate) | A GO/NO-GO/PIVOT gate that de-risks the result before committing to the full build; a no-go or pivot points back to `proposal`. |
| `plan` | plan | The study's technical design (`plan.md`): architecture, evaluation design, key decisions with rejected alternatives, project layout (declares the code folder). Stable; no task list. |
| `tasks` | tasks | The single work queue (`tasks.md`): Setup / Build / Eval / Paper / Polish sections, continuous T-ids, `[P]` parallel markers, claim links. Expected to churn; re-runs refine and preserve states. |
| `implement` | implement | Works the queue: Build tasks produce code in the folder `plan.md` declares (default `./src/`, legacy `./design/`); Eval tasks run and write verdicts to `claims.md`. Skips `[HUMAN]` Paper tasks. |
| `paper` | — (kept human-led) | Section-by-section outlining/critique (human-led, never ghostwrites) where every claim traces back to evidence; the System Design section is sourced from `plan.md`. Runs in parallel with `implement`. |
| `analyze` | analyze | Read-only cross-artifact consistency + review-readiness audit, AND the **sync checker** across plan, tasks, code, evidence, and manuscript (detects drift, routes the re-run). |
| `review` | — (research extension) | A self-review panel that reads **only the paper** (like a real reviewer), reports findings + scores with a suggested fix command each, and loops until no high-severity findings remain. Writes only its round file. |
| `rebuttal` | — (research extension) | Evidence-backed response to reviewer comments, fitted to the venue limit. |
| `ae` | — (research extension) | Artifact-evaluation package: reproducibility checklist, README, badge plan, archival link. |

## Commands

All commands are invoked as `/research.<name>` (in Copilot CLI, as the `research.<name>` custom agent).

- `/research.init` — One-time per paper repo: copy the bundled templates into `.research/templates/` so commands can load them.
- `/research.constitution` — Establish or update the research constitution (quality principles, writing voice, venue norms).
- `/research.proposal` — Pipeline entry point: turn a raw idea into `proposal.md`, a readable 1-3 page argument (falsifiable thesis, argued gap, pre-committed validation plan, venue + paper-type).
- `/research.relatedwork` — Survey prior work and position the contribution against the closest baselines.
- `/research.feasibility` — De-risk the result with a quick check and emit a GO/NO-GO/PIVOT verdict; a no-go or pivot routes back to `/research.proposal`.
- `/research.plan` — The study's technical design into `plan.md` (architecture, evaluation design, decisions, layout incl. the code-folder declaration). Stable; tasks derive from it.
- `/research.tasks` — Derive the single work queue `tasks.md` from `plan.md` (Setup/Build/Eval/Paper/Polish, T-ids, claim links); re-runs refine and preserve checkbox states.
- `/research.implement` — Work the queue: build into the declared code folder, run evals and keep `claims.md` current, tick checkboxes; skips `[HUMAN]` Paper tasks (those belong to `/research.paper`).
- `/research.paper` — Outline or critique paper sections (human-led), paper-type aware, with every claim traceable to `claims.md`; the System Design section is sourced from `plan.md`.
- `/research.analyze` — Read-only cross-artifact consistency + review-readiness audit, and the sync checker across plan, tasks, code, evidence, and manuscript; routes findings and re-runs to the owning commands.
- `/research.review` — Simulate a reviewer panel reading **only the paper**; report mock reviews + scores with a suggested fix command per finding (writes only `review/round-N.md`, never another artifact), and loop until clean.
- `/research.rebuttal` — Draft a prioritized, evidence-backed rebuttal to reviewer comments, fitted to the venue word limit.
- `/research.ae` — Prepare an artifact-evaluation submission (reproducibility checklist, artifact README, badge plan, archival link).
- `/research.mdreview` — Optional review UI: launch `tools/mdreview.py` (local web server) to read, edit, comment on, and export the repo's markdown; comments land in `./.mdreview/` as sidecar JSON.

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
    plan.md                  study design: architecture + evaluation design + decisions + layout (stable)
    tasks.md                 the single work queue: Setup/Build/Eval/Paper/Polish (churns)
    claims.md                claim ↔ evidence matrix (the shared sync point; written by implement, read by paper/analyze/review)
    analyze-report.md        consistency + sync + desk-reject report
    review/round-N.md  rebuttal/  ae/   outputs of those commands
  feasibility/             throwaway probe code
  src/                     THE SYSTEM CODE (built by /research.implement; folder declared in plan.md - legacy projects use design/)
  eval/                    eval writeups + index + scripts, data, results
  paper/                   outlines + manuscript - or a dedicated sibling repo recorded in .research/paper-repo
```

Command contract:

1. Read `./.research/memory/constitution.md` if it exists (skip silently otherwise).
2. Read its upstream artifacts (e.g. `plan` reads `proposal.md` + `feasibility.md`; `tasks` reads `plan.md`; `implement` reads `plan.md` + `tasks.md`; `paper` reads `tasks.md` + `plan.md` + `claims.md`).
3. Take user input via `$ARGUMENTS`.
4. Produce or update only its own artifact(s) — implement's code and eval outputs are the ones written outside `.research/` (in the declared code folder and `./eval/`); end by reporting the path(s) and a one-line `Next: /research.<x>`.
5. Be paper-type aware where relevant (measurement / attack / defense / benchmark / systematization (SoK)) via `.research/templates/paper/<type>.md` (copied from the bundle by `/research.init`).

Commands `mkdir -p` as needed and never overwrite user content without saying so.

## Pipeline order

```
constitution → proposal → relatedwork → feasibility → plan → tasks → implement (∥ paper) → analyze → review (loop)
            (+ rebuttal post-submission, ae once results exist, init for setup)
```

After a GO, `plan` fixes the study design and `tasks` derives one work queue from it. `implement` works the queue (code into the declared folder, eval verdicts into `claims.md`) while the human-led `paper` lane runs in parallel, reading `claims.md` and tagging any unbacked claim `[UNVERIFIED]` - the two communicate only through documents they read, never by writing into each other. `feasibility` is a GO/NO-GO gate (a no-go or pivot routes back to `proposal`). `analyze` is the sync checker that detects drift among plan, tasks, code, evidence, and manuscript and routes the re-run, and `review` loops back into the fix-commands until no new high-severity findings remain. The Build section is paper-type aware: heavy for build-papers, minimal or absent for measurement / SoK.

## Form factor

Pure agent slash commands — no runtime of its own. Each command is a Markdown file at `commands/research.<name>.md` with minimal YAML frontmatter (`description`, optional `argument-hint`) and a prompt body that reads the user's free text from `$ARGUMENTS`. `install.sh` (POSIX sh, idempotent, prints what it does) installs them for one or more agents:

- **Claude Code** — copied (or symlinked) into `~/.claude/commands/`.
- **Codex CLI** — copied (or symlinked) into `~/.codex/prompts/` (honoring `$CODEX_HOME`); same `$ARGUMENTS` form.
- **GitHub Copilot CLI** — via the script, transformed into custom agents in `~/.copilot/agents/research.<name>.agent.md`, each selected with `/agent`, with a generated adapter note mapping `$ARGUMENTS` → the user's message and `Next: /research.<x>` → switching agents. (Copilot CLI can *also* install the `.claude-plugin` bundle directly from its marketplace — see below — reading `commands/` with no script.) The command body is otherwise verbatim, so the pipeline is authored once.

The default (no flag) installs for Claude Code, preserving the original behavior; `--all` covers every agent. Templates ship as plain Markdown; `install.sh` stages them to `~/.research-kit/` (override with `RESEARCH_KIT_HOME`) and `/research.init` copies them into a paper repo's `.research/templates/`. The default constitution is embedded in `/research.constitution`.

The repo also doubles as a **plugin marketplace**, a zero-script path shared by three agents. `.claude-plugin/marketplace.json` lists a single plugin whose source is the repo root, and `.claude-plugin/plugin.json` is its manifest; the existing `commands/` directory is the plugin's command set with no file movement. **Claude Code:** `/plugin marketplace add jiancui-research/research-kit` then `/plugin install research-kit@research-kit`, namespacing the stages as `/research-kit:research.<name>`. **GitHub Copilot CLI reads the same `.claude-plugin` bundle:** `copilot plugin marketplace add jiancui-research/research-kit` then `copilot plugin install research-kit@research-kit`, exposing the same namespaced `/research-kit:research.<name>` stages (verified against Copilot CLI 1.0.40). **OMP reads the same bundle too:** `/marketplace add jiancui-research/research-kit` then `/marketplace install research-kit@research-kit`; its commands resolve bundled templates and tools through the `installPath` in OMP's installed-plugin registry. In Claude's mode the plugin bundle (including `templates/`) is copied to Claude's cache, so `/research.init` reads templates from `${CLAUDE_PLUGIN_ROOT}/templates`, falling back to the `install.sh` staging dir otherwise. This is packaging only — no hooks, MCP servers, or runtime are added.

There is no Python CLI, no daemon, no build step. The model does the work; the files are the interface.

## Scope (v1)

Full paper lifecycle: from a raw idea (via the proposal entry point) through related work, the feasibility gate, task planning, evals, drafting, the self-audit, and the self-review loop, plus the surrounding academic tasks of rebuttal and artifact evaluation. Paper-type awareness covers measurement, attack, defense, benchmark, and systematization (SoK) papers, with cross-cutting craft guides for abstract/intro, figures/tables, and venue norms.

## Non-goals

- No Python CLI or any other CLI - commands run inside the AI coding agent (Claude Code, Codex CLI, Copilot CLI, or OMP).
- No hooks, MCP servers, or runtime machinery. The optional Claude Code plugin packaging (`.claude-plugin/`) is just a manifest around the same command files - no event handlers or background processes.
- No daemon, server, or hosted state.
- No speculative abstractions. If a feature is not needed for the lifecycle above, it is out.

## Open-source and privacy stance

- **License**: MIT. The toolkit is public and meant for anyone writing research papers, not a single author.
- **Distilled, not copied**: all shipped guidance is original and generalizable. The templates and constitution capture transferable principles of good research writing - they never carry verbatim sentences, personal drafts, unpublished analyses, advisor-attributed style notes, person names, or other identifying details from any source material.
- **User content stays local**: everything a user generates lives in their own `./.research/` directory; the toolkit defines structure and prompts, not a repository of anyone's work.
