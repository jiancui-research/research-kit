# speckit-research

Spec-Driven Development for research papers, as Claude Code slash commands.

Writing a paper is a lot like building software: you start fuzzy, and quality comes from making each step explicit, reviewable, and traceable to evidence. speckit-research borrows that discipline. Instead of one giant "write my paper" prompt, it gives you a pipeline of small, focused commands - each reads what came before, takes your input, and produces one well-scoped artifact under `./.research/` in your paper repo.

It is just Claude Code slash commands plus Markdown templates and a default research constitution. No Python CLI, no hooks, no build step. Simplicity is the point.

## Pipeline

The commands form an ordered pipeline. Each stage builds on the last:

```
constitution → idea → relatedwork → plan → experiment → paper → analyze
```

Plus four commands you reach for when the moment calls for it: `rebuttal`, `review`, `proposal`, and `ae` (artifact evaluation).

You don't have to run every stage, and you can re-run any command as your work evolves. Commands only touch their own artifacts and tell you before overwriting anything.

## Quickstart

```sh
# 1. Install the commands into ~/.claude/commands/
./install.sh

# 2. In your paper repo, set the tone (optional but recommended)
/research.constitution measurement paper for a security venue, plain and precise voice

# 3. Sharpen your idea
/research.idea LLM agents leak secrets through tool-call arguments; measure how often

# 4. Walk the pipeline
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

## Working directory

Commands read and write under `./.research/` in your own paper repo. They create folders as needed.

```
.research/
  memory/constitution.md   research principles + writing voice
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

Several commands are paper-type aware - measurement, attack, defense, and benchmark - and adapt their structure and checklists accordingly. The per-type templates live in `templates/paper/`.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add or improve commands and templates. The guiding principle: keep it simple, keep the pipeline consistent, and write original, generalizable guidance.

## Credits

Inspired by [GitHub spec-kit](https://github.com/github/spec-kit) (MIT), which brought Spec-Driven Development to software. speckit-research adapts the idea to writing research papers.

## License

MIT - see [LICENSE](LICENSE).
