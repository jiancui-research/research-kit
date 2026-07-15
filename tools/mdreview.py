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

SKIP_DIRS = {".git", "node_modules", ".venv", ".mdreview"}
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
  #app { display:grid; grid-template-columns:250px 1fr 320px; height:100vh; }
  #side { border-right:1px solid var(--line); overflow-y:auto; padding:10px; font-size:13px; }
  #side .dir { font-weight:600; margin-top:6px; }
  #side button { display:block; width:100%; text-align:left; border:0; background:none;
                 padding:3px 6px; border-radius:5px; cursor:pointer; font:inherit; color:#333; }
  #side button:hover { background:#f0f3f8; }
  #side button.active { background:#e3ecfd; color:var(--accent); }
  #main { overflow-y:auto; padding:28px 40px; }
  #bar { display:flex; gap:8px; align-items:center; margin-bottom:14px; }
  #bar .path { font-weight:600; margin-right:auto; }
  #bar button { border:1px solid var(--line); background:#fff; border-radius:6px;
                padding:5px 12px; cursor:pointer; font:inherit; }
  #bar button:hover { border-color:var(--accent); color:var(--accent); }
  #doc { max-width:760px; }
  #doc h1,#doc h2,#doc h3 { line-height:1.3; }
  #doc pre { background:#f6f8fa; padding:10px; border-radius:6px; overflow-x:auto; }
  #doc code { background:#f6f8fa; padding:1px 4px; border-radius:4px; font-size:90%; }
  #doc table { border-collapse:collapse; } #doc td,#doc th { border:1px solid var(--line); padding:4px 9px; }
  #doc blockquote { border-left:3px solid var(--line); margin-left:0; padding-left:14px; color:#555; }
  #doc mark { background:var(--hl); cursor:pointer; border-bottom:2px solid var(--hl-strong); }
  #editor { display:none; width:100%; height:calc(100vh - 110px); font:13px/1.5 ui-monospace,Menlo,monospace;
            border:1px solid var(--line); border-radius:6px; padding:12px; }
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
  <nav id="side"></nav>
  <section id="main">
    <div id="bar" style="display:none">
      <span class="path" id="path"></span>
      <button id="editBtn">Edit</button>
      <button id="saveBtn" style="display:none">Save</button>
      <button id="cancelBtn" style="display:none">Cancel</button>
      <button id="exportBtn">Export</button>
    </div>
    <article id="doc"><p class="empty">Pick a file on the left.</p></article>
    <textarea id="editor" spellcheck="false"></textarea>
  </section>
  <aside id="panel"><p class="empty">Comments appear here.</p></aside>
</div>
<div id="pop"><textarea id="popText" placeholder="Comment..."></textarea><br>
  <button id="popAdd">Add comment</button></div>
<div id="toast"></div>
<script>
const $ = id => document.getElementById(id);
let state = null;      // {path, content, mtime, comments:[{...,anchored}]}
let editing = false;
let pending = null;    // {quote, prefix, suffix} awaiting comment text

const api = async (url, body) => {
  const res = await fetch(url, body ? {method:"POST",
    headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)} : undefined);
  return res;
};
const toast = msg => { const t=$("toast"); t.textContent=msg; t.style.display="block";
  setTimeout(()=>t.style.display="none", 2200); };

async function loadFiles() {
  const files = await (await api("/api/files")).json();
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
      b.onclick = () => openDoc(node[key]);
      el.appendChild(b);
    }
  }
}

async function openDoc(path) {
  const res = await api("/api/doc?path=" + encodeURIComponent(path));
  if (!res.ok) { toast((await res.json()).error); return; }
  state = await res.json();
  setEditing(false);
  $("bar").style.display = "flex";
  $("path").textContent = state.path;
  $("doc").innerHTML = state.html;
  for (const btn of document.querySelectorAll("#side button"))
    btn.classList.toggle("active", btn.dataset.path === path);
  applyHighlights();
  renderPanel();
}

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
function applyHighlights() {
  const article = $("doc");
  for (const c of state.comments) {
    const start = findAnchor(article.textContent, c);
    c.anchored = start >= 0 && c.quote.length > 0;
    if (!c.anchored) continue;
    const end = start + c.quote.length;
    let pos = 0;
    for (const node of textNodesUnder(article)) {
      const len = node.length, a = Math.max(start - pos, 0), b = Math.min(end - pos, len);
      if (a < b) {
        const r = document.createRange();
        r.setStart(node, a); r.setEnd(node, b);
        const mk = document.createElement("mark");
        mk.dataset.id = c.id;
        mk.onclick = ev => { ev.stopPropagation(); focusCard(c.id); };
        try { r.surroundContents(mk); } catch (e) {}
      }
      pos += len;
      if (pos >= end) break;
    }
  }
}

