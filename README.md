# speckit-research

Spec-Driven Development for research papers, as slash commands for your AI coding agent — Claude Code, Codex CLI, or GitHub Copilot CLI.

Writing a paper is a lot like building software: you start fuzzy, and quality comes from making each step explicit, reviewable, and traceable to evidence. speckit-research borrows that discipline. Instead of one giant "write my paper" prompt, it gives you a pipeline of small, focused commands - each reads what came before, takes your input, and produces one well-scoped artifact under `./.research/` in your paper repo.

It is just slash commands plus Markdown templates and a default research constitution. No Python CLI, no hooks, no build step. Simplicity is the point.

## Pipeline

The commands form an ordered pipeline. Each stage builds on the last:

```
constitution → idea → relatedwork → plan → experiment → paper → analyze
```

Plus four commands you reach for when the moment calls for it: `rebuttal`, `review`, `proposal`, and `ae` (artifact evaluation).

You don't have to run every stage, and you can re-run any command as your work evolves. Commands only touch their own artifacts and tell you before overwriting anything.

## Quickstart

```sh
# 1. Install the commands + stage the bundled templates
#    Default installs for Claude Code. Pick your agent(s) with flags:
./install.sh                     # Claude Code (default)
./install.sh --codex             # Codex CLI
./install.sh --copilot           # GitHub Copilot CLI
./install.sh --all               # all of the above
```

> In **Claude Code** and **Codex CLI** the stages are slash commands: `/research.idea …`.
> In **Copilot CLI** each stage installs as a custom agent — pick it with `/agent` (e.g.
> `research.idea`), then type your input. See [Supported agents](#supported-agents) below.

```sh
# 2. In your paper repo, copy the templates in (once per repo)
/research.init

# 3. Set the tone (optional but recommended)
/research.constitution measurement paper for a security venue, plain and precise voice

# 4. Sharpen your idea
/research.idea LLM agents leak secrets through tool-call arguments; measure how often

# 5. Walk the pipeline
/research.relatedwork
/research.plan
/research.experiment
/research.paper
/research.analyze
```

Each command reads your free text after the command name, reads its upstream artifacts, and writes its result into `./.research/`. When it finishes it prints the file path and suggests the next command.

## Commands

All commands are invoked as `/research.<name>` in Claude Code.

| Command | What it does |
| --- | --- |
| `/research.init` | Copy the bundled templates into this paper repo's `.research/templates/` (run once per repo, after `install.sh`). |
| `/research.constitution` | Establish or update the research constitution: quality principles, writing voice, and venue norms. |
| `/research.idea` | Turn a rough idea into a sharp, falsifiable `idea.md` - NABC, the gap, measurable contributions, testable RQs, venue and paper type. |
| `/research.relatedwork` | Survey prior work and position your contribution against it. |
| `/research.plan` | Produce a paper-type-aware research and experiment plan: methodology, baselines, datasets, metrics, threat model, evaluation design. |
| `/research.experiment` | Break the plan into trackable experiments and keep the claim-evidence matrix current. |
| `/research.paper` | Draft paper sections, paper-type aware, with every claim traceable back to the evidence matrix. |
| `/research.analyze` | Read-only cross-artifact consistency and review-readiness audit; outputs a prioritized gap report. |
| `/research.rebuttal` | Draft a prioritized, evidence-backed rebuttal to reviewer comments, fitted to the venue word limit. |
| `/research.review` | Write a fair, specific, actionable peer review of another author's paper. |
| `/research.proposal` | Turn idea and plan into a proposal or fellowship pitch using NABC and Heilmeier lenses, audience-aware. |
| `/research.ae` | Prepare an artifact-evaluation submission: reproducibility checklist, artifact README, badge plan, archival link. |

## Supported agents

speckit-research installs the same pipeline for three AI coding agents. Pick one or more at install time; `--all` does every one. The default (no flag) is Claude Code, for backward compatibility.

| Agent | Install | Where it lands | How you invoke a stage |
| --- | --- | --- | --- |
| **Claude Code** | `./install.sh` (default) | `~/.claude/commands/research.*.md` | `/research.idea <text>` slash command |
| **Codex CLI** | `./install.sh --codex` | `~/.codex/prompts/research.*.md` | `/research.idea <text>` slash command |
| **GitHub Copilot CLI** | `./install.sh --copilot` | `~/.copilot/agents/research.*.agent.md` | `/agent` → pick `research.idea`, then type your input |

A few details:

- **Claude Code and Codex CLI** consume the command files verbatim. Both expand the `$ARGUMENTS` placeholder with whatever you type after the command, so the pipeline behaves identically.
- **Copilot CLI** has no parameterized slash commands, so each stage is installed as a *custom agent* instead. `install.sh` generates one `research.<name>.agent.md` per stage, with a short adapter note at the top that maps the two slash-command idioms onto the agent model: `$ARGUMENTS` becomes "your latest message", and `Next: /research.<x>` becomes "switch to the `research.<x>` agent via `/agent`". The pipeline body is otherwise unchanged.
- **Honoring `$CODEX_HOME`.** If you set `CODEX_HOME`, Codex prompts install under `$CODEX_HOME/prompts`. You can also override any destination directly with `CLAUDE_COMMANDS_DIR`, `CODEX_PROMPTS_DIR`, or `COPILOT_AGENTS_DIR`.
- **No install needed for a quick try.** Any agent that can pull a file into context can run a stage directly — e.g. in Copilot CLI, `@commands/research.idea.md <your idea>` reads the command and your input without registering anything. The installers exist so the stages are available everywhere without juggling paths.

`--symlink` (for Claude Code and Codex CLI) links the command files instead of copying them, so edits to this repo take effect immediately. `--uninstall` removes the installed stages from all three agents and deletes the staged templates.

## Working directory

Commands read and write under `./.research/` in your own paper repo. They create folders as needed.

```
.research/
  memory/constitution.md   research principles + writing voice
  templates/               skeletons + craft guides (copied here by /research.init)
  idea.md                  problem, motivation (NABC), gap, contributions, RQs, venue, paper type
  related-work.md          prior work and positioning
  plan.md                  methodology, baselines, datasets, metrics, threat model
  claims.md                claim ↔ evidence matrix
  experiments/             one file per experiment + index.md
  paper/                   section-by-section drafts
  analyze-report.md        prioritized gap report
  review/  rebuttal/  proposal/  ae/   outputs of those commands
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
