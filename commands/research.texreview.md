---
description: "Open texreview, a local web UI to review the compiled paper - LaTeX source left, PDF right, SyncTeX click-to-source, comments on selections in either pane (button, `⌘⇧M`, or right-click) (requires uv + a TeX install). Comments are sidecar JSON in the paper repo's .texreview/ that any agent can read."
argument-hint: "optional flags passed through, e.g. --main paper.tex --port 9000"
---

## Preparation

Resolve `<bundle>` from the enclosing installed plugin directory (the skill adapter
supplies it), else `${CLAUDE_PLUGIN_ROOT}`, else the enabled OMP `installPath` in
the nearest project `.omp/plugins/installed_plugins.json` or `~/.omp/plugins/installed_plugins.json`,
else `${RESEARCH_KIT_HOME:-$HOME/.research-kit}`. Use the first candidate containing
`guides/setup.md` and `templates/`; name the installation problem if none resolves.
Read `<bundle>/guides/setup.md` and complete its setup for this command, then resume
the request. Internal guides use this bundle; artifact templates use local copies.

## What this is
texreview is research-kit's optional manuscript review UI - a single-user local Overleaf with the review loop built in: editable LaTeX source on the left, the compiled PDF on the right, SyncTeX sync in both directions (click PDF text to jump to its source line; Reveal flashes the PDF box for the cursor line), Google-Docs-style comments on a selection in **either** pane - right-click the selection to comment - each recording its `file:line` target, Overleaf-style `⌘B`/`⌘I` wrapping the selection in `\textbf{}`/`\textit{}`, a Recompile button (`latexmk -pdf -synctex=1`), and one-click export of open comments for any AI. It is a leaf utility - no other command depends on it. (This command only launches a tool; it does not create project settings.)

## Steps
1. Use `<bundle>/tools/texreview.py` from Preparation. If it is absent, report the missing tool and ask the user to repair the research-kit installation. Do not create `.research/` to launch a viewer.
2. Check `uv` is available (`command -v uv`). If missing, point to https://docs.astral.sh/uv/ and stop. If `latexmk` is missing, warn that Recompile and SyncTeX need a TeX install (MacTeX / TeX Live) but continue.
3. Run it in the background: `uv run <resolved-path> --open $ARGUMENTS`. The tool finds the manuscript itself: the current repo if it holds a `\documentclass` `.tex`, else the sibling repo on line 1 of `./.research/paper-repo`. Report the URL it prints.
4. Tell the user both feedback paths:
   - In-repo: comments live in the **paper repo's** `.texreview/comments.json`, each carrying the quote plus its `file:line` (SyncTeX-resolved for PDF selections, known outright for source ones) - asking an agent in that repo to "read .texreview/comments.json and address the comments" works with no export. When YOU address a comment as the agent, update its entry (match by id): set `"resolved": true`, add a one-sentence `"reply"` describing the fix, and a `"fixed"` field quoting a short exact snippet of the new LaTeX - after the next compile the UI highlights where the fix landed.
   - External: the Export button copies open comments (with ids, `file:line` targets, and the same reply instructions) for pasting into any AI.

## Completion
Report the URL and note the server runs until stopped (Ctrl-C in its terminal, or kill the background job). End with: `Next: address the comments in the paper repo (any agent), then Recompile - or /research.review for a full mock review.`