function renderPanel() {
  const panel = $("panel"); panel.innerHTML = "";
  if (!state.comments.length) {
    panel.innerHTML = '<p class="empty">No comments. Select text in the document to add one.</p>';
    return;
  }
  for (const c of state.comments) {
    const card = document.createElement("div");
    card.className = "card" + (c.resolved ? " resolved" : "");
    card.id = "card-" + c.id;
    const q = document.createElement("span"); q.className = "q"; q.textContent = '"' + c.quote + '"';
    const body = document.createElement("div"); body.textContent = c.comment;
    const meta = document.createElement("div"); meta.className = "meta";
    meta.textContent = c.created.slice(0, 16).replace("T", " ") + (c.anchored ? "" : " ");
    if (!c.anchored) { const o = document.createElement("span"); o.className = "orphan";
      o.textContent = "orphaned"; meta.appendChild(o); }
    const res = document.createElement("button");
    res.textContent = c.resolved ? "Reopen" : "Resolve";
    res.onclick = async () => { await api("/api/comment/update",
      {path: state.path, id: c.id, resolved: !c.resolved}); openDoc(state.path); };
    const del = document.createElement("button");
    del.textContent = "Delete";
    del.onclick = async () => { await api("/api/comment/delete",
      {path: state.path, id: c.id}); openDoc(state.path); };
    meta.append(res, del);
    card.append(q, body, meta);
    panel.appendChild(card);
  }
}
function focusCard(id) {
  const card = $("card-" + id);
  if (card) { card.scrollIntoView({behavior:"smooth", block:"center"});
    card.style.borderColor = "var(--accent)";
    setTimeout(()=>card.style.borderColor = "", 1200); }
}

$("doc").addEventListener("mouseup", ev => {
  if (editing || !state) return;
  setTimeout(() => {
    const sel = window.getSelection();
    if (!sel.rangeCount || sel.isCollapsed) { $("pop").style.display = "none"; return; }
    const range = sel.getRangeAt(0);
    if (!$("doc").contains(range.commonAncestorContainer)) return;
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
  openDoc(state.path);
};
document.addEventListener("mousedown", ev => {
  if (!$("pop").contains(ev.target)) $("pop").style.display = "none";
});

function setEditing(on) {
  editing = on;
  $("doc").style.display = on ? "none" : "";
  $("editor").style.display = on ? "block" : "none";
  $("editBtn").style.display = on ? "none" : "";
  $("exportBtn").style.display = on ? "none" : "";
  $("saveBtn").style.display = on ? "" : "none";
  $("cancelBtn").style.display = on ? "" : "none";
}
$("editBtn").onclick = () => { $("editor").value = state.content; setEditing(true); };
$("cancelBtn").onclick = () => setEditing(false);
async function save(overwrite) {
  const body = { path: state.path, content: $("editor").value };
  if (!overwrite) body.mtime = state.mtime;
  const res = await api("/api/doc", body);
  if (res.status === 409) {
    if (confirm("File changed on disk since you loaded it.\nOK = overwrite with your version.  Cancel = discard your edits and reload."))
      return save(true);
    return openDoc(state.path);
  }
  if (!res.ok) { toast((await res.json()).error); return; }
  toast("Saved");
  await openDoc(state.path);
}
$("saveBtn").onclick = () => save(false);
document.addEventListener("keydown", ev => {
  if ((ev.metaKey || ev.ctrlKey) && ev.key === "s" && editing) { ev.preventDefault(); save(false); }
});

$("exportBtn").onclick = async () => {
  const res = await api("/api/export?path=" + encodeURIComponent(state.path));
  await navigator.clipboard.writeText(await res.text());
  toast("Copied document + comments to clipboard");
};

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
