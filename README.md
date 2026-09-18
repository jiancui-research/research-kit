<div align="center">

# 🔬 research-kit

### Research, writing, and review in nine commands.

**Develop your idea, run the study, and write in your paper's own style.**

[![License](https://img.shields.io/github/license/jiancui-research/research-kit)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/jiancui-research/research-kit)](https://github.com/jiancui-research/research-kit/commits/main)

[Quickstart](#quickstart) · [Commands](#commands) · [Review UIs](#review-ui) · [Workflow](docs/workflow.md) · [Installation](docs/install.md)

![mdreview demo: editing, commenting, and export](docs/assets/mdreview-demo.gif)

</div>

## Quickstart

**1. Install for your agent.**

Claude Code:

```text
/plugin marketplace add jiancui-research/research-kit
/plugin install research-kit@research-kit
```

Codex CLI, from your terminal:

```sh
codex plugin marketplace add https://github.com/jiancui-research/research-kit
codex plugin add research-kit@research-kit
```

Start a new agent session after installation. [OMP, Copilot, script installs, and upgrades →](docs/install.md)

**Which agent?** For writing, I use Codex and get the best prose in my own experience. This is a personal observation; all four agents receive the same stage instructions.

**2. Start with what you have.** These are agent requests, one per turn:

```text
/research.write related-work         # outline or revise an existing section
/research.write draft intro          # explicitly request full prose
/research.texreview                  # edit LaTeX and comment on the PDF
```

Claude plugin commands use the prefix `/research-kit:research.write`. In Codex,
use `$research-kit:research.write` and include your request in the same message.

Already have a paper? Writing reads the whole manuscript and quotes real sentences
from it before changing a section. It needs no proposal, plan, or task queue.
Project setup happens automatically on the first research or writing command.

Starting from an idea? Follow the research loop:

```text
/research.proposal describe your idea or point to rough notes
/research.relatedwork
/research.feasibility
/research.plan
/research.implement
/research.write draft intro
/research.review
```

Each stage reports its work and suggests the next step. You review its output and
choose when to continue. `implement` builds and evaluates by default; manuscript
work requires an explicit request.

## Commands

| Command | What it does |
|---|---|
| `/research.proposal` | Turn an idea or rough notes into a testable research argument. |
| `/research.relatedwork` | Survey prior work and sharpen the proposal's gap. |
| `/research.feasibility` | Run a small probe and decide GO, NO-GO, or PIVOT. |
| `/research.plan` | Design the study and maintain its task list, preserving progress. |
| `/research.implement` | Build, evaluate, maintain claims, and check consistency. |
| `/research.write` | Outline, revise, or draft in the paper's style; learn writing preferences. |
| `/research.review` | Critically review the paper using venue and paper-type guidance. |
| `/research.mdreview` | Edit and comment on Markdown; use `split` for source beside preview. |
| `/research.texreview` | Edit LaTeX beside the PDF, with comments and source navigation. |

## Keep your writing preferences

Before your first outline, draft, or revision, choose **2–3 papers close to your
topic and paper type**. Provide papers you like, or ask the agent to suggest some
with reasons. Say **"skip examples"** to proceed without them. Your selection or
skip is saved for the project, so later sections do not ask again.

```text
/research.write style suggest example papers for this project
/research.write style learn from the papers in .research/writing/samples/
/research.write style remember: use direct sentences and keep our terminology
```

Samples, explicit instructions, and confirmed preferences from your edits feed the
same `.research/writing/style.md`. Refreshing samples preserves your example-paper
choice, instructions, and learned preferences. Later sections read that file and
match the manuscript's sentence construction, terms, numbers, and macros.

<a id="review-ui"></a>

## Two review UIs

**LaTeX: `/research.texreview`**

![texreview: LaTeX source, compiled PDF, and comments](docs/assets/texreview-hero.png)

Select text in either pane and click **Comment**, press **⌘⇧M**, or right-click.
Comments carry source targets the agent can act on. Save to recompile; use the
outline or click PDF text to navigate. Requires `uv` and a TeX installation for compiling.

**Markdown: `/research.mdreview`**

![mdreview: document editing and comments](docs/assets/mdreview-hero.png)

Click a rendered block to edit it, or use `/research.mdreview split` for source
beside preview. Save with **⌘S**. Select text to comment. Requires `uv`.

Both viewers keep comments in the repo and export them for use in another chat.
Ask the agent to read `.mdreview/` or `.texreview/comments.json` and address the
open comments. The viewers work independently of the research pipeline.

## Project files and upgrades

Tracking documents live under `.research/`; code, experiments, and manuscript
source live in the project's own directories. `plan.md` and `tasks.md` remain
separate files, maintained by one command. Project preferences stay in
`.research/memory/constitution.md` and can be edited directly.

Updating the kit preserves project artifacts and customized local templates.
First use fills missing templates and reports relevant differences. Existing
copies are refreshed only when you request it. Script reinstalls prune retired
commands that the installer recorded. See the [upgrade notes](docs/install.md#upgrading).

[Workflow and file ownership](docs/workflow.md) · [Design](docs/design.md) · [Contributing](CONTRIBUTING.md)

Inspired by [GitHub spec-kit](https://github.com/github/spec-kit). [MIT licensed](LICENSE).
