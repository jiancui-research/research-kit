---
description: Open mdreview, a local web UI for this repo's markdown: one wide pane you revise directly in the rendered view, or `split` for source beside preview. Comments are sidecar JSON in ./.mdreview/ that any agent can read (requires uv).
argument-hint: (none) for the one-pane layout, `split` for source beside preview; any other flags pass through, e.g. `split --port 9000`
---

## User input
`$ARGUMENTS` selects the layout and passes everything else to the tool. A leading bare word
`split` (or a `--split` flag) opens the two-pane layout; anything else is forwarded untouched.

## What this is
mdreview is research-kit's optional review UI, in two layouts over the same server and the same
`./.mdreview/` comments.

**One pane (default).** The rendered document, which you edit in place:

- **Click any paragraph, heading, list item, table row or code block and it becomes just that markdown**, ready to edit. One task in a 30-item queue opens as that one task, and one row of `claims.md` as that one row - not the whole list or table. Click away or press Esc and it renders again. Only the lines you touched are rewritten, because the source range comes from the markdown parser rather than from converting HTML back to markdown - so tables, spacing and raw HTML elsewhere in the file are never reflowed.
- A `Preview / Markdown` toggle swaps the pane for the full source editor (line numbers, syntax colour) when you need the raw file. Raw HTML blocks are the one thing you cannot click to edit; use the Markdown tab for those.

**Split (`split`).** Raw markdown left with line numbers and syntax colour, rendered preview
right, click-to-source sync, draggable divider. Reach for it when seeing source and result at
once is the point - writing a table, checking structure, editing raw markdown at length.

Both layouts share Google-Docs-style comments on selected rendered text, conflict-safe saves,
and one-click export (document + open comments) for any AI. Editing is in-memory until you save:
`Save` (or `⌘S`) writes to disk, so nothing lands in the file behind your back.

It is a leaf utility - no other command depends on it, and it works in any repo. (Like /research.init, this command does not read the constitution; it only launches a tool.)

## Steps
1. Resolve the tool from the same three locations as the bundled templates:
   - `${CLAUDE_PLUGIN_ROOT}/tools/mdreview.py` (Claude Code plugin install), else
   - `<installPath>/tools/mdreview.py`, where `installPath` comes from the enabled `research-kit@research-kit` entry in the nearest project-scoped `.omp/plugins/installed_plugins.json`, falling back to `~/.omp/plugins/installed_plugins.json` (OMP plugin install), else
   - `${RESEARCH_KIT_HOME:-$HOME/.research-kit}/tools/mdreview.py` (staged by `install.sh`).
   If none exists, say so and point to `./install.sh`, `/plugin install research-kit@research-kit`, or `/marketplace install research-kit@research-kit`, then stop.
2. Check `uv` is available (`command -v uv`). If missing, point to https://docs.astral.sh/uv/ and stop.
3. Read the layout off `$ARGUMENTS`: strip a leading bare `split` (or a `--split` flag) and keep it as the `--split` option; whatever remains is passed through as-is.
   From the repo root, run it in the background: `uv run <resolved-path> [--split] --open <remaining arguments>`. Report the URL it prints, and which layout opened.
4. Tell the user both feedback paths:
   - In-repo: comments live under `./.mdreview/` - asking an agent to "read .mdreview/ and address the comments on <file>" works with no export. When YOU address a comment as the agent, update its sidecar entry (match by id): set `"resolved": true`, add a one-sentence `"reply"` describing the fix, and a `"fixed"` field quoting a short exact snippet of the new text you wrote - the UI shows replies in its Resolved list and highlights the fixed passage.
   - External: the Export button copies document + open comments (with ids and the same reply instructions) for pasting into any AI.

## Completion
Report the URL, which layout opened, and that the server runs until stopped (Ctrl-C in its terminal, or kill the background job). A running instance of one layout is never reused for the other. End with: `Next: /research.implement paper <section>` (act on manuscript comments), or keep working in any lane. Mention the other layout once - `/research.mdreview split` for source beside preview, or plain `/research.mdreview` for the one pane you edit in directly.
