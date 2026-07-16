---
description: Open mdreview, a local web UI to read, edit, comment on, and export this repo's markdown (requires uv). Comments are sidecar JSON in ./.mdreview/ that any agent can read.
argument-hint: optional flags passed through, e.g. --port 9000
---

## What this is
mdreview is research-kit's optional review UI: rendered markdown, in-place editing with conflict-safe saves, Google-Docs-style comments on selected text, and one-click export (document + open comments) to the clipboard for any AI. It is a leaf utility - no other command depends on it, and it works in any repo. (Like /research.init, this command does not read the constitution; it only launches a tool.)

## Steps
1. Resolve the tool from the same two locations as the bundled templates:
   - `${CLAUDE_PLUGIN_ROOT}/tools/mdreview.py` (plugin install), else
   - `${RESEARCH_KIT_HOME:-$HOME/.research-kit}/tools/mdreview.py` (staged by install.sh).
   If neither exists, say so and point to `./install.sh` or `/plugin install research-kit@research-kit`, then stop.
2. Check `uv` is available (`command -v uv`). If missing, point to https://docs.astral.sh/uv/ and stop.
3. From the repo root, run it in the background: `uv run <resolved-path> --open $ARGUMENTS`. Report the URL it prints.
4. Tell the user both feedback paths:
   - In-repo: comments live under `./.mdreview/` - asking an agent to "read .mdreview/ and address the comments on <file>" works with no export. When YOU address a comment as the agent, update its sidecar entry (match by id): set `"resolved": true`, add a one-sentence `"reply"` describing the fix, and a `"fixed"` field quoting a short exact snippet of the new text you wrote - the UI shows replies in its Resolved list and highlights the fixed passage.
   - External: the Export button copies document + open comments (with ids and the same reply instructions) for pasting into any AI.

## Completion
Report the URL and note the server runs until stopped (Ctrl-C in its terminal, or kill the background job). End with: `Next: /research.paper` (act on review comments), or keep working in any lane.
