#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown-it-py"]
# ///
"""mdreview: a local web UI to read, edit, comment on, and export a repo's markdown.

Part of research-kit (an optional leaf tool - nothing in the pipeline depends on it).
Run from any repo root:  uv run tools/mdreview.py [--port N] [--open] [--root DIR]
Comments are sidecar JSON under the target repo's .mdreview/ - markdown files stay clean.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import time
import urllib.request
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from markdown_it import MarkdownIt

SKIP_DIRS = {".git", "node_modules", ".venv", ".mdreview", ".pytest_cache", "__pycache__"}
MAX_BYTES = 2 * 1024 * 1024
MAX_IMAGE_BYTES = 10 * 1024 * 1024
SIDECAR_DIR = ".mdreview"
# Which UI the browser gets. "review" (/research.mdreview) is one pane you edit in the
# rendered view; "split" (/research.mdsplit) is the source-beside-preview layout. Both
# share this server and the same .mdreview/ comment sidecars.
UI_MODE = "review"
# Nested blocks that are still a self-contained slice of source, so clicking one task in
# a 30-item queue edits that task rather than the whole list. The UI targets the
# innermost tagged element, and these ranges nest inside their parent block's range.
FINE_BLOCKS = {"list_item_open", "tr_open"}
# A server bakes its HTML in at startup, so one left running after the tool is updated
# keeps serving the old UI. Fingerprint the source so a stale instance is not reused.
try:
    BUILD = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]
except OSError:
    BUILD = "unknown"
IMAGE_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "svg": "image/svg+xml",
    "webp": "image/webp",
}


class RequestError(Exception):
    """An error with an HTTP status, raised by core functions, mapped by route()."""

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def safe_resolve(root: Path, rel: str) -> Path:
    """Resolve rel under root; refuse anything that escapes root."""
    p = (root / rel).resolve()
    if not p.is_relative_to(root.resolve()):
        raise RequestError(400, f"path escapes root: {rel}")
    return p


def list_md_files(root: Path) -> list[str]:
    """All *.md under root (relative paths), pruning SKIP_DIRS, files before subdirs."""
    out: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for f in sorted(filenames):
            if f.endswith(".md"):
                out.append((Path(dirpath) / f).relative_to(root).as_posix())
    return out


def read_doc(root: Path, rel: str) -> dict:
    """Read a UTF-8 markdown file under root; refuse missing, huge, or binary files."""
    p = safe_resolve(root, rel)
    if not p.is_file():
        raise RequestError(404, f"no such file: {rel}")
    if p.stat().st_size > MAX_BYTES:
        raise RequestError(413, f"file over {MAX_BYTES // (1024 * 1024)} MB: {rel}")
    try:
        content = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise RequestError(415, f"not UTF-8 text: {rel}")
    return {"content": content, "mtime": p.stat().st_mtime}


def _atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".mdreview-tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def write_doc(root: Path, rel: str, content: str, expected_mtime: float | None) -> dict:
    """Atomically save content. 409 if the file changed since expected_mtime (None skips)."""
    p = safe_resolve(root, rel)
    if p.exists() and expected_mtime is not None and abs(p.stat().st_mtime - expected_mtime) > 1e-6:
        raise RequestError(409, "file changed on disk since it was loaded")
    _atomic_write(p, content)
    return {"mtime": p.stat().st_mtime}


def _comments_path(root: Path, rel: str) -> Path:
    safe_resolve(root, rel)  # validates rel; the sidecar mirrors it
    return root / SIDECAR_DIR / (rel + ".json")


def load_comments(root: Path, rel: str) -> list[dict]:
    cp = _comments_path(root, rel)
    if not cp.is_file():
        return []
    return json.loads(cp.read_text(encoding="utf-8"))


def _save_comments(root: Path, rel: str, comments: list[dict]) -> None:
    _atomic_write(_comments_path(root, rel), json.dumps(comments, ensure_ascii=False, indent=1))


def add_comment(root: Path, rel: str, quote: str, prefix: str, suffix: str, comment: str) -> dict:
    entry = {
        "id": uuid.uuid4().hex[:12],
        "quote": quote,
        "prefix": prefix,
        "suffix": suffix,
        "comment": comment,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "resolved": False,
    }
    comments = load_comments(root, rel)
    comments.append(entry)
    _save_comments(root, rel, comments)
    return entry


def _find_comment(comments: list[dict], cid: str) -> dict:
    for c in comments:
        if c["id"] == cid:
            return c
    raise RequestError(404, f"no such comment: {cid}")


def update_comment(root: Path, rel: str, cid: str, fields: dict) -> dict:
    comments = load_comments(root, rel)
    c = _find_comment(comments, cid)
    for k in ("resolved", "comment", "reply", "fixed"):
        if k in fields:
            c[k] = fields[k]
    _save_comments(root, rel, comments)
    return c


def delete_comment(root: Path, rel: str, cid: str) -> None:
    comments = load_comments(root, rel)
    c = _find_comment(comments, cid)
    comments.remove(c)
    _save_comments(root, rel, comments)


# CommonMark semantics (2-space list nesting, GitHub-style) + GFM tables/strikethrough
_md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")


def render_md(text: str) -> str:
    """Render, tagging every top-level block with the source lines it came from.

    These `data-l0`/`data-l1` attributes are what lets the review UI turn a rendered
    paragraph back into exactly its markdown source, so editing in the rendered view
    never needs an HTML-to-markdown conversion. They are inert everywhere else.
    Raw `html_block` content renders verbatim and cannot carry attributes, so those
    blocks are the one kind that stays uneditable in the rendered view.
    """
    tokens = _md.parse(text)
    for t in tokens:
        if t.map and (t.level == 0 or t.type in FINE_BLOCKS):
            t.attrSet("data-l0", str(t.map[0]))
            t.attrSet("data-l1", str(t.map[1]))
    return _md.renderer.render(tokens, _md.options, {})


def export_text(root: Path, rel: str) -> str:
    """Document + unresolved comments as one AI-ready markdown blob with a reply loop."""
    doc = read_doc(root, rel)
    open_comments = [c for c in load_comments(root, rel) if not c["resolved"]]
    sidecar = f"{SIDECAR_DIR}/{rel}.json"
    parts = [
        "Review this document and address each reviewer comment listed at the end.",
        f"- If you can edit this repository: apply your fixes to `{rel}`, then for each",
        f'  comment you addressed, update its entry in `{sidecar}` (match by id): set',
        f'  `"resolved": true`, add a one-sentence `"reply"` describing the fix, and a',
        f'  `"fixed"` field quoting a short exact snippet of the NEW text you wrote,',
        "  so the UI can highlight where the fix landed.",
        "- If you cannot edit files: return the revised document, then end with a",
        "  RESOLUTIONS block, one line per addressed comment, formatted",
        "  `<id>: <one-sentence reply>`, so an in-repo agent can apply it.",
        "",
        "---",
        "",
        doc["content"].rstrip(),
        "",
    ]
    if open_comments:
        parts += ["---", "", "## Reviewer comments", ""]
        for i, c in enumerate(open_comments, 1):
            parts.append(f'{i}. [id: {c["id"]}] > "{c["quote"]}"')
            parts.append(f"   {c['comment']}")
            parts.append("")
    return "\n".join(parts)


PAGE = r"""<!doctype html>
<html><head><meta charset="utf-8"><title>mdreview</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  /* Catppuccin: Latte by day, Mocha by night. Follows the OS unless you pick one. */
  :root {
    --bg:#eff1f5; --bg-alt:#e6e9ef; --surface:#fff; --raised:#dce0e8;
    --line:#ccd0da; --text:#4c4f69; --muted:#6c6f85; --faint:#9ca0b0;
    --accent:#1e66f5; --accent-soft:#dce4fb; --on-accent:#fff;
    --code-bg:#e6e9ef; --shadow:rgba(76,79,105,.22); --sel:rgba(30,102,245,.3);
    --hl:rgba(223,142,29,.3); --hl-strong:rgba(254,100,11,.55);
    --ok:#40a02b; --ok-soft:rgba(64,160,43,.16); --ok-line:#a6d29a; --warn:#df8e1d;
    --md-head:#1e66f5; --md-mark:#7c7f93; --md-code:#40a02b;
    --md-link:#179299; --md-comment:#8c8fa1;
  }
  :root[data-theme="dark"] {
    --bg:#1e1e2e; --bg-alt:#181825; --surface:#313244; --raised:#45475a;
    --line:#45475a; --text:#cdd6f4; --muted:#a6adc8; --faint:#7f849c;
    --accent:#89b4fa; --accent-soft:#313d57; --on-accent:#11111b;
    --code-bg:#181825; --shadow:rgba(0,0,0,.5); --sel:rgba(137,180,250,.32);
    --hl:rgba(249,226,175,.28); --hl-strong:rgba(250,179,135,.6);
    --ok:#a6e3a1; --ok-soft:rgba(166,227,161,.16); --ok-line:#57794f; --warn:#f9e2af;
    --md-head:#89b4fa; --md-mark:#9399b2; --md-code:#a6e3a1;
    --md-link:#94e2d5; --md-comment:#6c7086;
  }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
         color:var(--text); background:var(--bg); }
  #app { display:grid; grid-template-columns:230px 1fr 6px 1fr 300px; height:100vh; }
  /* grid/flex items default to min-height:auto, so a long document would stretch the
     grid past 100vh and scroll the page (taking the toolbars with it); force pane scrolling */
  #app > * { min-width:0; min-height:0; }
  #main, #edarea { min-height:0; }
  /* review mode: one wide centre column, [Preview | Markdown] switching which pane
     occupies it. split mode carries no data-mode, so none of this applies to it. */
  [data-mode="review"] #app { grid-template-columns:230px 1fr 300px;
                              grid-template-rows:auto 1fr; }
  [data-mode="review"] #sidewrap { grid-column:1; grid-row:1 / span 2; }
  [data-mode="review"] #rbar { grid-column:2; grid-row:1; display:flex; }
  [data-mode="review"] #srcpane, [data-mode="review"] #main { grid-column:2; grid-row:2; }
  [data-mode="review"] #panel { grid-column:3; grid-row:1 / span 2; }
  [data-mode="review"] #gutter, [data-mode="review"] #bar,
  [data-mode="review"] #docctl { display:none; }
  [data-mode="review"] #srcpane { display:none; }
  [data-mode="review"] #app.showsrc #srcpane { display:flex; }
  [data-mode="review"] #app.showsrc #main { display:none; }
  [data-mode="review"] #doc { max-width:820px; margin:0 auto; }
  #seg { display:inline-flex; border:1px solid var(--line); border-radius:7px;
         overflow:hidden; background:var(--surface); }
  #seg button { border:0; border-radius:0; background:none; color:var(--muted);
                padding:4px 14px; cursor:pointer; font:13px inherit; }
  #seg button.on { background:var(--accent-soft); color:var(--accent); font-weight:600; }
  /* a rendered block invites a click only when it can actually be edited */
  [data-mode="review"] #doc [data-l0] { border-radius:5px; }
  /* highlight the innermost editable thing under the pointer, so hovering one task in
     a list offers that task rather than the whole list */
  [data-mode="review"] #doc [data-l0]:hover:not(:has([data-l0]:hover)) {
        background:var(--raised); box-shadow:0 0 0 3px var(--raised); }
  [data-mode="review"] #doc pre:has(> [data-l0]:hover) {
        background:var(--raised); box-shadow:0 0 0 3px var(--raised); }
  [data-mode="review"] #doc tr[data-l0]:hover:not(:has([data-l0]:hover)) { box-shadow:none; }
  #doc li > textarea.blockedit { margin:2px 0; }
  #doc textarea.blockedit { display:block; width:100%; font:13px/1.6 ui-monospace,Menlo,monospace;
        color:var(--text); background:var(--bg-alt); border:1px solid var(--accent);
        border-radius:6px; padding:9px 11px; resize:none; outline:none; }
  #gutter { cursor:col-resize; background:var(--bg-alt); border-left:1px solid var(--line);
            border-right:1px solid var(--line); }
  #gutter:hover, #gutter.dragging { background:var(--accent); }
  #side { border-right:1px solid var(--line); overflow-y:auto; padding:10px; font-size:13px; }
  #sidewrap { background:var(--bg-alt); }
  #scope { display:none; font-size:12px; color:var(--muted); margin-bottom:8px; user-select:none; }
  #side .dir { font-weight:600; margin-top:6px; color:var(--muted); }
  #side .dir .count { font-weight:400; color:var(--faint); }
  #side button { display:block; width:100%; text-align:left; border:0; background:none;
                 padding:3px 6px; border-radius:5px; cursor:pointer; font:inherit; color:var(--text); }
  #side button:hover { background:var(--raised); }
  #side button.active { background:var(--accent-soft); color:var(--accent); }
  #srcpane { display:flex; flex-direction:column; min-width:0; }
  #bar, #rbar { display:flex; gap:8px; align-items:center; padding:9px 12px;
         border-bottom:1px solid var(--line); background:var(--bg-alt); }
  #rbar { display:none; }
  #bar .path, #rbar .path { font-weight:600; font-size:13px; margin-right:auto; overflow:hidden;
               text-overflow:ellipsis; white-space:nowrap; }
  #bar button, #rbar button { border:1px solid var(--line); background:var(--surface); color:var(--text);
                border-radius:6px; padding:4px 11px; cursor:pointer; font:13px inherit; }
  #bar button:hover, #rbar button:hover { border-color:var(--accent); color:var(--accent); }
  /* A textarea cannot paint line numbers or syntax colour, so an identically wrapped
     mirror div sits under a transparent textarea and paints both. Sizes are in em so
     the A+/A- control scales the gutter with the text. */
  #edarea { position:relative; flex:1; font:13px/1.55 ui-monospace,Menlo,monospace; }
  #gutterbg { position:absolute; left:0; top:0; bottom:0; width:3.6em;
              background:var(--bg-alt); border-right:1px solid var(--line); }
  #editor, #mirror { position:absolute; inset:0; margin:0; border:0; font:inherit;
            padding:14px 16px 14px 4.6em; white-space:pre-wrap; overflow-wrap:break-word; }
  #mirror { overflow:hidden; pointer-events:none; color:var(--text); }
  #mirror .row { position:relative; }
  #mirror .row::before { content:attr(data-n); position:absolute; left:-4.2em; width:3em;
            text-align:right; color:var(--faint); }
  /* syntax colours only - bold or italic would change glyph widths and desync the
     mirror from the textarea it sits under */
  #mirror .th { color:var(--md-head); }
  #mirror .tb { color:var(--md-mark); }
  #mirror .tc { color:var(--md-code); }
  #mirror .tu { color:var(--md-link); }
  #mirror .tq { color:var(--md-comment); }
  /* the mirror paints the text; the textarea keeps only the caret and the selection */
  #editor { outline:none; resize:none; overflow:auto; background:transparent;
            color:transparent; caret-color:var(--accent); }
  #editor::placeholder { color:var(--faint); }
  #editor::selection { background:var(--sel); }
  #edarea.composing #editor { color:var(--text); }
  #edarea.composing #mirror, #edarea.composing #mirror * { color:transparent; }
  #main { overflow-y:auto; padding:22px 30px; min-width:0; background:var(--bg); }
  #doc { max-width:720px; }
  #doc h1,#doc h2,#doc h3 { line-height:1.3; }
  #doc pre { background:var(--code-bg); padding:10px; border-radius:6px; overflow-x:auto; }
  #doc code { background:var(--code-bg); padding:1px 4px; border-radius:4px; font-size:90%; }
  #doc table { border-collapse:collapse; } #doc td,#doc th { border:1px solid var(--line); padding:4px 9px; }
  #doc blockquote { border-left:3px solid var(--line); margin-left:0; padding-left:14px; color:var(--muted); }
  #doc img { max-width:100%; }
  #doc a { color:var(--accent); }
  #doc mark { background:var(--hl); color:inherit; cursor:pointer;
              border-bottom:2px solid var(--hl-strong); }
  @keyframes flashbg { 0%,100% { background:transparent; } 50% { background:var(--hl-strong); } }
  #doc span.flash, #doc mark.flash { animation: flashbg .55s ease-in-out 3; border-radius:3px; }
  #doc .mermaid { position:relative; }
  .zoombtn { position:absolute; top:6px; right:6px; opacity:0; transition:opacity .15s;
             border:1px solid var(--line); background:var(--surface); color:var(--text);
             border-radius:6px; padding:2px 8px; cursor:pointer; font-size:14px; }
  #doc .mermaid:hover .zoombtn { opacity:1; }
  #overlay { position:fixed; inset:0; background:rgba(17,17,27,.72); display:none;
             align-items:center; justify-content:center; z-index:30; }
  #stage { background:var(--surface); border-radius:10px; padding:24px; width:86vw; height:86vh;
           overflow:hidden; cursor:grab; display:flex; align-items:center; justify-content:center; }
  #stage svg { width:100%; height:auto; max-width:none; }
  #zctrl { position:fixed; top:18px; right:22px; display:flex; gap:6px; z-index:31; }
  #zctrl button { border:0; background:var(--surface); color:var(--text); border-radius:7px;
                  padding:6px 13px; cursor:pointer; font:15px inherit; }
  #panel { border-left:1px solid var(--line); overflow-y:auto; padding:12px; font-size:13px;
           background:var(--bg-alt); }
  #panelHead { display:flex; align-items:center; justify-content:space-between;
               font-weight:600; margin-bottom:10px; }
  #panelHead button { border:1px solid var(--line); background:var(--surface); color:var(--text);
                      border-radius:6px; padding:4px 11px; cursor:pointer; font:13px inherit; }
  #panelHead button:hover { border-color:var(--accent); color:var(--accent); }
  #doc mark.resolvedmark { background:var(--ok-soft); border-bottom:2px solid var(--ok-line); }
  .card .q:hover { text-decoration:underline; }
  .card { border:1px solid var(--line); border-radius:8px; padding:9px 11px; margin-bottom:9px;
          background:var(--surface); }
  .card.resolved { opacity:.6; }
  .card .q { color:var(--muted); font-style:italic; display:block; margin-bottom:5px;
             white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .card .orphan { color:var(--warn); font-size:11px; font-weight:600; }
  .card .reply { color:var(--ok); font-style:italic; margin-top:5px; }
  .card .editbox { width:100%; height:56px; font:inherit; border:1px solid var(--accent);
                   border-radius:5px; padding:5px; margin-top:2px;
                   background:var(--bg); color:var(--text); }
  details.resolvedlist { margin-top:12px; }
  details.resolvedlist summary { cursor:pointer; color:var(--muted); font-weight:600;
                                 font-size:12px; margin-bottom:8px; user-select:none; }
  .card .meta { color:var(--faint); font-size:11px; margin-top:5px; display:flex; gap:8px; }
  .card .meta button { border:0; background:none; color:var(--accent); cursor:pointer; padding:0; font-size:11px; }
  #pop { position:fixed; display:none; background:var(--surface); border:1px solid var(--line);
         border-radius:8px; box-shadow:0 8px 26px var(--shadow); padding:9px; width:280px; z-index:10; }
  #pop textarea { width:100%; height:64px; font:inherit; border:1px solid var(--line);
                  border-radius:5px; padding:6px; background:var(--bg); color:var(--text); }
  #pop button { margin-top:6px; border:0; background:var(--accent); color:var(--on-accent);
                border-radius:5px; padding:5px 12px; cursor:pointer; font:inherit; font-weight:600; }
  #toast { position:fixed; bottom:18px; left:50%; transform:translateX(-50%);
           background:var(--text); color:var(--bg); border-radius:7px; padding:8px 16px;
           display:none; font-size:13px; z-index:20; box-shadow:0 6px 20px var(--shadow); }
  .fontctl { display:inline-flex; gap:3px; }
  .fontctl button { border:1px solid var(--line); background:var(--surface); border-radius:5px;
                    padding:1px 7px; cursor:pointer; font-size:11px; color:var(--muted); }
  .fontctl button:hover { border-color:var(--accent); color:var(--accent); }
  #themeBtn { border:1px solid var(--line); background:var(--surface); color:var(--muted);
              border-radius:5px; padding:1px 8px; cursor:pointer; font-size:12px; }
  #themeBtn:hover { border-color:var(--accent); color:var(--accent); }
  #docctl { position:sticky; top:0; justify-content:flex-end; display:flex; z-index:5;
            margin-bottom:2px; }
  #panelToggle.off { opacity:.4; }
  .empty { color:var(--faint); }
