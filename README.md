# research-kit

Spec-Driven Development for research papers, as slash commands for your AI coding agent — Claude Code, Codex CLI, or GitHub Copilot CLI. Instead of one giant "write my paper" prompt, you get a pipeline of small commands: each reads what came before, takes your input, and writes one artifact under `./.research/`. Just Markdown commands + templates and a default research constitution — no Python CLI, no build step.

## Pipeline

```
constitution → proposal → relatedwork → feasibility → tasks → (design + experiment + paper, in parallel) → analyze → review
```

After feasibility, `tasks` fans out into three parallel lanes that co-evolve: **design** builds the system (code), **experiment** evaluates it, **paper** writes it up. `analyze` is the sync checker that catches drift between them and tells you what to re-run. The design lane is paper-type aware - heavy for systems/defense, skipped for measurement / SoK. Plus auxiliary commands: `rebuttal` (post-submission) and `ae` (artifact evaluation). Run any subset, re-run any stage as your work evolves; commands only touch their own artifacts and never overwrite silently.

📐 **[Workflow diagram + per-command inputs/outputs →](docs/workflow.md)**

## Quickstart

**Claude Code — plugin (recommended, no script):**

```text
/plugin marketplace add jiancui-research/research-kit
/plugin install research-kit@research-kit
```

Plugin stages are namespaced, e.g. `/research-kit:research.proposal …`; update later with `/plugin marketplace update`.

**Any agent — script:**

```sh
./install.sh            # Claude Code (default). Also: --codex, --copilot, --all
```

Then, in your paper repo:

```sh
/research.init                       # once per repo: copy templates into .research/
/research.constitution <focus>       # optional: set writing voice + venue
/research.proposal <your raw idea>   # pipeline entry
/research.relatedwork
/research.feasibility
/research.tasks                      # writes three plans: design, experiment, paper
/research.design                     # build-papers only: implement the system into ~/Projects/<repo>
/research.experiment                 # evaluate the build; runs parallel with paper, synced via claims.md
/research.paper
/research.analyze                    # also a "sync" check: what drifted, what to re-run
/research.review
```

Each command writes its result into `./.research/` and suggests the next one. (Plugin installs prefix every command with `research-kit:`.)

## Commands

| Command | What it does |
| --- | --- |
| `/research.init` | Copy the bundled templates into this paper repo's `.research/templates/` (run once per repo, after `install.sh`). |
| `/research.constitution` | Establish or update the research constitution: quality principles, writing voice, and venue norms. |
| `/research.proposal` | Pipeline entry: turn a raw idea into a sharp, falsifiable proposal — NABC, the gap, measurable contributions, testable RQs, venue and paper type. |
| `/research.relatedwork` | Survey prior work into `related-work.md` and sharpen the proposal's gap and positioning. |
| `/research.feasibility` | De-risk the central result with a quick probe and return a GO / NO-GO / PIVOT verdict before you invest in the full build. |
| `/research.tasks` | Produce three paper-type-aware plans: the design/build plan, the experiment-evaluation plan, and the paper task list (READY vs blocked-on-claim). |
| `/research.design` | Build lane (build-papers only): implement the system from `tasks/design.md` into actual code under `~/Projects/<repo>`, outside the vault. Skipped for measurement / SoK. |
| `/research.experiment` | Run the experiment tasks that evaluate the built system and keep the claim-evidence matrix current. |
| `/research.paper` | Human-led writing: outline a section or critique your draft, every claim traceable to the evidence matrix; System Design sourced from `tasks/design.md`. |
| `/research.analyze` | Read-only cross-artifact audit **and** the sync checker across the design/experiment/paper lanes: flags drift and names the exact re-run. Outputs a prioritized gap report. |
| `/research.review` | Simulate a reviewer panel: mock reviews + scores, route each finding to the command that owns the fix, and loop until clean. |
| `/research.rebuttal` | Draft a prioritized, evidence-backed rebuttal to reviewer comments, fitted to the venue word limit. |
| `/research.ae` | Prepare an artifact-evaluation submission: reproducibility checklist, artifact README, badge plan, archival link. |

## Supported agents

The same pipeline installs for three agents; pick one or more (`--all` for every one; default is Claude Code).

| Agent | Install | How you invoke a stage |
| --- | --- | --- |
| **Claude Code** (plugin) | `/plugin install research-kit@research-kit` | `/research-kit:research.proposal <text>` |
| **Claude Code** (script) | `./install.sh` | `/research.proposal <text>` |
| **Codex CLI** | `./install.sh --codex` | `/research.proposal <text>` |
| **GitHub Copilot CLI** | `./install.sh --copilot` | `/agent` → pick `research.proposal`, then type your input |

- **Copilot** has no parameterized slash commands, so each stage installs as a custom agent (`research.<name>.agent.md`) with a short adapter note; the body is otherwise identical.
- **Self-pruning & overrides.** Re-running `install.sh` removes commands deleted from the bundle. Override destinations with `CLAUDE_COMMANDS_DIR` / `CODEX_PROMPTS_DIR` / `COPILOT_AGENTS_DIR` (or `CODEX_HOME`); `--symlink` links instead of copies; `--uninstall` removes everything.

## Working directory

Everything a paper needs lives under `./.research/` — commit it alongside the paper as the decision record. The one exception is the design lane's **code**, which lives in its own repo under `~/Projects/<repo>` (outside the vault).

```
.research/
  memory/constitution.md   research principles + writing voice
  templates/               skeletons + craft guides (from /research.init)
  proposal.md              problem, NABC, gap, contributions, RQs, venue, paper type
  related-work.md          prior work + positioning
  feasibility.md           de-risk probe + GO / NO-GO / PIVOT
  tasks/design.md          system architecture + repo layout + build tasks (build-papers; → code)
  tasks/experiment.md      experiment design + task list (evaluation)
  tasks/paper.md           paper section tasks (READY vs blocked-on-claim)
  claims.md                claim ↔ evidence matrix
  experiments/             one file per experiment + index.md
  paper/                   section drafts
  analyze-report.md        prioritized gap + sync report
  review/ rebuttal/ ae/    outputs of those commands

~/Projects/<repo>/         the built system (design lane's code) — outside the vault
```

## Customization

`.research/memory/constitution.md` sets the quality bar, writing voice, and venue norms every command reads first — edit it directly or via `/research.constitution`. Several commands are paper-type aware (measurement, attack, defense, benchmark, SoK); the skeletons and craft guides live in `templates/` and are copied in by `/research.init`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep it simple, keep the pipeline consistent, and write original, generalizable guidance.

## Credits & license

Inspired by [GitHub spec-kit](https://github.com/github/spec-kit) (MIT), which brought Spec-Driven Development to software. MIT licensed — see [LICENSE](LICENSE).
