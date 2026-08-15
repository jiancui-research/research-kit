<div align="center">

# 🔬 research-kit

### *Do research in documents, not code.*

**Spec-Driven Development for research papers: a pipeline of slash commands for your AI coding agent — Claude Code, Codex CLI, GitHub Copilot CLI, or Oh My Pi (OMP).
Every stage produces one reviewable Markdown document. The documents are what you check; the code is written from them.**

[![License](https://img.shields.io/github/license/jiancui-research/research-kit)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/jiancui-research/research-kit)](https://github.com/jiancui-research/research-kit/commits/main)
[![Agents](https://img.shields.io/badge/agents-Claude%20Code%20·%20Codex%20·%20Copilot%20·%20OMP-blueviolet)](#-supported-agents)
[![Form factor](https://img.shields.io/badge/pure%20markdown-no%20build%20step-brightgreen)](#-quickstart)
[![GitHub stars](https://img.shields.io/github/stars/jiancui-research/research-kit?style=social)](https://github.com/jiancui-research/research-kit/stargazers)

[Quickstart](#-quickstart) · [Commands](#-commands) · [Review UI](#review-ui) · [Workflow docs](docs/workflow.md) · [Design](docs/design.md)

![mdreview demo: click-to-source sync, commenting, export](docs/assets/mdreview-demo.gif)

*The bundled review surfaces: Overleaf-style split view for your docs **and** your LaTeX paper, click-to-source sync, Google-Docs-style comments an agent can act on — [details below](#review-ui).*

</div>

---

## 🤔 Why

research-kit gives you three things. Each one buys back time you were spending on something that is not research.

### 1. Write the document, not the plumbing

Your attention goes to the argument. Code, experiment scripts, and LaTeX formatting are the agent's job.

Every stage produces one Markdown doc under `./.research/` — the spec, the record, and the thing you actually check. The implementation plan derives from these docs, the agent builds from the plan, and results flow back into `claims.md` and the draft, where you judge them. Two guardrails keep that honest: `feasibility` returns **GO / NO-GO / PIVOT** before you over-invest, and `analyze` catches the lanes drifting from the docs and names the exact re-run.

### 2. Think on the page, and hand your thinking to the agent

Reading and judging are yours; you should be able to do both in place.

Both your Markdown docs and your LaTeX manuscript open in a [bundled review UI](#review-ui) with Google-Docs-style comments anchored to `file:line`. The agent picks them up straight from the repo — `.mdreview/comments.json`, `.texreview/comments.json` — so "read the comments and address them" needs no export at all. When you want a different model, or just a conversation, one button copies every open comment with its target and reply format into any chat.

### 3. Write in your paper's voice, not an agent's

Prose that reads as generated is prose you have to rewrite.

`/research.write` reads the **whole** manuscript before it writes a word, states the paper's argument back to you, and takes a voice sample — your terms, your tense, your number formatting — so a new section matches the ones around it. Under that sit craft guides for the genre, per section and per paper type. And with `/research.style` you point it at papers whose writing you admire, and it distills them into `.research/writing/style.md` — which then keeps growing, absorbing the instructions you give and the edits you make, so a preference stated once is never re-earned.

The three compound: the argument is settled in documents, checked by commenting on them, and written up in a voice that is yours.

## 🚪 Where you come in

Nobody starts from nothing every time. Find the row that matches what is already on your disk — the pipeline is a chain you can join partway, not a gate you have to walk through.

<details open>
<summary><b>1. "I have an idea and nothing else."</b> — the full chain</summary>

The canonical path, and the only one that uses every stage. `proposal` turns the idea into a falsifiable argument, `feasibility` tells you whether to keep going *before* you build, and `tasks` becomes the queue the agent works.

```sh
/research.init && /research.constitution
/research.proposal "<your raw idea, however rough>"
/research.relatedwork          # sharpens the gap back into proposal.md
/research.feasibility          # GO / NO-GO / PIVOT — the cheapest stage to fail at
/research.plan && /research.tasks
/research.implement            # build + eval, until the queue is done
```
</details>

<details>
<summary><b>2. "I have code and results, but no paper."</b> — start at the argument, skip the gate</summary>

The riskiest question is already answered, so `feasibility` has nothing to add. What you are missing is the argument the results support, and the ledger tying one to the other.

```sh
/research.init
/research.proposal "<what the results show, and why it matters>"
/research.plan                 # describe what you built, not what you planned to
/research.tasks                # the queue comes out as mostly Eval + Paper
/research.implement            # fills claims.md: every claim -> supported / partial / refuted
/research.analyze              # names where code, evidence, and docs disagree
```

`claims.md` is the thing that makes this path worth it: it is what stops a number in the abstract from drifting away from the experiment that produced it.
</details>

<details>
<summary><b>3. "I have rough notes, a half-written doc, an old draft."</b> — feed them to the entry stage</summary>

`proposal` takes prose as input, not just a one-liner. Point it at what you have and it returns a 1–3 page argument you can actually judge — then iterate on *that* rather than on scattered notes.

```sh
/research.init
/research.proposal "$(cat notes.md)"     # or just describe where the notes live
/research.mdreview                       # read it, comment in place, let the agent revise
```

From there, join path 1 or 2 depending on whether the work exists yet.
</details>

<details>
<summary><b>4. "I already have a LaTeX paper in flight."</b> — writing tool only, no pipeline</summary>

**You do not need the pipeline to use the writing half.** The section commands read the manuscript itself, so a paper with no `proposal.md` behind it still works: the argument gets derived from your abstract and contribution list instead.

```sh
/research.init                       # just puts the templates and craft guides in place
/research.style                      # optional: point it at papers you want to sound like
/research.write related-work         # reads the WHOLE paper, states its argument, then works
/research.texreview                  # comment on the PDF; the agent picks the comments up
/research.review                     # mock reviewer panel, reading only the paper
```

`/research.write` reads every section before touching one, so a new paragraph lands in your terms, your tense, and your number formatting rather than in a generic register.
</details>

## 🗺️ The pipeline

research-kit follows the workflow strong research already follows: sharpen an idea into a falsifiable proposal, position it, pilot the riskiest assumption, plan the study, derive one queue, then build, evaluate, and work on the manuscript through one executor before review. Each step stays explicit and checkable:

```mermaid
flowchart LR
    C[constitution] --> P[proposal] --> RW[relatedwork] --> F{feasibility<br/>GO / NO-GO / PIVOT}
    F -.->|NO-GO / PIVOT| P
    F -->|GO| PL["plan<br/>study design"]
    PL --> T["tasks<br/>single queue"]
    T --> I["implement<br/>build + eval + explicit user-led paper work"]
    I --> A["analyze<br/>(sync check)"] --> R["review<br/>(paper-only)"]
    A -.->|re-run what is stale| T
    R -.->|route findings| I
```

Why this shape: every stage ends in a Markdown document under `./.research/` that you review before the next stage builds on it. After feasibility's GO, `plan` fixes the stable study design and `tasks` derives one queue. `implement` owns that queue: it builds code, runs evals, updates `claims.md`, and assists with `[USER-LED]` manuscript tasks only when you explicitly select them. Empty/default runs never start manuscript work. The Build section remains paper-type aware; `rebuttal` and `ae` are auxiliary.

📐 **[Workflow diagram + per-command inputs/outputs →](docs/workflow.md)**

<a id="review-ui"></a>

## 🖥️ Where you watch the agent work

Handing the build and the evaluation to an agent only works if you can *see* what it did. So research-kit ships two review surfaces — one for the tracking documents, one for the paper itself. Both are local web UIs, one Python file each, localhost only, nothing beyond `uv` to install. You read, you comment, you edit a line; the agent picks the comments up from the repo and does the work.

### 📄 The paper: `/research.texreview`

**A single-user local Overleaf with the review loop built in.** LaTeX source on the left, the compiled PDF on the right, and comments that know which line of which `.tex` file they belong to.

![texreview: LaTeX source left, compiled PDF right, a comment carrying its file:line target](docs/assets/texreview-hero.png)

- 💬 **Comment on either side, fix in the source.** Select text in the rendered paper *or* in the LaTeX, then right-click it to attach a note (selecting alone no longer interrupts you). Every comment records the quote *and* a `file.tex:line` target — resolved through SyncTeX for a PDF selection, known outright for a source one — so an agent working in the paper repo knows exactly where to edit — *"read `.texreview/comments.json` and address the open comments"*. It replies with what it changed and marks them resolved; the fix is highlighted on the next compile.
- 🎯 **Click the PDF, land on the line.** Click any rendered word and the editor jumps to its source. When SyncTeX can only point at a structural line — `acmart` typesets `\begin{abstract}` during `\maketitle`, the `comment` package routes blocks through a generated file — texreview falls back to searching the sources for the words you actually clicked, so you land somewhere you can edit. **Reveal →** goes the other way, flashing the PDF box for your cursor line.
- 🔨 **Save and it recompiles.** `⌘S` runs `latexmk -pdf -synctex=1` and reloads the pane; saves landing mid-compile queue one follow-up instead of stacking. Errors show a parsed log. Compile in a terminal instead and the pane still refreshes.
- ⌨️ **Editor basics that matter in LaTeX** — `⌘B`/`⌘I` wrap the selection in `\textbf{}`/`\textit{}` (press again to unwrap), find in file (`⌘F`) with a live match count, comment toggle (`⌘/`) over the selection, syntax colour with line numbers, bracket matching that tints the partner of whichever `{` or `[` your cursor sits on (and reddens one with no partner, which is a compile error waiting to happen), collapsible folders so a 25-file paper repo opens at six rows.
- 📋 **Export with targets** — open comments copy to the clipboard with ids, `file:line` targets, and reply instructions, for any AI outside the repo.

Launch from the manuscript repo, or from the research repo (it follows `.research/paper-repo`): `/research.texreview`, or directly `uv run tools/texreview.py --open`. Needs `uv` plus a TeX install (`latexmk` / `synctex`, bundled with MacTeX and TeX Live).

### 📝 The documents: `/research.mdreview`

Checking and editing that pipeline of docs *is* the workflow — so **mdreview** gives the Markdown side the same treatment: a local web UI over your repo's docs, where you revise the rendered document directly.

![mdreview overview: split view with comments](docs/assets/mdreview-hero.png)

- ✍️ **Revise in the rendered view** — click any paragraph, heading, list item, table row or code block and it turns into just that markdown (one task out of a 30-item queue, one row of `claims.md`); click away and it renders again. Only the lines you touched are rewritten, because the source range comes from the markdown parser rather than from converting HTML back to markdown — so tables, spacing and raw HTML elsewhere are never reflowed.
- 🔀 **`Preview / Markdown` toggle** — one wide pane, swapped for the full source editor (line numbers, syntax colour) when you need the raw file. Prefer source and preview side by side? `/research.mdsplit` is the same tool in the two-pane layout, with click-to-source sync and a draggable divider.
- 💬 **Google-Docs-style comments** — select rendered text and attach a note. Comments live as sidecar JSON under `./.mdreview/`, so your markdown stays clean and any coding agent can read them in-repo: *"read `.mdreview/` and address the comments on proposal.md"*.
- 📋 **One-click export** — copies the document plus open comments to the clipboard, ready to paste into any AI for review.
- 🧜 **Mermaid diagrams** — ` ```mermaid ` fences render as diagrams with a zoom + pan lightbox (via CDN; they fall back to code blocks offline).
- 🔒 **Safe saves** — atomic writes with a conflict guard for when the file changed on disk mid-review (say, an agent edited it), plus a `.research/ only` sidebar filter that keeps the focus on the tracking docs.

| Comment on a selection | Click-to-source sync + mermaid |
| --- | --- |
| ![commenting](docs/assets/mdreview-comment.png) | ![sync and mermaid](docs/assets/mdreview-sync.png) |

Launch from any repo: `/research.mdreview` in your agent, or directly `uv run tools/mdreview.py --open` (add `--split` for the two-pane layout).

## ⚡ Quickstart

**Claude Code — plugin (recommended, no script):**

```text
/plugin marketplace add jiancui-research/research-kit
/plugin install research-kit@research-kit
```

Plugin stages are namespaced, e.g. `/research-kit:research.proposal …`; update later with `/plugin marketplace update`.

**Oh My Pi (OMP) — plugin (no script):**

```text
/marketplace add jiancui-research/research-kit
/marketplace install research-kit@research-kit
```

OMP reads the same `.claude-plugin` bundle directly, exposing the namespaced `/research-kit:research.*` stages. Update later with `/marketplace update research-kit`, then `/marketplace upgrade research-kit@research-kit` — or from a shell, `omp plugin marketplace update research-kit && omp plugin upgrade research-kit@research-kit` (note: `omp marketplace …` is not a top-level command; marketplace management lives under `omp plugin marketplace`). Refreshing the marketplace alone does **not** bump an installed plugin — `omp plugin list` keeps reporting the old version until you run the `upgrade`.

**Codex CLI and GitHub Copilot CLI — script:**

```sh
git clone https://github.com/jiancui-research/research-kit
cd research-kit
./install.sh --codex      # -> ~/.codex/prompts/     (all stages, /research.* )
./install.sh --copilot    # -> ~/.copilot/agents/    (all stages as custom agents)
```

Use the script for these two, not their plugin marketplaces. Codex installs a plugin fine but converts commands to skills and drops every stage that takes arguments, so you would get `research.init` alone; Copilot expects `plugin.json` at the repo root plus an `agents/` or `skills/` directory, so a marketplace install exposes nothing. The script targets each agent's documented location: [Codex custom prompts](https://developers.openai.com/codex/custom-prompts) (deprecated in favour of skills, still supported with `$ARGUMENTS`, no removal date announced) and [Copilot personal custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli).

**Any agent — script:**

```sh
./install.sh            # Claude Code (default). Also: --codex, --copilot, --all
```

Then, in your paper repo, start with `/research.init` (`/research-kit:research.init` for plugin installs) and follow the pipeline — each command writes its result into `./.research/` and suggests the next one.

### ✅ Check what you have

Verify the install rather than assuming it took — an out-of-date copy fails silently by running old stage instructions.

```sh
omp plugin list                 # OMP: expect research-kit@research-kit (<version>)
copilot plugin list             # Copilot CLI: expect research-kit@research-kit (v<version>)
ls ~/.claude/commands/research.* # script installs (or ~/.codex/prompts/, ~/.copilot/agents/)
```

Compare against the `version` field in [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) on `main`. To update:

```sh
omp plugin marketplace update research-kit && omp plugin upgrade research-kit@research-kit
copilot plugin update research-kit
git pull && ./install.sh --all   # script installs; re-running also prunes deleted stages
```

Gotchas seen in practice:

- **`copilot plugin update` can fail with `Access is denied. (os error 5)`** when a file in the plugin directory is locked by a running CLI. Close other Copilot CLI sessions and retry; the second attempt usually succeeds.
- **A Copilot plugin entry that lists a version still exposes no stages.** `copilot plugin list` will happily report `research-kit@research-kit (v0.13.0)` while `~/.copilot/agents/` is empty and the CLI reports no custom agents — re-verified on Copilot CLI 1.0.74. The registry entry is not the same thing as a usable install; use `./install.sh --copilot` and confirm `ls ~/.copilot/agents/research.*.agent.md` lists every stage.
- **Script installs are per-agent.** Updating the OMP or Claude Code plugin does nothing for `~/.codex/prompts/` or `~/.copilot/agents/`; re-run `install.sh` for those.
- **Windows: `./install.sh` reports `No such file or directory` even though the file is right there.** Git checked the script out with CRLF endings (`core.autocrlf=true`), so the kernel reads the shebang as `#!/usr/bin/env sh\r`. The repo now ships a `.gitattributes` pinning `*.sh` to LF; on a checkout made before that, run `git rm --cached install.sh && git checkout HEAD -- install.sh` (or `dos2unix install.sh`) to restore it. The `HEAD` matters: without it, `git checkout` looks in the index, where `git rm --cached` just removed the file, so it fails with `pathspec 'install.sh' did not match` and leaves the script staged for deletion.

<details>
<summary><b>The full run, stage by stage</b></summary>

```sh
/research.init                       # once per repo: copy templates into .research/
/research.constitution <focus>       # optional: set writing voice + venue
/research.style                      # optional: learn how you write, from samples + your instructions
/research.proposal <your raw idea>   # pipeline entry
/research.relatedwork
/research.feasibility
/research.plan                       # study design: architecture + eval design (plan.md)
/research.tasks                      # one work queue derived from the plan (tasks.md)
/research.implement                  # work automated queue tasks
/research.implement paper intro      # explicitly outline a user-led manuscript task
/research.write related-work         # or write a section directly, outside the queue
/research.analyze                    # also a "sync" check: what drifted, what to re-run
/research.review
```

</details>

## 🧩 Commands

| Command | What it does |
| --- | --- |
| `/research.init` | Copy the bundled templates into this paper repo's `.research/templates/` (run once per repo, after `install.sh`). |
| `/research.constitution` | Establish or update the research constitution: quality principles, writing voice, and venue norms. |
| `/research.proposal` | Pipeline entry: turn a raw idea into a readable 1-3 page argument (falsifiable thesis, argued gap, pre-committed validation plan, venue and paper type). |
| `/research.relatedwork` | Survey prior work into `related-work.md` and sharpen the proposal's gap and positioning. |
| `/research.feasibility` | De-risk the central result with a quick probe and return a GO / NO-GO / PIVOT verdict before you invest in the full build. |
| `/research.plan` | The study's technical design into `plan.md`: architecture, evaluation design, key decisions, project layout. Stable; tasks derive from it. |
| `/research.tasks` | Derive the single work queue `tasks.md` from the plan (Setup/Build/Eval/Paper/Polish, T-ids, claim links); re-runs refine, preserving checkbox states. |
| `/research.implement` | Execute the whole queue: build code, run evals, maintain claims, and handle `[USER-LED]` manuscript tasks only when explicitly selected (`paper`, `outline`, `critique`, or `draft`). |
| `/research.write` | Write or revise one manuscript section: reads the whole paper and states its argument before any prose, then outlines, revises, critiques, or drafts. Same work as `/research.implement paper <section>`, reachable on its own. |
| `/research.style` | Optional: build `.research/writing/style.md`, the file the writing commands read for how *you* want your paper written — distilled from papers you admire (`writing/samples/`), the instructions you give, and the edits you make to prose written for you. |
| `/research.analyze` | Read-only cross-artifact audit **and** the sync checker across plan, tasks, code, evidence, and manuscript: flags drift and names the exact re-run. |
| `/research.review` | Simulate a reviewer panel reading **only the paper**: mock reviews + scores, plus a suggested fix command per finding; you route them and loop until clean. |
| `/research.rebuttal` | Draft a prioritized, evidence-backed rebuttal to reviewer comments, fitted to the venue word limit. |
| `/research.ae` | Prepare an artifact-evaluation submission: reproducibility checklist, artifact README, badge plan, archival link. |
| `/research.mdreview` | Open a local web UI for the repo's markdown: one wide pane you revise directly in the rendered view, plus comments and export (optional; requires `uv`). Comments are sidecar JSON in `./.mdreview/` any agent can read. |
| `/research.mdsplit` | The same UI in the source-beside-preview layout: raw markdown left, rendered right, click-to-source sync. Same comments. |
| `/research.texreview` | Review the compiled paper: LaTeX source left, PDF right, SyncTeX click-to-source, comments on PDF selections carrying `file:line` targets, recompile on save, export (optional; requires `uv` + TeX). |

## 🤖 Supported agents

The same pipeline installs for four agents; pick one or more (`--all` covers the three `install.sh` targets; OMP uses the plugin marketplace).

| Agent | Install | How you invoke a stage |
| --- | --- | --- |
| **Claude Code** (plugin) | `/plugin install research-kit@research-kit` | `/research-kit:research.proposal <text>` |
| **Oh My Pi (OMP)** (plugin) | `/marketplace add jiancui-research/research-kit` → `/marketplace install research-kit@research-kit` | `/research-kit:research.proposal <text>` |
| **Claude Code** (script) | `./install.sh` | `/research.proposal <text>` |
| **Codex CLI** (script only) | `./install.sh --codex` | `/research.proposal <text>` |
| **GitHub Copilot CLI** (script only) | `./install.sh --copilot` | `/agent` → pick `research.proposal`, then type your input |

<details>
<summary><b>Per-agent notes (why Codex and Copilot need the script, self-pruning, overrides)</b></summary>

- **OMP** installs the same `.claude-plugin` bundle through `/marketplace`, reading `commands/` directly (it falls back to `.claude-plugin/marketplace.json` when `.omp-plugin/` is absent). Plugin commands resolve bundled templates and tools through OMP's installed-plugin registry at `~/.omp/plugins/installed_plugins.json`.
- **Codex** does have a marketplace and will happily install this bundle — but it converts commands into skills, and skills have no `$ARGUMENTS` substitution, so every stage that takes input is silently skipped. Only `research.init` survives. The script installs all stages into `~/.codex/prompts/` as native `/research.*` commands instead. (Custom prompts are marked deprecated in favour of skills, still support `$ARGUMENTS`, and have no announced removal date.)
- **Copilot** expects `plugin.json` at the repo root plus an `agents/` or `skills/` directory; it no longer surfaces a plugin's `commands/`, and an installed bundle reports zero available agents. This worked at Copilot CLI 1.0.40 and stopped by 1.0.63, so `./install.sh --copilot` (which generates `*.agent.md` custom agents in `~/.copilot/agents/`) is the supported path. The failure is quiet: `copilot plugin install`/`update` succeeds, `copilot plugin list` prints a version, and the bundle really is unpacked under `~/.copilot/installed-plugins/` — but the stages never appear. Trust `ls ~/.copilot/agents/research.*.agent.md`, not the plugin list. Re-verified on Copilot CLI 1.0.74.
- **One install for all four** would require shipping stages as `skills/<name>/SKILL.md`, the one format every agent here reads. The trade-off is that skills are model-invocable, so stages could fire without you asking; `docs/design.md` records the analysis.
- **Self-pruning & overrides.** Re-running `install.sh` removes commands deleted from the bundle. Override destinations with `CLAUDE_COMMANDS_DIR` / `CODEX_PROMPTS_DIR` / `COPILOT_AGENTS_DIR` (or `CODEX_HOME`); `--symlink` links instead of copies; `--uninstall` removes everything.

</details>

## 📁 Working directory

The project is one repo (under `~/Projects`, outside the vault). research-kit's **tracking docs** all live under `./.research/` — commit it alongside the paper as the decision record. The actual **work products** (code, data, paper source) live in sibling root folders.

<details>
<summary><b>Full layout</b></summary>

```
<project>/                 one repo under ~/Projects, outside the vault
  .research/               all research-kit tracking docs:
    memory/constitution.md   research principles + writing voice
    templates/               skeletons + craft guides (from /research.init)
    writing/                 optional: samples/ you chose + style.md (register, your standing instructions, what your edits taught it)
    proposal.md              problem, NABC, gap, contributions, RQs, venue, paper type
    related-work.md          prior work + positioning
    feasibility.md           de-risk probe + GO / NO-GO / PIVOT
    plan.md                  study design: architecture + eval design + layout (stable)
    tasks.md                 the single work queue: Setup/Build/Eval/Paper/Polish (churns)
    claims.md                claim ↔ evidence matrix (the shared sync point)
    analyze-report.md        prioritized gap + sync report
    review/ rebuttal/ ae/    outputs of those commands
  feasibility/             throwaway probe code
  src/                     the system code (built by /research.implement; folder declared in plan.md, legacy design/)
  eval/                    eval writeups + index + scripts, data, results
  paper/                   outlines + manuscript source - or a dedicated sibling repo
                           <name>-<venue><yy>-latex recorded in .research/paper-repo
```

</details>

## 🎨 Customization

`.research/memory/constitution.md` sets the quality bar, writing voice, and venue norms every command reads first — edit it directly or via `/research.constitution`. Several commands are paper-type aware (measurement, attack, defense, benchmark, SoK); the skeletons and craft guides live in `templates/` and are copied in by `/research.init`. `/research.style` is the optional layer on top: drop papers you admire into `.research/writing/samples/` and it distils one `writing/style.md` that every section you write reads — a file that also accumulates your standing instructions and whatever your own edits reveal.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep it simple, keep the pipeline consistent, and write original, generalizable guidance.

## 🙏 Credits & license

Inspired by [GitHub spec-kit](https://github.com/github/spec-kit) (MIT), which brought Spec-Driven Development to software. MIT licensed — see [LICENSE](LICENSE).