</style></head><body>
<div id="app">
  <nav id="sidewrap" style="overflow-y:auto; border-right:1px solid var(--line);">
    <div style="padding:10px 10px 0 10px;">
      <label id="scope"><input type="checkbox" id="scopeChk" checked> .research/ only</label>
    </div>
    <div id="side" style="border:0;"></div>
  </nav>
  <div id="rbar" class="bar" style="visibility:hidden">
    <span class="path" id="rpath"></span>
    <span id="seg"><button id="segPrev" class="on">Preview</button><button id="segSrc">Markdown</button></span>
    <span class="fontctl"><button id="rFontDown" data-f="doc" data-d="-1" title="Smaller text">A−</button><button id="rFontUp" data-f="doc" data-d="1" title="Larger text">A+</button></span>
    <button id="rsaveBtn">Save</button>
    <button id="rthemeBtn" title="Light / dark theme">◐</button>
    <button id="rpanelToggle" title="Show / hide the comments panel">💬</button>
  </div>
  <section id="srcpane">
    <div id="bar" style="visibility:hidden">
      <span class="path" id="path"></span>
      <span class="fontctl"><button data-f="editor" data-d="-1" title="Smaller editor text">A−</button><button data-f="editor" data-d="1" title="Larger editor text">A+</button></span>
      <button id="saveBtn">Save</button>
      <button id="revealBtn" title="Blink the preview text matching the cursor position">Reveal →</button>
    </div>
    <div id="edarea">
      <div id="gutterbg"></div>
      <div id="mirror" aria-hidden="true"></div>
      <textarea id="editor" spellcheck="false" placeholder="Pick a file on the left."></textarea>
    </div>
  </section>
  <div id="gutter" title="drag to resize; double-click to reset"></div>
  <section id="main">
    <div id="docctl" class="fontctl"><button data-f="doc" data-d="-1" title="Smaller preview text">A−</button><button data-f="doc" data-d="1" title="Larger preview text">A+</button><button id="themeBtn" title="Light / dark theme">◐</button><button id="panelToggle" title="Show / hide the comments panel">💬</button></div>
    <article id="doc"><p class="empty">Raw markdown on the left, rendered preview here.
      Click rendered text to jump the cursor to its source. Select rendered text to comment.</p></article>
  </section>
  <aside id="panel">
    <div id="panelHead">
      <span>Comments</span>
      <span class="fontctl"><button data-f="panel" data-d="-1" title="Smaller comments text">A−</button><button data-f="panel" data-d="1" title="Larger comments text">A+</button></span>
      <button id="exportBtn" title="Copy document + open comments (with ids and reply instructions) for any AI">Export</button>
    </div>
    <div id="cards"><p class="empty">Comments appear here.</p></div>
  </aside>
