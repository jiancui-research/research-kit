# speckit-research

Spec-Driven Development for research papers, as slash commands for your AI coding agent — Claude Code, Codex CLI, or GitHub Copilot CLI.

Writing a paper is a lot like building software: you start fuzzy, and quality comes from making each step explicit, reviewable, and traceable to evidence. speckit-research borrows that discipline. Instead of one giant "write my paper" prompt, it gives you a pipeline of small, focused commands - each reads what came before, takes your input, and produces one well-scoped artifact under `./.research/` in your paper repo.

It is just slash commands plus Markdown templates and a default research constitution. No Python CLI, no hooks, no build step. Simplicity is the point.

## Pipeline

The commands form an ordered pipeline. Each stage builds on the last:

```
constitution → proposal → relatedwork → feasibility → tasks → (experiment + paper, in parallel) → analyze → review
```

Plus auxiliary commands you reach for when the moment calls for it: `rebuttal` (post-submission) and `ae` (artifact evaluation).

You don't have to run every stage, and you can re-run any command as your work evolves. Commands only touch their own artifacts and tell you before overwriting anything.

## Quickstart

**Claude Code — install as a plugin (recommended, no script):**

```text
# 1. Register the marketplace and install the plugin
/plugin marketplace add jiancui-research/speckit-research
/plugin install speckit-research@speckit-research
```

Plugin stages are namespaced with the plugin name, e.g. `/speckit-research:research.proposal …`.
Update later with `/plugin marketplace update` then re-install.

**Any agent — install with the script:**

```sh
# Installs the commands + stages the bundled templates.
# Default installs for Claude Code. Pick your agent(s) with flags:
./install.sh                     # Claude Code (default)
./install.sh --codex             # Codex CLI
./install.sh --copilot           # GitHub Copilot CLI
./install.sh --all               # all of the above
```

