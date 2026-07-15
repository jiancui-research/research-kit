#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown"]
# ///
"""mdreview: a local web UI to read, edit, comment on, and export a repo's markdown.

Part of research-kit (an optional leaf tool - nothing in the pipeline depends on it).
Run from any repo root:  uv run tools/mdreview.py [--port N] [--open] [--root DIR]
Comments are sidecar JSON under the target repo's .mdreview/ - markdown files stay clean.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import markdown as md_lib

SKIP_DIRS = {".git", "node_modules", ".venv", ".mdreview", ".pytest_cache", "__pycache__"}
MAX_BYTES = 2 * 1024 * 1024
SIDECAR_DIR = ".mdreview"


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
                out.append(str((Path(dirpath) / f).relative_to(root)))
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
    for k in ("resolved", "comment"):
        if k in fields:
            c[k] = fields[k]
    _save_comments(root, rel, comments)
    return c


def delete_comment(root: Path, rel: str, cid: str) -> None:
    comments = load_comments(root, rel)
    c = _find_comment(comments, cid)
    comments.remove(c)
    _save_comments(root, rel, comments)


def render_md(text: str) -> str:
    return md_lib.markdown(text, extensions=["tables", "fenced_code"])


def export_text(root: Path, rel: str) -> str:
    """Document + unresolved comments as one AI-ready markdown blob."""
    doc = read_doc(root, rel)
    open_comments = [c for c in load_comments(root, rel) if not c["resolved"]]
    parts = [
        "Review this document; address the inline reviewer comments.",
        "",
        "---",
        "",
        doc["content"].rstrip(),
        "",
    ]
    if open_comments:
        parts += ["---", "", "## Reviewer comments", ""]
        for i, c in enumerate(open_comments, 1):
            parts.append(f'{i}. > "{c["quote"]}"')
            parts.append(f"   {c['comment']}")
            parts.append("")
    return "\n".join(parts)


PAGE = r"""<!doctype html>
<html><head><meta charset="utf-8"><title>mdreview</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root { --line:#e2e2e2; --accent:#2563eb; --hl:#fff3b0; --hl-strong:#ffe066; }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:#1f2328; }
  #app { display:grid; grid-template-columns:230px 1fr 6px 1fr 300px; height:100vh; }
  #gutter { cursor:col-resize; background:#fafafa; border-left:1px solid var(--line);
            border-right:1px solid var(--line); }
  #gutter:hover, #gutter.dragging { background:var(--accent); }
  #side { border-right:1px solid var(--line); overflow-y:auto; padding:10px; font-size:13px; }
  #scope { display:none; font-size:12px; color:#555; margin-bottom:8px; user-select:none; }
  #side .dir { font-weight:600; margin-top:6px; }
  #side button { display:block; width:100%; text-align:left; border:0; background:none;
                 padding:3px 6px; border-radius:5px; cursor:pointer; font:inherit; color:#333; }
  #side button:hover { background:#f0f3f8; }
  #side button.active { background:#e3ecfd; color:var(--accent); }
  #srcpane { display:flex; flex-direction:column; min-width:0; }
  #bar { display:flex; gap:8px; align-items:center; padding:9px 12px; border-bottom:1px solid var(--line); }
  #bar .path { font-weight:600; font-size:13px; margin-right:auto; overflow:hidden;
               text-overflow:ellipsis; white-space:nowrap; }
  #bar button { border:1px solid var(--line); background:#fff; border-radius:6px;
                padding:4px 11px; cursor:pointer; font:13px inherit; }
  #bar button:hover { border-color:var(--accent); color:var(--accent); }
  #editor { flex:1; width:100%; border:0; outline:none; resize:none; padding:14px 16px;
            font:13px/1.55 ui-monospace,Menlo,monospace; color:#24292f; }
  #main { overflow-y:auto; padding:22px 30px; min-width:0; }
  #doc { max-width:720px; }
  #doc h1,#doc h2,#doc h3 { line-height:1.3; }
  #doc pre { background:#f6f8fa; padding:10px; border-radius:6px; overflow-x:auto; }
  #doc code { background:#f6f8fa; padding:1px 4px; border-radius:4px; font-size:90%; }
  #doc table { border-collapse:collapse; } #doc td,#doc th { border:1px solid var(--line); padding:4px 9px; }
  #doc blockquote { border-left:3px solid var(--line); margin-left:0; padding-left:14px; color:#555; }
  #doc mark { background:var(--hl); cursor:pointer; border-bottom:2px solid var(--hl-strong); }
  @keyframes flashbg { 0%,100% { background:transparent; } 50% { background:var(--hl-strong); } }
  #doc span.flash { animation: flashbg .55s ease-in-out 3; border-radius:3px; }
  #doc .mermaid { position:relative; }
  .zoombtn { position:absolute; top:6px; right:6px; opacity:0; transition:opacity .15s;
             border:1px solid var(--line); background:#fff; border-radius:6px; padding:2px 8px;
             cursor:pointer; font-size:14px; }
  #doc .mermaid:hover .zoombtn { opacity:1; }
  #overlay { position:fixed; inset:0; background:rgba(15,18,22,.6); display:none;
             align-items:center; justify-content:center; z-index:30; }
  #stage { background:#fff; border-radius:10px; padding:24px; width:86vw; height:86vh;
           overflow:hidden; cursor:grab; display:flex; align-items:center; justify-content:center; }
  #stage svg { width:100%; height:auto; max-width:none; }
  #zctrl { position:fixed; top:18px; right:22px; display:flex; gap:6px; z-index:31; }
  #zctrl button { border:0; background:#fff; border-radius:7px; padding:6px 13px;
                  cursor:pointer; font:15px inherit; }
  #panel { border-left:1px solid var(--line); overflow-y:auto; padding:12px; font-size:13px; }
  .card { border:1px solid var(--line); border-radius:8px; padding:9px 11px; margin-bottom:9px; }
  .card.resolved { opacity:.55; }
  .card .q { color:#666; font-style:italic; display:block; margin-bottom:5px; white-space:nowrap;
             overflow:hidden; text-overflow:ellipsis; }
  .card .orphan { color:#b45309; font-size:11px; font-weight:600; }
  .card .meta { color:#999; font-size:11px; margin-top:5px; display:flex; gap:8px; }
  .card .meta button { border:0; background:none; color:var(--accent); cursor:pointer; padding:0; font-size:11px; }
  #pop { position:fixed; display:none; background:#fff; border:1px solid var(--line); border-radius:8px;
         box-shadow:0 4px 18px rgba(0,0,0,.13); padding:9px; width:280px; z-index:10; }
  #pop textarea { width:100%; height:64px; font:inherit; border:1px solid var(--line); border-radius:5px; padding:6px; }
  #pop button { margin-top:6px; border:0; background:var(--accent); color:#fff; border-radius:5px;
                padding:5px 12px; cursor:pointer; font:inherit; }
  #toast { position:fixed; bottom:18px; left:50%; transform:translateX(-50%); background:#1f2328; color:#fff;
           border-radius:7px; padding:8px 16px; display:none; font-size:13px; z-index:20; }
  .empty { color:#999; }
</style></head><body>
<div id="app">
  <nav id="sidewrap" style="overflow-y:auto; border-right:1px solid var(--line);">
    <div style="padding:10px 10px 0 10px;">
      <label id="scope"><input type="checkbox" id="scopeChk" checked> .research/ only</label>
    </div>
    <div id="side" style="border:0;"></div>
  </nav>
  <section id="srcpane">
    <div id="bar" style="visibility:hidden">
      <span class="path" id="path"></span>
      <button id="saveBtn">Save</button>
      <button id="revealBtn" title="Blink the preview text matching the cursor position">Reveal →</button>
      <button id="exportBtn">Export</button>
    </div>
    <textarea id="editor" spellcheck="false" placeholder="Pick a file on the left."></textarea>
  </section>
  <div id="gutter" title="drag to resize; double-click to reset"></div>
  <section id="main">
    <article id="doc"><p class="empty">Raw markdown on the left, rendered preview here.
      Click rendered text to jump the cursor to its source. Select rendered text to comment.</p></article>
  </section>
  <aside id="panel"><p class="empty">Comments appear here.</p></aside>
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
let state = null;      // {path, mtime, comments:[{...,anchored}]}
let allFiles = [];
let pending = null;    // {quote, prefix, suffix} awaiting comment text
let dirty = false;
let renderTimer = null;

const api = async (url, body) => fetch(url, body ? {method:"POST",
  headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)} : undefined);