</div>
<div id="pop"><textarea id="popText" placeholder="Comment..."></textarea><br>
  <button id="popAdd">Add comment</button></div>
<div id="overlay">
  <div id="zctrl">
    <button id="zOut" title="zoom out">−</button>
    <button id="zIn" title="zoom in">+</button>
    <button id="zReset" title="reset">reset</button>
    <button id="zClose" title="close">✕</button>
  </div>
  <div id="stage"></div>
</div>
<div id="toast"></div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
const $ = id => document.getElementById(id);

/* ---------- theme: follow the OS until you pick one ---------- */
// paints the theme immediately; mermaid/re-render happen in applyTheme(), which runs
// after `state` exists (this file's declarations below are still in their dead zone)
function setThemeAttr() {
  const saved = localStorage.getItem("mdreview.theme");
  const dark = saved ? saved === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  document.documentElement.dataset.theme = dark ? "dark" : "light";
  const b = document.getElementById("themeBtn");
  if (b) b.textContent = dark ? "☾" : "☀";
  return dark;
}
setThemeAttr();
function applyTheme() {
  const dark = setThemeAttr();
  if (!window.mermaid) return;
  mermaid.initialize({ startOnLoad: false, theme: dark ? "dark" : "neutral",
                       suppressErrorRendering: true });
  if (state) rerender();
}
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
  if (!localStorage.getItem("mdreview.theme")) applyTheme();
});

