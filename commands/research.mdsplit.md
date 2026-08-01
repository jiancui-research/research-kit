---
description: Open the source-beside-preview markdown UI: raw markdown on the left, rendered preview on the right, comments on the rendered text (requires uv). Same comments as /research.mdreview.
argument-hint: optional flags passed through, e.g. --port 9000
---

## What this is
The two-pane layout of research-kit's markdown review UI: raw markdown source on the left (line numbers, syntax colour), the rendered preview on the right, comments on selected rendered text, and one-click export for any AI. Use it when you want to see source and result at the same time - writing a table, checking structure, or editing raw markdown at length. For reading and revising prose, `/research.mdreview` gives one wide pane you edit in directly.

Both commands are the same tool and the same `./.mdreview/` comments; only the layout differs. It is a leaf utility - no other command depends on it, and it works in any repo. (Like /research.init, this command does not read the constitution; it only launches a tool.)

## Steps
1. Resolve the tool from the same three locations as the bundled templates:
   - `${CLAUDE_PLUGIN_ROOT}/tools/mdreview.py` (Claude Code plugin install), else
   - `<installPath>/tools/mdreview.py`, where `installPath` comes from the enabled `research-kit@research-kit` entry in the nearest project-scoped `.omp/plugins/installed_plugins.json`, falling back to `~/.omp/plugins/installed_plugins.json` (OMP plugin install), else
   - `${RESEARCH_KIT_HOME:-$HOME/.research-kit}/tools/mdreview.py` (staged by `install.sh`).
   If none exists, say so and point to `./install.sh`, `/plugin install research-kit@research-kit`, or `/marketplace install research-kit@research-kit`, then stop.
2. Check `uv` is available (`command -v uv`). If missing, point to https://docs.astral.sh/uv/ and stop.
3. From the repo root, run it in the background: `uv run <resolved-path> --split --open $ARGUMENTS`. Report the URL it prints.
4. Tell the user both feedback paths:
   - In-repo: comments live under `./.mdreview/` - asking an agent to "read .mdreview/ and address the comments on <file>" works with no export. When YOU address a comment as the agent, update its sidecar entry (match by id): set `"resolved": true`, add a one-sentence `"reply"` describing the fix, and a `"fixed"` field quoting a short exact snippet of the new text you wrote - the UI shows replies in its Resolved list and highlights the fixed passage.
   - External: the Export button copies document + open comments (with ids and the same reply instructions) for pasting into any AI.

## Completion
Report the URL and note the server runs until stopped (Ctrl-C in its terminal, or kill the background job). End with: `Next: /research.implement paper <section>` (act on manuscript comments), or keep working in any lane. Mention `/research.mdreview` for the one-pane layout you edit in directly.