const toast = msg => { const t=$("toast"); t.textContent=msg; t.style.display="block";
  setTimeout(()=>t.style.display="none", 2200); };
const setDirty = d => { dirty = d; $("saveBtn").textContent = d ? "Save •" : "Save"; };

/* ---------- sidebar ---------- */
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
  // toggled: only the tracking docs sitting directly in .research/ (hides templates/, tasks/, memory/, ...)
  const files = only
    ? allFiles.filter(f => f.startsWith(".research/") && !f.slice(10).includes("/"))
    : allFiles;
  const tree = {};
  for (const f of files) {
    const parts = f.split("/"); let node = tree;
    for (const p of parts.slice(0, -1)) node = (node[p + "/"] ??= {});
    node[parts.at(-1)] = f;
  }
  $("side").innerHTML = "";
  renderTree(tree, $("side"), 0);
}
function renderTree(node, el, depth) {
  for (const key of Object.keys(node).sort((a,b)=>a.localeCompare(b))) {
    if (key.endsWith("/")) {
      const d = document.createElement("div");
      d.className = "dir"; d.textContent = key; d.style.paddingLeft = depth*12 + "px";
      el.appendChild(d);
      renderTree(node[key], el, depth + 1);
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
  setDirty(false);
  $("bar").style.visibility = "visible";
  $("path").textContent = state.path;
  paint(d.html);
  renderSidebar();
}
function paint(html) {
  $("doc").innerHTML = html;
  applyHighlights();
  renderMermaid();
  renderPanel();
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
    const start = findAnchor(article.textContent, c);
    c.anchored = start >= 0 && c.quote.length > 0;
    if (!c.anchored) continue;
    wrapTextRange(article, start, start + c.quote.length, () => {
      const mk = document.createElement("mark");
      mk.dataset.id = c.id;
      mk.onclick = ev => { ev.stopPropagation(); focusCard(c.id); };
      return mk;
    });
  }
}
function renderPanel() {
  const panel = $("panel"); panel.innerHTML = "";
  if (!state.comments.length) {
    panel.innerHTML = '<p class="empty">No comments. Select rendered text to add one.</p>';
    return;
  }
  for (const c of state.comments) {
    const card = document.createElement("div");
    card.className = "card" + (c.resolved ? " resolved" : "");
    card.id = "card-" + c.id;
    const q = document.createElement("span"); q.className = "q"; q.textContent = '"' + c.quote + '"';
    const body = document.createElement("div"); body.textContent = c.comment;
    const meta = document.createElement("div"); meta.className = "meta";
    meta.textContent = c.created.slice(0, 16).replace("T", " ") + " ";
    if (!c.anchored) { const o = document.createElement("span"); o.className = "orphan";
      o.textContent = "orphaned"; meta.appendChild(o); }
    const res = document.createElement("button");
    res.textContent = c.resolved ? "Reopen" : "Resolve";
    res.onclick = async () => { await api("/api/comment/update",
      {path: state.path, id: c.id, resolved: !c.resolved}); refreshComments(); };
    const del = document.createElement("button");
    del.textContent = "Delete";
    del.onclick = async () => { await api("/api/comment/delete",
      {path: state.path, id: c.id}); refreshComments(); };
    meta.append(res, del);
    card.append(q, body, meta);
    panel.appendChild(card);
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
  if (card) { card.scrollIntoView({behavior:"smooth", block:"center"});
    card.style.borderColor = "var(--accent)";
    setTimeout(()=>card.style.borderColor = "", 1200); }
}

/* ---------- select-to-comment ---------- */
$("doc").addEventListener("mouseup", ev => {
  if (!state) return;
  setTimeout(() => {
    const sel = window.getSelection();
    if (!sel.rangeCount || sel.isCollapsed) { $("pop").style.display = "none"; return; }
    const range = sel.getRangeAt(0);
    if (!$("doc").contains(range.commonAncestorContainer)) return;
    if (ev.detail > 1) {
      // double/triple click: sync to source (select the word there), never open the comment box
      $("pop").style.display = "none";
      const pre = document.createRange();
      pre.selectNodeContents($("doc"));
      pre.setEnd(range.startContainer, range.startOffset);
      jumpToSource(pre.toString(), sel.toString().trim());
      return;
    }
    const quote = sel.toString();
    if (!quote.trim()) return;
    const pre = document.createRange();
    pre.selectNodeContents($("doc")); pre.setEnd(range.startContainer, range.startOffset);
    const post = document.createRange();
    post.selectNodeContents($("doc")); post.setStart(range.endContainer, range.endOffset);
    pending = { quote, prefix: pre.toString().slice(-30), suffix: post.toString().slice(0, 30) };
    const pop = $("pop"), rect = range.getBoundingClientRect();
    pop.style.display = "block";
    pop.style.left = Math.min(rect.left, innerWidth - 300) + "px";
    pop.style.top = (rect.bottom + 8) + "px";
    $("popText").value = ""; $("popText").focus();
  }, 0);
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
    const left = 230, right = 300, gw = 6;
    const usable = innerWidth - left - right - gw;
    let frac = (ev.clientX - left - gw / 2) / usable;
    frac = Math.min(0.8, Math.max(0.2, frac));
    $("app").style.gridTemplateColumns = `230px ${frac}fr 6px ${1 - frac}fr 300px`;
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
  $("app").style.gridTemplateColumns = "230px 1fr 6px 1fr 300px";
});

if (window.mermaid)
  mermaid.initialize({ startOnLoad: false, theme: "neutral", suppressErrorRendering: true });
loadFiles();
</script></body></html>"""


def route(root: Path, method: str, path: str, query: dict, body: dict) -> tuple[int, str, object]:
    """Pure dispatcher: (status, content-type, payload). Payload str => raw, else JSON."""
    try:
        if method == "GET" and path == "/":
            return 200, "text/html; charset=utf-8", PAGE
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
        if isinstance(payload, str):
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


def main() -> None:
    ap = argparse.ArgumentParser(description="mdreview: local markdown review UI")
    ap.add_argument("--port", type=int, default=8377)
    ap.add_argument("--open", action="store_true", help="open the browser")
    ap.add_argument("--root", default=".", help="repo root to serve (default: cwd)")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"error: not a directory: {root}")
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