let state = null;      // {path, mtime, comments:[{...,anchored}]}
let allFiles = [];
let pending = null;    // {quote, prefix, suffix} awaiting comment text
let dirty = false;
let renderTimer = null;

const api = async (url, body) => fetch(url, body ? {method:"POST",
  headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)} : undefined);
const toast = msg => { const t=$("toast"); t.textContent=msg; t.style.display="block";
  setTimeout(()=>t.style.display="none", 2200); };
const setDirty = d => {
  dirty = d;
  for (const id of ["saveBtn", "rsaveBtn"]) $(id).textContent = d ? "Save •" : "Save";
};

/* ---------- sidebar: collapsible folders ---------- */
let collapsed = new Set(JSON.parse(localStorage.getItem("mdreview.collapsed") || "[]"));
async function loadFiles() {
  allFiles = await (await api("/api/files")).json();
  const hasResearch = allFiles.some(f => f.startsWith(".research/"));
  $("scope").style.display = hasResearch ? "block" : "none";
  $("scopeChk").checked = hasResearch;
  renderSidebar();
}
$("scopeChk").onchange = renderSidebar;
function renderSidebar() {
  const only = $("scope").style.display !== "none" && $("scopeChk").checked;
  // toggled: everything the pipeline wrote under .research/ - only the bundled templates are noise
  const files = only
    ? allFiles.filter(f => f.startsWith(".research/") && !f.startsWith(".research/templates/"))
    : allFiles;
  const tree = {};
  for (const f of files) {
    const parts = f.split("/"); let node = tree;
    for (const p of parts.slice(0, -1)) node = (node[p + "/"] ??= {});
    node[parts.at(-1)] = f;
  }
  $("side").innerHTML = "";
  renderTree(tree, $("side"), 0, "");
}
function countFiles(node) {
  let n = 0;
  for (const k of Object.keys(node)) n += k.endsWith("/") ? countFiles(node[k]) : 1;
  return n;
}
function renderTree(node, el, depth, prefix) {
  for (const key of Object.keys(node).sort((a,b)=>a.localeCompare(b))) {
    if (key.endsWith("/")) {
      const path = prefix + key, open = !collapsed.has(path);
      const d = document.createElement("button");
      d.className = "dir";
      d.style.paddingLeft = depth*12 + "px";
      d.append((open ? "▾ " : "▸ ") + key);
      const c = document.createElement("span");
      c.className = "count"; c.textContent = " " + countFiles(node[key]);
      d.appendChild(c);
      d.title = (open ? "Hide " : "Show ") + path;
      d.onclick = () => {
        open ? collapsed.add(path) : collapsed.delete(path);
        localStorage.setItem("mdreview.collapsed", JSON.stringify([...collapsed]));
        renderSidebar();
      };
      el.appendChild(d);
      if (open) renderTree(node[key], el, depth + 1, path);
    } else {
      const b = document.createElement("button");
      b.textContent = key; b.dataset.path = node[key]; b.style.paddingLeft = (depth*12+6) + "px";
      b.classList.toggle("active", state && state.path === node[key]);
      b.onclick = () => openDoc(node[key]);
      el.appendChild(b);
    }
  }
}

/* ---------- document ---------- */
async function openDoc(path) {
  if (dirty && !confirm("Unsaved changes will be lost. Switch file anyway?")) return;
  const res = await api("/api/doc?path=" + encodeURIComponent(path));
  if (!res.ok) { toast((await res.json()).error); return; }
  const d = await res.json();
  state = { path: d.path, mtime: d.mtime, comments: d.comments };
  $("editor").value = d.content;
  queueMirror();
  setDirty(false);
  $("bar").style.visibility = "visible";
  $("rbar").style.visibility = "visible";
  $("rpath").textContent = state.path;
  $("path").textContent = state.path;
  paint(d.html);
  renderSidebar();
}
function paint(html) {
  lastSel = null;   // content changed; stale snapshots must not anchor comments
  $("doc").innerHTML = html;
  fixImagePaths();
  applyHighlights();
  renderMermaid();
  renderPanel();
}
function fixImagePaths() {
  // relative image refs resolve against the DOC's directory (GitHub semantics),
  // not the server root the page is served from
  const dir = state.path.includes("/") ? state.path.slice(0, state.path.lastIndexOf("/") + 1) : "";
  for (const img of $("doc").querySelectorAll("img")) {
    const src = img.getAttribute("src") || "";
    if (/^(https?:|data:|\/)/.test(src)) continue;
    img.src = "/" + dir + src;
  }
}
async function renderMermaid() {
  // ```mermaid fences arrive as <pre><code class="language-mermaid">; swap them for
  // rendered diagrams when mermaid.js loaded (CDN - offline they stay as code blocks)
  if (!window.mermaid) return;
  for (const code of $("doc").querySelectorAll("pre code.language-mermaid")) {
    const div = document.createElement("div");
    div.className = "mermaid";
    div.textContent = code.textContent;
    code.parentElement.replaceWith(div);
  }
  try { await mermaid.run({ nodes: $("doc").querySelectorAll(".mermaid") }); }
  catch (e) { /* invalid diagram mid-typing: leave the source text visible */ }
  for (const div of $("doc").querySelectorAll(".mermaid")) {
    if (div.dataset.zoomable || !div.querySelector("svg")) continue;
    div.dataset.zoomable = "1";
    const b = document.createElement("button");
    b.className = "zoombtn"; b.textContent = "⤢"; b.title = "Enlarge diagram (zoom + pan)";
    b.onclick = () => openDiagram(div.querySelector("svg"));
    div.appendChild(b);
  }
}
async function rerender() {
  if (!state) return;
  const res = await api("/api/render", {content: $("editor").value});
  if (res.ok) paint((await res.json()).html);
}
$("editor").addEventListener("input", () => {
  queueMirror();
  if (!state) return;
  setDirty(true);
  clearTimeout(renderTimer);
  renderTimer = setTimeout(rerender, 450);
});