> How you invoke a stage depends on the install method. Via the **plugin** (Claude Code) the
> stages are namespaced: `/speckit-research:research.proposal …`. Via **install.sh** they are plain
> slash commands in **Claude Code** and **Codex CLI** (`/research.proposal …`), and custom agents in
> **Copilot CLI** (pick with `/agent`, e.g. `research.proposal`, then type your input). See
> [Supported agents](#supported-agents) below.

```sh
# 2. In your paper repo, copy the templates in (once per repo)
/research.init

# 3. Set the tone (optional but recommended)
/research.constitution measurement paper for a security venue, plain and precise voice

# 4. Turn your raw idea into a proposal
/research.proposal LLM agents leak secrets through tool-call arguments; measure how often

# 5. Walk the pipeline
/research.relatedwork
/research.feasibility
/research.tasks
/research.experiment   # runs in parallel with paper, synced via claims.md
/research.paper
/research.analyze
/research.review
```

Each command reads your free text after the command name, reads its upstream artifacts, and writes its result into `./.research/`. When it finishes it prints the file path and suggests the next command.

> If you installed via the Claude Code **plugin**, prefix every command with the plugin name,
> e.g. `/speckit-research:research.init` and `/speckit-research:research.proposal …`.

## Commands

All commands are invoked as `/research.<name>` in Claude Code and Codex CLI (or, after a Claude Code plugin install, as `/speckit-research:research.<name>`).

| Command | What it does |
| --- | --- |
| `/research.init` | Copy the bundled templates into this paper repo's `.research/templates/` (run once per repo, after `install.sh`). |
| `/research.constitution` | Establish or update the research constitution: quality principles, writing voice, and venue norms. |
| `/research.proposal` | Pipeline entry: turn a raw idea into a sharp, falsifiable proposal - NABC, the gap, measurable contributions, testable RQs, venue and paper type. |
| `/research.relatedwork` | Survey prior work and position your contribution against it. |
| `/research.feasibility` | De-risk the central result with a quick probe and return a GO / NO-GO / PIVOT verdict before you invest in the full build. |
| `/research.tasks` | Produce a paper-type-aware experiment design plus the experiment and paper task lists (READY vs blocked-on-claim). |
| `/research.experiment` | Break the tasks into trackable experiments and keep the claim-evidence matrix current. |
| `/research.paper` | Draft paper sections, paper-type aware, with every claim traceable back to the evidence matrix. |
| `/research.analyze` | Read-only cross-artifact consistency and review-readiness audit; outputs a prioritized gap report. |
| `/research.rebuttal` | Draft a prioritized, evidence-backed rebuttal to reviewer comments, fitted to the venue word limit. |
| `/research.review` | Simulate a reviewer panel: write mock reviews + scores, route each finding to the command that owns the fix, and loop until clean. |
| `/research.ae` | Prepare an artifact-evaluation submission: reproducibility checklist, artifact README, badge plan, archival link. |

## Supported agents

speckit-research installs the same pipeline for three AI coding agents. Pick one or more at install time; `--all` does every one. The default (no flag) is Claude Code, for backward compatibility. Claude Code can additionally install as a **plugin** from the marketplace.

| Agent | Install | Where it lands | How you invoke a stage |
| --- | --- | --- | --- |
| **Claude Code** (plugin) | `/plugin install speckit-research@speckit-research` | Claude Code plugin cache | `/speckit-research:research.proposal <text>` |
| **Claude Code** (script) | `./install.sh` (default) | `~/.claude/commands/research.*.md` | `/research.proposal <text>` slash command |
| **Codex CLI** | `./install.sh --codex` | `~/.codex/prompts/research.*.md` | `/research.proposal <text>` slash command |
| **GitHub Copilot CLI** | `./install.sh --copilot` | `~/.copilot/agents/research.*.agent.md` | `/agent` → pick `research.proposal`, then type your input |

A few details:

- **Claude Code, two ways.** The *plugin* path (`/plugin marketplace add jiancui-research/speckit-research` → `/plugin install speckit-research@speckit-research`) needs no script and auto-updates via `/plugin marketplace update`, but stages are namespaced (`/speckit-research:research.proposal`). The *script* path (`./install.sh`) drops plain `/research.*` commands into `~/.claude/commands/`. Both ship the same command files and templates; the plugin loads templates from its own bundle (`${CLAUDE_PLUGIN_ROOT}/templates`), the script stages them under `~/.speckit-research`.
- **Claude Code and Codex CLI** consume the command files verbatim. Both expand the `$ARGUMENTS` placeholder with whatever you type after the command, so the pipeline behaves identically.
- **Copilot CLI** has no parameterized slash commands, so each stage is installed as a *custom agent* instead. `install.sh` generates one `research.<name>.agent.md` per stage, with a short adapter note at the top that maps the two slash-command idioms onto the agent model: `$ARGUMENTS` becomes "your latest message", and `Next: /research.<x>` becomes "switch to the `research.<x>` agent via `/agent`". The pipeline body is otherwise unchanged.
- **Honoring `$CODEX_HOME`.** If you set `CODEX_HOME`, Codex prompts install under `$CODEX_HOME/prompts`. You can also override any destination directly with `CLAUDE_COMMANDS_DIR`, `CODEX_PROMPTS_DIR`, or `COPILOT_AGENTS_DIR`.
- **No install needed for a quick try.** Any agent that can pull a file into context can run a stage directly — e.g. in Copilot CLI, `@commands/research.proposal.md <your idea>` reads the command and your input without registering anything. The installers exist so the stages are available everywhere without juggling paths.

`--symlink` (for the script install of Claude Code and Codex CLI) links the command files instead of copying them, so edits to this repo take effect immediately. `--uninstall` removes the script-installed stages from all three agents and deletes the staged templates. Plugin installs are managed with `/plugin` instead — remove with `/plugin uninstall speckit-research@speckit-research`.

## Working directory

Commands read and write under `./.research/` in your own paper repo. They create folders as needed.

```
.research/
  memory/constitution.md   research principles + writing voice
  templates/               skeletons + craft guides (copied here by /research.init)
  proposal.md              problem, motivation (NABC), gap, contributions, RQs, venue, paper type
  related-work.md          prior work and positioning
  feasibility.md           de-risk probe + GO / NO-GO / PIVOT verdict
  tasks/experiment.md      experiment design + build/obtain & experiment task list
  tasks/paper.md           paper section task list (READY vs blocked-on-claim)
  claims.md                claim ↔ evidence matrix
  experiments/             one file per experiment + index.md
  paper/                   section-by-section drafts
  analyze-report.md        prioritized gap report
  review/  rebuttal/  ae/   outputs of those commands
```

Commit `./.research/` alongside your paper. It is the spec - a readable record of every decision, claim, and piece of evidence behind the draft.

## Customizing the constitution

The constitution at `.research/memory/constitution.md` is where you set the rules every other command follows: quality bar, writing voice, citation habits, and the norms of your target venue. Run `/research.constitution` to create or update it in a guided way, or edit the file by hand. Once it exists, every command reads it first, so a change there ripples through the whole pipeline.

If no constitution exists, commands fall back to sensible defaults and keep going.

## Paper types

Several commands are paper-type aware - measurement, attack, defense, benchmark, and systematization (SoK) - and adapt their structure and checklists accordingly. The skeletons live in `templates/paper/`, and cross-cutting craft guides in `templates/sections/` (abstract + intro, figures + tables) and `templates/venue-norms.md` (choosing a venue and its conventions). `/research.init` copies all of these into your paper repo's `.research/templates/`, where the commands load them.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add or improve commands and templates. The guiding principle: keep it simple, keep the pipeline consistent, and write original, generalizable guidance.

## Credits

Inspired by [GitHub spec-kit](https://github.com/github/spec-kit) (MIT), which brought Spec-Driven Development to software. speckit-research adapts the idea to writing research papers.

## License

MIT - see [LICENSE](LICENSE).
