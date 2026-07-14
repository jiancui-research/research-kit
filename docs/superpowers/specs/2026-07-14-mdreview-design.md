# mdreview design

Date: 2026-07-14. Status: approved by user; form factor revised same day (part of research-kit, not a separate repo) at user direction.

## Purpose

A local, single-user web UI for reviewing markdown documents in any repo: read them rendered, edit and save them back to disk, attach Google-Docs-style comments to selected text, and export document + comments to the clipboard to feed an external AI. Primary use case: research-kit paper repos (`.research/`, `paper/`), but the tool is repo-agnostic.

## Form factor and distribution

- Lives in research-kit as `tools/mdreview.py`: one file, PEP 723 inline metadata, `dependencies = ["markdown"]`, run with `uv run tools/mdreview.py [--port N] [--open] [--root DIR]`. Prerequisite: `uv`.
- Distributed exactly like the templates: `install.sh` stages `tools/` to `${RESEARCH_KIT_HOME:-$HOME/.research-kit}/tools`; the plugin ships it at `${CLAUDE_PLUGIN_ROOT}/tools`. Uninstall removes it with the bundle home.
- Launched by a normal command, `commands/research.mdreview.md`, which resolves the tool from either location (mirroring `research.init` template resolution) and runs it in the current repo. Because it is a plain markdown command, it reaches Claude Code, Codex CLI, and Copilot CLI through the existing install paths.
- The pipeline does not depend on it: mdreview is an optional leaf utility. CLAUDE.md's "no machinery" gotcha and CONTRIBUTING get a one-line carve-out stating this exception and why.
- Server: stdlib `http.server`, bound to `127.0.0.1` only, default port 8377 (auto-increment if taken, with a printed notice). UI is one embedded HTML/CSS/JS template; no frontend build, no client-side markdown engine.

## File scope

Serve every `*.md` under the launch directory, recursively, skipping `.git`, `node_modules`, `.venv`, and `.mdreview`. Hidden directories like `.research` are included. Sidebar shows a collapsible tree.

## UI model: rendered-first with edit toggle

- Default view: server-rendered markdown (python-markdown, extensions: `tables`, `fenced_code`).
- `Edit` swaps the document for a full-document plain textarea. `Save` POSTs and returns to the rendered view; `Cancel` discards. Cmd/Ctrl-S also saves.
- No live preview and no autosave in v1.
- Commented spans are highlighted in the rendered view; clicking one focuses its card in a right-hand comments panel (text, timestamp, resolve toggle, delete).
- Selecting text in the rendered view shows an "Add comment" popover.

## Comments

- Storage: sidecar JSON per document at `<repo>/.mdreview/<relpath>.json`. Markdown files stay clean. Committing or gitignoring `.mdreview/` is the user's choice.
- Schema per comment: `{id, quote, prefix, suffix, comment, created, resolved}`.
- Anchoring: text-quote against the rendered text (exact quote plus ~30 chars of prefix/suffix context, Hypothesis-style). Re-anchored by search on each render; if the quote no longer exists after an edit, the comment appears in the panel marked orphaned rather than vanishing.
- v1 has no threads or replies: flat comments with a resolved flag.

## Save semantics

- Atomic write (temp file + rename).
- Conflict guard: client sends the mtime it loaded; if the on-disk file is newer (edited in parallel by the user or an AI agent), the server refuses (409) and the UI offers reload vs overwrite.
- Undo story is git; the tool keeps no history of its own.

## Export

Per-document `Export` copies to the clipboard: a one-line preamble ("Review this document; address the inline reviewer comments."), the full markdown source, then a `## Reviewer comments` section listing each unresolved comment as a numbered `> "quoted text"` plus the note. For Claude Code no export is needed: the sidecar lives in-repo, so "read `.mdreview/` and address the comments" works directly; the command file mentions this.

## Error handling

- Path traversal blocked: every resolved path must stay under the launch root.
- Files over 2 MB and non-UTF-8 files refused with a clear message.
- Comment writes are atomic like document saves.

## Out of scope for v1

Threads/replies, multi-user, auth, images/uploads, WYSIWYG editing, file watching for external changes, markdown flavors beyond tables + fenced code.

## Testing

- `pytest` for the server core (`tools/test_mdreview.py`, run via `uv run --with pytest,markdown pytest tools/test_mdreview.py`): pure functions and the `route()` dispatcher, so tests need no sockets. No test config lands in the repo; the command line carries the dependencies.
- Manual UI verification against the `codary` repo as fixture.
- research-kit's existing validation loop (`install.sh --all` / `--uninstall` in scratch dirs) must stay clean with `tools/` staged.

## research-kit integration checklist

README Commands table row, `docs/workflow.md` auxiliary mention, `docs/design.md` command list, CLAUDE.md machinery carve-out, CONTRIBUTING carve-out, plugin version bump to 0.5.0.