/* ---------- highlights + comments ---------- */
function textNodesUnder(el) {
  const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), out = [];
  let n; while (n = w.nextNode()) out.push(n);
  return out;
}
function findAnchor(text, c) {
  for (const probe of [(c.prefix||"")+c.quote+(c.suffix||""), (c.prefix||"")+c.quote]) {
    const i = text.indexOf(probe);
    if (i >= 0) return i + (c.prefix||"").length;
  }
  return text.indexOf(c.quote);
}
function wrapTextRange(container, start, end, makeEl) {
  // wrap [start,end) of container's text, segment-wise per text node, with makeEl()
  let pos = 0, first = null;
  for (const node of textNodesUnder(container)) {
    const len = node.length, a = Math.max(start - pos, 0), b = Math.min(end - pos, len);
    if (a < b) {
      const r = document.createRange();
      r.setStart(node, a); r.setEnd(node, b);
      const el = makeEl();
      try { r.surroundContents(el); first = first || el; } catch (e) {}
    }
    pos += len;
    if (pos >= end) break;
  }
  return first;
}
function applyHighlights() {
  const article = $("doc");
  for (const c of state.comments) {
    // resolved comments with a recorded fix anchor on the NEW text; otherwise the original quote
    const target = (c.resolved && c.fixed) ? c.fixed : c.quote;
    const start = (c.resolved && c.fixed)
      ? article.textContent.indexOf(c.fixed)
      : findAnchor(article.textContent, c);
    c.anchored = start >= 0 && target.length > 0;
    if (!c.anchored) continue;
    wrapTextRange(article, start, start + target.length, () => {
      const mk = document.createElement("mark");
      mk.dataset.id = c.id;
      if (c.resolved) mk.className = "resolvedmark";
      mk.onclick = ev => { ev.stopPropagation(); focusCard(c.id); };
      return mk;
    });
  }
}
let resolvedOpen = false;
function commentCard(c) {
  const card = document.createElement("div");
  card.className = "card" + (c.resolved ? " resolved" : "");
  card.id = "card-" + c.id;
  const q = document.createElement("span"); q.className = "q"; q.textContent = '"' + c.quote + '"';
  q.title = "Show this passage in the document";
  q.style.cursor = "pointer";
  q.onclick = () => locateComment(c);
  const body = document.createElement("div"); body.textContent = c.comment;
  card.append(q, body);
  if (c.reply) {
    const rep = document.createElement("div"); rep.className = "reply";
    rep.textContent = "↳ " + c.reply;
    card.appendChild(rep);
  }
  const meta = document.createElement("div"); meta.className = "meta";
  meta.textContent = c.created.slice(0, 16).replace("T", " ") + " ";
  if (!c.anchored && !c.resolved) { const o = document.createElement("span"); o.className = "orphan";
    o.textContent = "orphaned"; meta.appendChild(o); }
  const edit = document.createElement("button");
  edit.textContent = "Edit";
  edit.onclick = () => {
    if (card.querySelector("textarea")) return;
    const ta = document.createElement("textarea");
    ta.value = c.comment;
    ta.className = "editbox";
    body.replaceWith(ta);
    ta.focus();
    ta.addEventListener("keydown", ev => { if (ev.key === "Escape") refreshComments(); });
    edit.textContent = "Save";
    edit.onclick = async () => {
      const v = ta.value.trim();
      if (v && v !== c.comment)
        await api("/api/comment/update", {path: state.path, id: c.id, comment: v});
      refreshComments();
    };
  };
  const res = document.createElement("button");
  res.textContent = c.resolved ? "Reopen" : "Resolve";
  res.onclick = async () => { await api("/api/comment/update",
    {path: state.path, id: c.id, resolved: !c.resolved}); refreshComments(); };
  const del = document.createElement("button");
  del.textContent = "Delete";
  del.onclick = async () => { await api("/api/comment/delete",
    {path: state.path, id: c.id}); refreshComments(); };
  meta.append(edit, res, del);
  card.appendChild(meta);
  return card;
}
function locateComment(c) {
  // chain: anchored mark (fixed or original text) -> stored context -> give up
  const mk = document.querySelector('#doc mark[data-id="' + c.id + '"]');
  if (mk) {
    mk.scrollIntoView({behavior: "smooth", block: "center"});
    mk.classList.add("flash");
    setTimeout(() => mk.classList.remove("flash"), 2000);
    return;
  }
  const text = $("doc").textContent;
  let start = -1, len = 40;
  if (c.prefix) {
    const i = text.indexOf(c.prefix);
    if (i >= 0) start = i + c.prefix.length;
  }
  if (start < 0 && c.suffix) {
    const i = text.indexOf(c.suffix);
    if (i >= 0) { start = Math.max(0, i - 40); len = i - start; }
  }
  if (start < 0 || len <= 0) {
    toast("Can't locate this passage anymore (text and its context both changed)");
    return;
  }
  flashRendered(start, Math.min(len, text.length - start));
}
function renderPanel() {
  const panel = $("cards"); panel.innerHTML = "";
  if (!state.comments.length) {
    panel.innerHTML = '<p class="empty">No comments. Select rendered text to add one.</p>';
    return;
  }
  const open = state.comments.filter(c => !c.resolved);
  const done = state.comments.filter(c => c.resolved);
  for (const c of open) panel.appendChild(commentCard(c));
  if (!open.length) {
    const p = document.createElement("p"); p.className = "empty";
    p.textContent = "No open comments."; panel.appendChild(p);
  }
  if (done.length) {
    const det = document.createElement("details");
    det.className = "resolvedlist";
    det.open = resolvedOpen;
    det.addEventListener("toggle", () => { resolvedOpen = det.open; });
    const sum = document.createElement("summary");
    sum.textContent = "Resolved (" + done.length + ")";
    det.appendChild(sum);
    for (const c of done) det.appendChild(commentCard(c));
    panel.appendChild(det);
  }
}
async function refreshComments() {
  // re-fetch comments only; keep the editor (possibly dirty) untouched
  const res = await api("/api/doc?path=" + encodeURIComponent(state.path));
  if (!res.ok) return;
  state.comments = (await res.json()).comments;
  rerender();
}
function focusCard(id) {
  const card = $("card-" + id);
  if (!card) return;
  const det = card.closest("details");
  if (det) { det.open = true; resolvedOpen = true; }
  card.scrollIntoView({behavior:"smooth", block:"center"});
  card.style.borderColor = "var(--accent)";
  setTimeout(()=>card.style.borderColor = "", 1200);
}

/* ---------- select-to-comment ---------- */
let lastSel = null;   // snapshot of the most recent doc selection (survives focus steals)
function captureSelection() {
  const sel = window.getSelection();
  if (!sel.rangeCount || sel.isCollapsed) return null;
  const range = sel.getRangeAt(0);
  if (!$("doc").contains(range.commonAncestorContainer)) return null;
  const quote = sel.toString();
  if (!quote.trim()) return null;
  const pre = document.createRange();
  pre.selectNodeContents($("doc")); pre.setEnd(range.startContainer, range.startOffset);
  const post = document.createRange();
  post.selectNodeContents($("doc")); post.setStart(range.endContainer, range.endOffset);
  lastSel = { quote, prefix: pre.toString().slice(-30), suffix: post.toString().slice(0, 30) };
  return lastSel;
}
function openCommentPopover(x, y) {
  // live selection if there is one; else the last snapshot (e.g. after a double-click sync)
  const cap = captureSelection() || lastSel;
  if (!cap) return false;
  pending = cap;
  const pop = $("pop");
  pop.style.display = "block";
  pop.style.left = Math.min(x, innerWidth - 300) + "px";
  pop.style.top = (y + 8) + "px";
  $("popText").value = ""; $("popText").focus();
  return true;
}
$("doc").addEventListener("mouseup", ev => {
  if (!state || ev.button !== 0) return;
  setTimeout(() => {
    const sel = window.getSelection();
    if (!sel.rangeCount || sel.isCollapsed) { $("pop").style.display = "none"; return; }
    const range = sel.getRangeAt(0);
    if (!$("doc").contains(range.commonAncestorContainer)) return;
    if (ev.detail > 1) {
      // double/triple click: sync to source (select the word there), never open the comment box
      $("pop").style.display = "none";
      captureSelection();   // snapshot so a follow-up right-click can still comment on it
      const pre = document.createRange();
      pre.selectNodeContents($("doc"));
      pre.setEnd(range.startContainer, range.startOffset);
      jumpToSource(pre.toString(), sel.toString().trim());
      return;
    }
    const rect = range.getBoundingClientRect();
    openCommentPopover(rect.left, rect.bottom);
  }, 0);
});
$("doc").addEventListener("contextmenu", ev => {
  // right-click on any selection (drag- or double-click-made) -> comment popover;
  // with nothing selected the native context menu stays
  if (!state) return;
  if (openCommentPopover(ev.clientX, ev.clientY)) ev.preventDefault();
});
$("popAdd").onclick = async () => {
  const text = $("popText").value.trim();
  if (!text || !pending) return;
  await api("/api/comment/add", {path: state.path, ...pending, comment: text});
  $("pop").style.display = "none"; pending = null;
  refreshComments();
};
document.addEventListener("mousedown", ev => {
  if (!$("pop").contains(ev.target)) $("pop").style.display = "none";
});

