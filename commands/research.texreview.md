---
description: Open texreview, a local web UI to review the compiled paper - LaTeX source left, PDF right, SyncTeX click-to-source, comments on selections in either pane (button, `⌘⇧M`, or right-click) (requires uv + a TeX install). Comments are sidecar JSON in the paper repo's .texreview/ that any agent can read.
argument-hint: optional flags passed through, e.g. --main paper.tex --port 9000
---

## What this is
texreview is research-kit's optional manuscript review UI - a single-user local Overleaf with the review loop built in: editable LaTeX source on the left, the compiled PDF on the right, SyncTeX sync in both directions (click PDF text to jump to its source line; Reveal flashes the PDF box for the cursor line), Google-Docs-style comments on a selection in **either** pane - right-click the selection to comment - each recording its `file:line` target, Overleaf-style `⌘B`/`⌘I` wrapping the selection in `\textbf{}`/`\textit{}`, a Recompile button (`latexmk -pdf -synctex=1`), and one-click export of open comments for any AI. It is a leaf utility - no other command depends on it. (Like /research.init, this command does not read the constitution; it only launches a tool.)

## Steps
1. Resolve the tool from the same three locations as the bundled templates:
   - `${CLAUDE_PLUGIN_ROOT}/tools/texreview.py` (Claude Code plugin install), else
   - `<installPath>/tools/texreview.py`, where `installPath` comes from the enabled `research-kit@research-kit` entry in the nearest project-scoped `.omp/plugins/installed_plugins.json`, falling back to `~/.omp/plugins/installed_plugins.json` (OMP plugin install), else
   - `${RESEARCH_KIT_HOME:-$HOME/.research-kit}/tools/texreview.py` (staged by `install.sh`).
   If none exists, say so and point to `./install.sh`, `/plugin install research-kit@research-kit`, or `/marketplace install research-kit@research-kit`, then stop.
2. Check `uv` is available (`command -v uv`). If missing, point to https://docs.astral.sh/uv/ and stop. If `latexmk` is missing, warn that Recompile and SyncTeX need a TeX install (MacTeX / TeX Live) but continue.
3. Run it in the background: `uv run <resolved-path> --open $ARGUMENTS`. The tool finds the manuscript itself: the current repo if it holds a `\documentclass` `.tex`, else the sibling repo on line 1 of `./.research/paper-repo`. Report the URL it prints.
4. Tell the user both feedback paths:
   - In-repo: comments live in the **paper repo's** `.texreview/comments.json`, each carrying the quote plus its `file:line` (SyncTeX-resolved for PDF selections, known outright for source ones) - asking an agent in that repo to "read .texreview/comments.json and address the comments" works with no export. When YOU address a comment as the agent, update its entry (match by id): set `"resolved": true`, add a one-sentence `"reply"` describing the fix, and a `"fixed"` field quoting a short exact snippet of the new LaTeX - after the next compile the UI highlights where the fix landed.
   - External: the Export button copies open comments (with ids, `file:line` targets, and the same reply instructions) for pasting into any AI.

## Completion
Report the URL and note the server runs until stopped (Ctrl-C in its terminal, or kill the background job). End with: `Next: address the comments in the paper repo (any agent), then Recompile - or /research.review for a full mock review.`