/* ---------- click rendered -> cursor in source ---------- */
$("doc").addEventListener("click", ev => {
  if (!state) return;
  const sel = window.getSelection();
  if (sel && !sel.isCollapsed) return;              // a drag-select, not a click
  let node = null, offset = 0;
  if (document.caretRangeFromPoint) {
    const r = document.caretRangeFromPoint(ev.clientX, ev.clientY);
    if (r) { node = r.startContainer; offset = r.startOffset; }
  } else if (document.caretPositionFromPoint) {
    const p = document.caretPositionFromPoint(ev.clientX, ev.clientY);
    if (p) { node = p.offsetNode; offset = p.offset; }
  }
  if (!node || !$("doc").contains(node)) return;
  const pre = document.createRange();
  pre.selectNodeContents($("doc"));
  try { pre.setEnd(node, offset); } catch (e) { return; }
  jumpToSource(pre.toString());
});
function jumpToSource(renderedCtx, selectWord) {
  const src = $("editor").value;
  const total = $("doc").textContent.length || 1;
  const ratio = renderedCtx.length / total;         // where the click sits in the doc
  let tail = renderedCtx.slice(-60);
  while (tail.length >= 5) {
    const hits = [];
    let i = src.indexOf(tail);
    while (i >= 0 && hits.length < 50) { hits.push(i); i = src.indexOf(tail, i + 1); }
    if (hits.length) {
      // among repeated matches, pick the one whose position best matches the click's
      const best = hits.reduce((a, b) =>
        Math.abs(b / src.length - ratio) < Math.abs(a / src.length - ratio) ? b : a);
      const pos = best + tail.length;
      if (selectWord) {
        // double-click: select the corresponding word in the source, if it is right ahead
        const wi = src.indexOf(selectWord, Math.max(0, pos - 2));
        if (wi >= 0 && wi - pos < 80) { placeCursor(wi, wi + selectWord.length); return; }
      }
      placeCursor(pos);
      return;
    }
    tail = tail.slice(Math.max(1, Math.ceil(tail.length / 4)));  // markdown syntax in the way: shrink from the left
  }
  // nothing matched (click landed on pure markup); with a word in hand, fall back to position-nearest word match
  if (selectWord) {
    const hits = [];
    let i = src.indexOf(selectWord);
    while (i >= 0 && hits.length < 200) { hits.push(i); i = src.indexOf(selectWord, i + 1); }
    if (hits.length) {
      const best = hits.reduce((a, b) =>
        Math.abs(b / src.length - ratio) < Math.abs(a / src.length - ratio) ? b : a);
      placeCursor(best, best + selectWord.length);
    }
  }
}
/* ---------- review mode: one pane, and editing in the rendered view ---------- */
let uiMode = "split";
function showSrc(on) {
  $("app").classList.toggle("showsrc", on);
  $("segSrc").classList.toggle("on", on);
  $("segPrev").classList.toggle("on", !on);
  // one font control, pointed at whichever pane is showing
  for (const b of [$("rFontDown"), $("rFontUp")]) b.dataset.f = on ? "editor" : "doc";
  if (on) { queueMirror(); $("editor").focus(); }
}
async function initMode() {
  const info = await (await api("/api/root")).json();
  uiMode = info.mode || "split";
  if (uiMode !== "review") return;
  document.documentElement.dataset.mode = "review";
  applyLayout();
  $("segPrev").onclick = () => showSrc(false);
  $("segSrc").onclick = () => showSrc(true);
  $("rsaveBtn").onclick = () => save(false);
  $("rthemeBtn").onclick = () => $("themeBtn").click();
  $("rpanelToggle").onclick = () => $("panelToggle").click();
  showSrc(false);
}

/* Turn one rendered block back into its markdown source. The source lines come from
   markdown-it via data-l0/data-l1, so nothing is ever converted from HTML back to
   markdown and the rest of the file is untouched. */
let editingBlock = null;
function blockSource(l0, l1) {
  const lines = $("editor").value.split("\n");
  let end = Math.min(l1, lines.length);
  while (end > l0 && !lines[end - 1].trim()) end--;   // hide the block's trailing blanks
  return {text: lines.slice(l0, end).join("\n"), blanks: Math.min(l1, lines.length) - end};
}
// A list item or table row cannot simply be swapped for a textarea without breaking the
// list or table around it, so those keep their element and host the editor inside.
function mountEditor(el, ta) {
  if (el.tagName === "LI") { el.textContent = ""; el.appendChild(ta); return; }
  if (el.tagName === "TR") {
    const span = el.children.length || 1;
    el.textContent = "";
    const cell = document.createElement("td");
    cell.colSpan = span;
    cell.appendChild(ta);
    el.appendChild(cell);
    return;
  }
  const host = el.tagName === "CODE" && el.parentElement.tagName === "PRE" ? el.parentElement : el;
  host.replaceWith(ta);
}
function openBlock(el) {
  if (editingBlock) return;
  const l0 = +el.dataset.l0, l1 = +el.dataset.l1;
  const {text, blanks} = blockSource(l0, l1);
  const ta = document.createElement("textarea");
  ta.className = "blockedit";
  ta.value = text;
  ta.spellcheck = false;
  mountEditor(el, ta);
  editingBlock = {l0, l1, blanks, ta};
  const fit = () => { ta.style.height = "auto"; ta.style.height = ta.scrollHeight + "px"; };
  fit();
  ta.addEventListener("input", fit);
  ta.focus();
  ta.setSelectionRange(ta.value.length, ta.value.length);
  ta.addEventListener("blur", () => commitBlock(true));
  ta.addEventListener("keydown", ev => {
    if (ev.key === "Escape") { ev.preventDefault(); commitBlock(false); }
    // Enter inserts a newline as usual; the block closes on blur or Escape
  });
}
function commitBlock(keep) {
  if (!editingBlock) return;
  const {l0, l1, blanks, ta} = editingBlock;
  const next = ta.value;
  editingBlock = null;                       // before rerender, so blur cannot re-enter
  const {text} = blockSource(l0, l1);
  if (!keep || next === text) { rerender(); return; }
  const lines = $("editor").value.split("\n");
  lines.splice(l0, Math.min(l1, lines.length) - l0,
               ...next.split("\n"), ...Array(blanks).fill(""));
  $("editor").value = lines.join("\n");
  queueMirror();
  setDirty(true);
  rerender();
}
$("doc").addEventListener("click", ev => {
  if (uiMode !== "review" || !state || editingBlock) return;
  if (ev.detail > 1) return;                      // double-click keeps its own behaviour
  if (!window.getSelection().isCollapsed) return; // a selection is a comment, not an edit
  if (ev.target.closest("mark")) return;          // clicking a highlight opens its comment
  const el = ev.target.closest("[data-l0]");
  if (el) openBlock(el);
});

/* ---------- mirror: line numbers + markdown syntax colour ---------- */
function esc(s) { return s.replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }
// One class letter per character: h heading, b marker/punctuation, c code, u link
// target, q HTML comment. Fenced blocks are the one construct that spans lines, so
// the fence flag is threaded through the loop in paintMirror.
const MD_LEAD = /^(\s*)([-*+]\s|\d+[.)]\s|>\s?)/;
function mdScan(line, fence) {
  const n = line.length, out = new Array(n).fill(" ");
  const fill = c => { for (let i = 0; i < n; i++) out[i] = c; };
  if (/^\s*(```|~~~)/.test(line)) { fill("c"); return {cls: out, fence: !fence}; }
  if (fence) { fill("c"); return {cls: out, fence}; }
  if (/^\s{0,3}#{1,6}\s/.test(line)) { fill("h"); return {cls: out, fence}; }
  let i = 0;
  const lead = MD_LEAD.exec(line);
  if (lead) {
    for (let j = lead[1].length; j < lead[0].length; j++) out[j] = "b";
    i = lead[0].length;
    if (line.slice(i, i + 3).match(/^\[[ xX]\]/)) {   // task list checkbox
      for (let j = i; j < i + 3; j++) out[j] = "b";
      i += 3;
    }
  }
  while (i < n) {
    const ch = line[i];
    if (ch === "`") {
      const close = line.indexOf("`", i + 1), end = close < 0 ? n : close + 1;
      for (let j = i; j < end; j++) out[j] = "c";
      i = end; continue;
    }
    if (line.startsWith("<!--", i)) {
      const close = line.indexOf("-->", i), end = close < 0 ? n : close + 3;
      for (let j = i; j < end; j++) out[j] = "q";
      i = end; continue;
    }
    if (ch === "[") {
      const rb = line.indexOf("]", i);
      if (rb > 0 && line[rb + 1] === "(") {
        const rp = line.indexOf(")", rb);
        out[i] = "b"; out[rb] = "b"; out[rb + 1] = "b";
        const end = rp < 0 ? n : rp;
        for (let j = rb + 2; j < end; j++) out[j] = "u";
        if (rp > 0) out[rp] = "b";
        i = rp < 0 ? n : rp + 1; continue;
      }
    }
    if (ch === "*" || ch === "_" || ch === "~") { out[i] = "b"; i++; continue; }
    i++;
  }
  return {cls: out, fence};
}
function renderLine(line, fence) {
  const n = line.length;
  if (!n) return {html: "", fence};
  const r = mdScan(line, fence);
  let out = "", j = 0;
  while (j < n) {
    const c = r.cls[j];
    let k = j + 1;
    while (k < n && r.cls[k] === c) k++;
    const txt = esc(line.slice(j, k));
    out += c === " " ? txt : '<span class="t' + c + '">' + txt + "</span>";
    j = k;
  }
  return {html: out, fence: r.fence};
}
let mirrorQueued = false;
function paintMirror() {
  mirrorQueued = false;
  const ed = $("editor");
  const lines = ed.value.split("\n");
  let out = "", fence = false;
  for (let i = 0; i < lines.length; i++) {
    const r = renderLine(lines[i], fence);
    fence = r.fence;
    // an empty row would collapse to zero height; the textarea keeps one line
    out += '<div class="row" data-n="' + (i + 1) + '">' + (r.html || "&#8203;") + "</div>";
  }
  // the textarea scrolls and the mirror does not, so a classic (non-overlay)
  // scrollbar would leave the mirror wider and wrap it differently
  const bar = ed.offsetWidth - ed.clientWidth;
  $("mirror").style.paddingRight = (parseFloat(getComputedStyle(ed).paddingRight) + bar) + "px";
  $("mirror").innerHTML = out;
  $("mirror").scrollTop = ed.scrollTop;
}
function queueMirror() {
  if (mirrorQueued) return;
  mirrorQueued = true;
  requestAnimationFrame(paintMirror);
}
$("editor").addEventListener("scroll", () => { $("mirror").scrollTop = $("editor").scrollTop; });
// while an IME is composing, the pending text lives in the textarea and not yet in the
// mirror, so hand the colour back to the textarea until the composition commits
$("editor").addEventListener("compositionstart", () => $("edarea").classList.add("composing"));
$("editor").addEventListener("compositionend", () => {
  $("edarea").classList.remove("composing"); queueMirror();
});
// wrapping changes with the pane width and the font size, which moves every number
new ResizeObserver(queueMirror).observe($("editor"));

function caretTop(ed, pos) {
  // mirror the textarea's text up to pos in a hidden div with identical wrapping,
  // so soft-wrapped long lines measure at their true visual height
  const div = document.createElement("div");
  const style = getComputedStyle(ed);
  for (const p of ["fontFamily","fontSize","fontWeight","lineHeight","letterSpacing",
                   "paddingTop","paddingRight","paddingBottom","paddingLeft","boxSizing"])
    div.style[p] = style[p];
  div.style.position = "absolute";
  div.style.visibility = "hidden";
  div.style.whiteSpace = "pre-wrap";
  div.style.wordWrap = "break-word";
  div.style.width = ed.clientWidth + "px";
  div.textContent = ed.value.slice(0, pos);
  const marker = document.createElement("span");
  marker.textContent = "​";
  div.appendChild(marker);
  document.body.appendChild(div);
  const top = marker.offsetTop;
  div.remove();
  return top;
}
function placeCursor(pos, end) {
  const ed = $("editor");
  ed.focus();
  ed.setSelectionRange(pos, end ?? pos);
  ed.scrollTop = Math.max(0, caretTop(ed, pos) - ed.clientHeight / 2);
  $("mirror").scrollTop = ed.scrollTop;
}

/* ---------- save + export ---------- */
async function save(overwrite) {
  if (!state) return;
  const body = { path: state.path, content: $("editor").value };
  if (!overwrite) body.mtime = state.mtime;
  const res = await api("/api/doc", body);
  if (res.status === 409) {
    if (confirm("File changed on disk since you loaded it.\nOK = overwrite with your version.  Cancel = discard your edits and reload."))
      return save(true);
    return openDoc(state.path);
  }
  if (!res.ok) { toast((await res.json()).error); return; }
  state.mtime = (await res.json()).mtime;
  setDirty(false);
  toast("Saved");
  rerender();
}
$("saveBtn").onclick = () => save(false);
document.addEventListener("keydown", ev => {
  if ((ev.metaKey || ev.ctrlKey) && ev.key === "s") { ev.preventDefault(); save(false); }
});
$("exportBtn").onclick = async () => {
  const res = await api("/api/export?path=" + encodeURIComponent(state.path));
  await navigator.clipboard.writeText(await res.text());
  toast("Copied document + comments to clipboard");
};

/* ---------- reveal: cursor in raw -> blink in rendered ---------- */
function revealInRendered() {
  if (!state) return;
  const ed = $("editor");
  const src = ed.value;
  const cur = ed.selectionStart;
  const docText = $("doc").textContent;
  const ratio = cur / (src.length || 1);
  let tail = src.slice(Math.max(0, cur - 60), cur).trim();
  while (tail.length >= 5) {
    const hits = [];
    let i = docText.indexOf(tail);
    while (i >= 0 && hits.length < 50) { hits.push(i); i = docText.indexOf(tail, i + 1); }
    if (hits.length) {
      const best = hits.reduce((a, b) =>
        Math.abs(b / docText.length - ratio) < Math.abs(a / docText.length - ratio) ? b : a);
      flashRendered(best, tail.length);
      return;
    }
    tail = tail.slice(Math.max(1, Math.ceil(tail.length / 4)));  // markdown syntax in the way
  }
  toast("No matching text in the preview (markup-only region?)");
}
function flashRendered(start, len) {
  const article = $("doc");
  const first = wrapTextRange(article, start, start + len,
    () => Object.assign(document.createElement("span"), {className: "flash"}));
  if (first) first.scrollIntoView({behavior: "smooth", block: "center"});
  setTimeout(() => {
    for (const s of article.querySelectorAll("span.flash")) s.replaceWith(...s.childNodes);
  }, 2000);
}
$("revealBtn").onclick = revealInRendered;

/* ---------- mermaid lightbox: zoom + pan ---------- */
let zoom = 1, panX = 0, panY = 0;
function applyStage() {
  $("stage").firstElementChild.style.transform =
    `translate(${panX}px, ${panY}px) scale(${zoom})`;
}
function openDiagram(svg) {
  const stage = $("stage");
  stage.innerHTML = "";
  const wrap = document.createElement("div");
  wrap.appendChild(svg.cloneNode(true));
  wrap.style.width = "100%";
  stage.appendChild(wrap);
  zoom = 1; panX = panY = 0;
  applyStage();
  $("overlay").style.display = "flex";
}
function closeDiagram() { $("overlay").style.display = "none"; }
$("zIn").onclick = () => { zoom = Math.min(8, zoom * 1.25); applyStage(); };
$("zOut").onclick = () => { zoom = Math.max(0.3, zoom / 1.25); applyStage(); };
$("zReset").onclick = () => { zoom = 1; panX = panY = 0; applyStage(); };
$("zClose").onclick = closeDiagram;
$("overlay").addEventListener("wheel", ev => {
  ev.preventDefault();
  zoom = Math.min(8, Math.max(0.3, zoom * (ev.deltaY < 0 ? 1.12 : 1 / 1.12)));
  applyStage();
}, {passive: false});
{
  let dragging = false, moved = false, sx = 0, sy = 0;
  $("stage").addEventListener("mousedown", ev => {
    dragging = true; moved = false; sx = ev.clientX - panX; sy = ev.clientY - panY;
    $("stage").style.cursor = "grabbing"; ev.preventDefault();
  });
  document.addEventListener("mousemove", ev => {
    if (!dragging) return;
    panX = ev.clientX - sx; panY = ev.clientY - sy; moved = true; applyStage();
  });
  document.addEventListener("mouseup", () => { dragging = false; $("stage").style.cursor = "grab"; });
  $("overlay").addEventListener("click", ev => {
    if (ev.target === $("overlay") && !moved) closeDiagram();
  });
}
document.addEventListener("keydown", ev => {
  if (ev.key === "Escape" && $("overlay").style.display === "flex") closeDiagram();
});

/* ---------- draggable pane divider ---------- */
$("gutter").addEventListener("mousedown", e => {
  e.preventDefault();
  $("gutter").classList.add("dragging");
  document.body.style.userSelect = "none";
  const move = ev => {
    const left = 230, right = panelVisible ? 300 : 0, gw = 6;
    const usable = innerWidth - left - right - gw;
    splitFrac = Math.min(0.8, Math.max(0.2, (ev.clientX - left - gw / 2) / usable));
    applyLayout();
  };
  const up = () => {
    $("gutter").classList.remove("dragging");
    document.body.style.userSelect = "";
    document.removeEventListener("mousemove", move);
    document.removeEventListener("mouseup", up);
  };
  document.addEventListener("mousemove", move);
  document.addEventListener("mouseup", up);
});
$("gutter").addEventListener("dblclick", () => {
  splitFrac = 0.5;
  applyLayout();
});

/* ---------- per-pane font size (persisted) ---------- */
const FONT_DEFAULTS = { editor: 13, doc: 15, panel: 13 };
const fonts = {};
for (const k in FONT_DEFAULTS)
  fonts[k] = +(localStorage.getItem("mdreview.font." + k) || FONT_DEFAULTS[k]);
function applyFonts() {
  $("edarea").style.fontSize = fonts.editor + "px";
  queueMirror();   // a font change re-wraps every line, so the numbers move
  $("doc").style.fontSize = fonts.doc + "px";
  $("panel").style.fontSize = fonts.panel + "px";
}
document.addEventListener("click", ev => {
  const b = ev.target.closest(".fontctl button");
  if (!b || !b.dataset.f) return;
  const k = b.dataset.f;
  fonts[k] = Math.min(24, Math.max(10, fonts[k] + (+b.dataset.d)));
  localStorage.setItem("mdreview.font." + k, fonts[k]);
  applyFonts();
});
applyFonts();

/* ---------- show/hide comments panel ---------- */
let panelVisible = localStorage.getItem("mdreview.panel") !== "hidden";
let splitFrac = 0.5;
function applyLayout() {
  $("panel").style.display = panelVisible ? "" : "none";
  // review mode has one centre column and no draggable split; this inline style would
  // otherwise beat the stylesheet and put the four-column layout back
  $("app").style.gridTemplateColumns = uiMode === "review"
    ? `230px 1fr ${panelVisible ? "300px" : "0"}`
    : `230px ${splitFrac}fr 6px ${1 - splitFrac}fr ${panelVisible ? "300px" : "0"}`;
  $("panelToggle").classList.toggle("off", !panelVisible);
}
$("panelToggle").onclick = () => {
  panelVisible = !panelVisible;
  localStorage.setItem("mdreview.panel", panelVisible ? "shown" : "hidden");
  applyLayout();
};
$("themeBtn").onclick = () => {
  localStorage.setItem("mdreview.theme",
    document.documentElement.dataset.theme === "dark" ? "light" : "dark");
  applyTheme();
};
applyLayout();

// mermaid loads after the head script ran applyTheme(), so set its theme now
if (window.mermaid) applyTheme();
initMode();
loadFiles();
</script></body></html>"""


def route(root: Path, method: str, path: str, query: dict, body: dict) -> tuple[int, str, object]:
    """Pure dispatcher: (status, content-type, payload). Payload str => raw, else JSON."""
    try:
        if method == "GET" and path == "/":
            return 200, "text/html; charset=utf-8", PAGE
        if method == "GET" and path == "/api/root":
            return 200, "application/json", {"root": str(root), "build": BUILD,
                                             "mode": UI_MODE}
        if method == "GET" and path == "/api/files":
            return 200, "application/json", list_md_files(root)
        if method == "GET" and path == "/api/doc":
            rel = query["path"][0]
            doc = read_doc(root, rel)
            return 200, "application/json", {
                **doc, "path": rel,
                "html": render_md(doc["content"]),
                "comments": load_comments(root, rel),
            }
        if method == "GET" and path == "/api/export":
            return 200, "text/plain; charset=utf-8", export_text(root, query["path"][0])
        if method == "POST" and path == "/api/render":
            return 200, "application/json", {"html": render_md(body["content"])}
        if method == "POST" and path == "/api/doc":
            return 200, "application/json", write_doc(
                root, body["path"], body["content"], body.get("mtime"))
        if method == "POST" and path == "/api/comment/add":
            return 200, "application/json", add_comment(
                root, body["path"], body["quote"], body["prefix"], body["suffix"], body["comment"])
        if method == "POST" and path == "/api/comment/update":
            fields = {k: body[k] for k in ("resolved", "comment") if k in body}
            return 200, "application/json", update_comment(root, body["path"], body["id"], fields)
        if method == "POST" and path == "/api/comment/delete":
            delete_comment(root, body["path"], body["id"])
            return 200, "application/json", {"ok": True}
        if method == "GET" and "." in path:
            # serve repo images so ![](figures/x.png) renders in the preview
            ext = path.rsplit(".", 1)[-1].lower()
            if ext in IMAGE_TYPES:
                p = safe_resolve(root, unquote(path).lstrip("/"))
                if not p.is_file():
                    raise RequestError(404, f"no such file: {path}")
                if p.stat().st_size > MAX_IMAGE_BYTES:
                    raise RequestError(413, f"image over {MAX_IMAGE_BYTES // (1024 * 1024)} MB")
                return 200, IMAGE_TYPES[ext], p.read_bytes()
        return 404, "application/json", {"error": f"no such route: {method} {path}"}
    except RequestError as e:
        return e.status, "application/json", {"error": e.message}
    except (KeyError, IndexError):
        return 400, "application/json", {"error": "missing parameter"}


class Handler(BaseHTTPRequestHandler):
    root: Path = Path(".")

    def log_message(self, fmt, *args):  # quiet
        pass

    def _send(self, status: int, ctype: str, payload) -> None:
        if isinstance(payload, (bytes, bytearray)):
            data = bytes(payload)
        elif isinstance(payload, str):
            data = payload.encode("utf-8")
        else:
            data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        self._send(*route(self.root, "GET", u.path, parse_qs(u.query), {}))

    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            self._send(400, "application/json", {"error": "invalid JSON body"})
            return
        self._send(*route(self.root, "POST", u.path, parse_qs(u.query), body))


def find_existing(root: Path, start: int) -> tuple[str | None, str | None]:
    """Probe nearby ports for an mdreview instance already serving this root.

    Returns (reusable_url, stale_url): an instance built from a different version of
    this file is reported as stale rather than reused, since it would serve the old UI.
    """
    stale = None
    for port in range(start, start + 20):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/root", timeout=0.3) as r:
                info = json.loads(r.read())
        except (OSError, ValueError):
            continue
        # a server in the other UI mode serves a different tool, not a reusable one
        if info.get("root") != str(root) or info.get("mode", "review") != UI_MODE:
            continue
        url = f"http://127.0.0.1:{port}/"
        if info.get("build") == BUILD:
            return url, None
        stale = stale or url
    return None, stale


def main() -> None:
    ap = argparse.ArgumentParser(description="mdreview: local markdown review UI")
    ap.add_argument("--port", type=int, default=8377)
    ap.add_argument("--open", action="store_true", help="open the browser")
    ap.add_argument("--root", default=".", help="repo root to serve (default: cwd)")
    ap.add_argument("--split", action="store_true",
                    help="source-beside-preview layout (/research.mdsplit) instead of "
                         "the one-pane view you edit in (/research.mdreview)")
    args = ap.parse_args()
    global UI_MODE
    UI_MODE = "split" if args.split else "review"
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"error: not a directory: {root}")
    existing, stale = find_existing(root, args.port)
    if existing:
        print(f"mdreview already serving {root}")
        print(f"  {existing}   (reusing the running instance)")
        if args.open:
            webbrowser.open(existing)
        return
    if stale:
        print(f"note: {stale} runs an older build of mdreview and was not reused.")
        print("      stop it (Ctrl-C in its terminal) and close that tab to avoid confusion.")
    Handler.root = root
    server = None
    for port in range(args.port, args.port + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            print(f"port {port} in use, trying {port + 1}")
    if server is None:
        raise SystemExit("error: no free port found")
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"mdreview serving {root}")
    print(f"  {url}   (Ctrl-C to stop; comments land in {root / SIDECAR_DIR}/)")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
