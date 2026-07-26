#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""texreview: a local web UI to review a LaTeX paper - source left, compiled PDF right.

Part of research-kit (an optional leaf tool - nothing in the pipeline depends on it).
Run from the manuscript repo, or from a research repo whose .research/paper-repo
points at it:  uv run tools/texreview.py [--port N] [--open] [--root DIR] [--main FILE]
Click PDF text to jump to its LaTeX source (SyncTeX), select PDF text to comment,
Recompile runs latexmk. Comments are sidecar JSON under the paper repo's .texreview/.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SKIP_DIRS = {".git", "node_modules", ".venv", ".texreview", ".pytest_cache", "__pycache__"}
TEXT_EXTS = (".tex", ".bib", ".cls", ".sty")
MAX_BYTES = 2 * 1024 * 1024
MAX_PDF_BYTES = 100 * 1024 * 1024
SIDECAR_DIR = ".texreview"
COMPILE_TIMEOUT = 600


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


def _has_documentclass(p: Path) -> bool:
    try:
        return "\\documentclass" in p.read_text(encoding="utf-8", errors="ignore")[:20000]
    except OSError:
        return False


def find_root(start: Path) -> Path:
    """The manuscript root: start itself if it holds a root .tex, else the dir
    .research/paper-repo (line 1) points to."""
    if any(_has_documentclass(p) for p in sorted(start.glob("*.tex"))):
        return start
    pointer = start / ".research" / "paper-repo"
    if pointer.is_file():
        lines = pointer.read_text(encoding="utf-8").splitlines()
        first = lines[0].strip() if lines else ""
        if first:
            target = Path(os.path.expanduser(first))
            if not target.is_absolute():
                target = start / target
            target = target.resolve()
            if target.is_dir():
                return target
            raise SystemExit(f"error: .research/paper-repo points to a missing dir: {first}")
    raise SystemExit(
        "error: no .tex with \\documentclass here and no usable .research/paper-repo pointer.\n"
        "Run from the manuscript repo, or record its path on line 1 of .research/paper-repo."
    )


def list_tex_files(root: Path) -> list[str]:
    """All LaTeX-ish text files under root (relative paths), pruning SKIP_DIRS."""
    out: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for f in sorted(filenames):
            if f.endswith(TEXT_EXTS):
                out.append((Path(dirpath) / f).relative_to(root).as_posix())
    return out


def find_main_tex(root: Path, override: str | None = None) -> str:
    """The compilation entry point: --main if given, else the shallowest
    \\documentclass .tex, preferring main.tex then paper.tex."""
    if override:
        p = safe_resolve(root, override)
        if not p.is_file():
            raise SystemExit(f"error: --main not found: {override}")
        return p.relative_to(root.resolve()).as_posix()
    cands = [f for f in list_tex_files(root)
             if f.endswith(".tex") and _has_documentclass(root / f)]
    if not cands:
        raise SystemExit(f"error: no .tex with \\documentclass under {root}")

    def rank(f: str) -> tuple:
        name = Path(f).name.lower()
        return (f.count("/"), {"main.tex": 0, "paper.tex": 1}.get(name, 2), f)

    return sorted(cands, key=rank)[0]


def read_doc(root: Path, rel: str) -> dict:
    """Read a UTF-8 text file under root; refuse missing, huge, or binary files."""
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
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".texreview-tmp")
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


# ---------- comments (one sidecar file: they annotate the compiled paper) ----------

def _comments_path(root: Path) -> Path:
    return root / SIDECAR_DIR / "comments.json"


def load_comments(root: Path) -> list[dict]:
    cp = _comments_path(root)
    if not cp.is_file():
        return []
    return json.loads(cp.read_text(encoding="utf-8"))


def _save_comments(root: Path, comments: list[dict]) -> None:
    _atomic_write(_comments_path(root), json.dumps(comments, ensure_ascii=False, indent=1))


def add_comment(root: Path, page: int, quote: str, prefix: str, suffix: str,
                file: str | None, line: int | None, comment: str) -> dict:
    entry = {
        "id": uuid.uuid4().hex[:12],
        "page": int(page),
        "quote": quote,
        "prefix": prefix,
        "suffix": suffix,
        "file": file,
        "line": line,
        "comment": comment,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "resolved": False,
    }
    comments = load_comments(root)
    comments.append(entry)
    _save_comments(root, comments)
    return entry


def _find_comment(comments: list[dict], cid: str) -> dict:
    for c in comments:
        if c["id"] == cid:
            return c
    raise RequestError(404, f"no such comment: {cid}")


def update_comment(root: Path, cid: str, fields: dict) -> dict:
    comments = load_comments(root)
    c = _find_comment(comments, cid)
    for k in ("resolved", "comment", "reply", "fixed"):
        if k in fields:
            c[k] = fields[k]
    _save_comments(root, comments)
    return c


def delete_comment(root: Path, cid: str) -> None:
    comments = load_comments(root)
    comments.remove(_find_comment(comments, cid))
    _save_comments(root, comments)


# ---------- compile (latexmk, one background job at a time) ----------

_compile = {"running": False, "ok": None, "log": "", "finished": 0.0}
_compile_lock = threading.Lock()


def latexmk_error_tail(log: str, limit: int = 4000) -> str:
    """The '!'-error blocks if any, else the last lines - capped for the UI."""
    lines = log.splitlines()
    bangs = [i for i, ln in enumerate(lines) if ln.startswith("!")]
    if bangs:
        keep: list[str] = []
        for i in bangs[:8]:
            keep.extend(lines[i:i + 3])
        text = "\n".join(keep)
    else:
        text = "\n".join(lines[-40:])
    return text[-limit:]


def _run_compile(root: Path, main_rel: str) -> None:
    ok, log = False, ""
    try:
        p = subprocess.run(
            ["latexmk", "-pdf", "-synctex=1", "-interaction=nonstopmode", main_rel],
            cwd=root, capture_output=True, text=True, timeout=COMPILE_TIMEOUT)
        ok = p.returncode == 0
        log = "" if ok else latexmk_error_tail(p.stdout + "\n" + p.stderr)
    except FileNotFoundError:
        log = "latexmk not found on PATH - install TeX Live / MacTeX"
    except subprocess.TimeoutExpired:
        log = f"compile timed out after {COMPILE_TIMEOUT}s"
    with _compile_lock:
        _compile.update(running=False, ok=ok, log=log, finished=time.time())


def start_compile(root: Path, main_rel: str) -> dict:
    with _compile_lock:
        if _compile["running"]:
            raise RequestError(409, "a compile is already running")
        _compile.update(running=True, ok=None, log="")
    threading.Thread(target=_run_compile, args=(root, main_rel), daemon=True).start()
    return {"started": True}


def compile_status() -> dict:
    with _compile_lock:
        return dict(_compile)


# ---------- SyncTeX (click <-> source, both directions) ----------

def parse_synctex_edit(out: str) -> dict:
    """First record of `synctex edit` output -> {'input': path, 'line': int}."""
    rec: dict = {}
    for ln in out.splitlines():
        if ln.startswith("Input:") and "input" not in rec:
            rec["input"] = ln[len("Input:"):].strip()
        elif ln.startswith("Line:") and "line" not in rec:
            rec["line"] = int(ln[len("Line:"):].strip())
        if "input" in rec and "line" in rec:
            return rec
    raise RequestError(404, "SyncTeX has no source mapping for that spot")


def parse_synctex_view(out: str) -> dict:
    """First record of `synctex view` output -> {'page': int, 'h','v','W','H': floats}."""
    rec: dict = {}
    prefixes = {"Page:": "page", "h:": "h", "v:": "v", "W:": "W", "H:": "H"}
    for ln in out.splitlines():
        for pref, name in prefixes.items():
            if ln.startswith(pref) and name not in rec:
                rec[name] = float(ln[len(pref):].strip())
        if len(rec) == len(prefixes):
            break
    if "page" not in rec:
        raise RequestError(404, "SyncTeX has no PDF mapping for that line")
    return {"page": int(rec["page"]), "h": rec.get("h", 0.0), "v": rec.get("v", 0.0),
            "W": rec.get("W", 0.0), "H": rec.get("H", 0.0)}


def _run_synctex(root: Path, args: list[str]) -> str:
    try:
        p = subprocess.run(["synctex", *args], cwd=root,
                           capture_output=True, text=True, timeout=10)
    except FileNotFoundError:
        raise RequestError(500, "synctex CLI not found - install TeX Live / MacTeX")
    except subprocess.TimeoutExpired:
        raise RequestError(504, "synctex timed out")
    return p.stdout


def synctex_edit(root: Path, pdf_rel: str, page: int, x: float, y: float) -> dict:
    """PDF point (page, x, y in pt from the page's top-left) -> {'file': rel, 'line': n}."""
    out = _run_synctex(root, ["edit", "-o", f"{int(page)}:{x:.2f}:{y:.2f}:{pdf_rel}"])
    rec = parse_synctex_edit(out)
    src = Path(rec["input"])
    if not src.is_absolute():
        src = root / src
    try:
        rel = src.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        raise RequestError(404, f"maps outside the project: {src.name} (class/package file)")
    if not (root / rel).is_file():
        raise RequestError(404, f"mapped file missing: {rel}")
    return {"file": rel, "line": rec["line"]}


def synctex_view(root: Path, pdf_rel: str, tex_rel: str, line: int) -> dict:
    """Source line -> PDF box. Tries the path as-is and ./-prefixed (synctex records vary)."""
    last: RequestError | None = None
    for name in (tex_rel, "./" + tex_rel):
        out = _run_synctex(root, ["view", "-i", f"{int(line)}:1:{name}", "-o", pdf_rel])
        try:
            return parse_synctex_view(out)
        except RequestError as e:
            last = e
    raise last if last else RequestError(404, "SyncTeX lookup failed")


# ---------- paper artifacts + export ----------

def pdf_info(root: Path, main_rel: str) -> dict:
    pdf = Path(main_rel).with_suffix(".pdf").as_posix()
    p = root / pdf
    has_synctex = any((root / Path(main_rel).with_suffix(sfx).as_posix()).is_file()
                      for sfx in (".synctex.gz", ".synctex"))
    return {"pdf": pdf, "main": main_rel, "exists": p.is_file(),
            "mtime": p.stat().st_mtime if p.is_file() else 0, "synctex": has_synctex}


def export_text(root: Path, main_rel: str) -> str:
    """Open comments as one AI-ready blob with file:line targets and a reply loop."""
    open_comments = [c for c in load_comments(root) if not c["resolved"]]
    parts = [
        "Address each reviewer comment on the compiled paper (LaTeX sources in this",
        f"repo, main file `{main_rel}`). Each comment quotes the PDF text it is about",
        "and, where SyncTeX could resolve it, the source location `file:line` to edit.",
        "- If you can edit this repository: fix each comment in the LaTeX sources, then",
        f"  update its entry in `{SIDECAR_DIR}/comments.json` (match by id): set",
        '  `"resolved": true`, add a one-sentence `"reply"` describing the fix, and a',
        '  `"fixed"` field quoting a short exact snippet of the NEW text you wrote, so',
        "  the UI can highlight where the fix landed after the next compile.",
        "- If you cannot edit files: return the revised LaTeX for each spot, then end",
        "  with a RESOLUTIONS block, one line per addressed comment, formatted",
        "  `<id>: <one-sentence reply>`, so an in-repo agent can apply it.",
        "",
    ]
    if open_comments:
        parts += ["## Reviewer comments", ""]
        for i, c in enumerate(open_comments, 1):
            where = (f"`{c['file']}:{c['line']}`, page {c['page']}"
                     if c.get("file") else f"page {c['page']}")
            parts.append(f'{i}. [id: {c["id"]}] {where} > "{c["quote"]}"')
            parts.append(f"   {c['comment']}")
            parts.append("")
    else:
        parts += ["(no open comments)", ""]
    return "\n".join(parts)


PAGE = r"""<!doctype html>
<html><head><meta charset="utf-8"><title>texreview</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root { --line:#e2e2e2; --accent:#2563eb; }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:#1f2328; }
  #app { display:grid; grid-template-columns:210px 1fr 6px 1fr 300px; height:100vh; }
  /* grid/flex items default to min-height:auto, so a long PDF would stretch the grid
     past 100vh and scroll the page (taking the toolbars with it); force pane scrolling */
  #app > * { min-width:0; min-height:0; }
  #pdfwrap, #editor { min-height:0; }
  #gutter { cursor:col-resize; background:#fafafa; border-left:1px solid var(--line);
            border-right:1px solid var(--line); }
  #gutter:hover, #gutter.dragging { background:var(--accent); }
  #side { overflow-y:auto; border-right:1px solid var(--line); padding:10px; font-size:13px; }
  #side .dir { font-weight:600; margin-top:6px; color:#555; }
  #side .dir .count { font-weight:400; color:#aaa; }
  #side button { display:block; width:100%; text-align:left; border:0; background:none;
                 padding:3px 6px; border-radius:5px; cursor:pointer; font:inherit; color:#333; }
  #side button:hover { background:#f0f3f8; }
  #side button.active { background:#e3ecfd; color:var(--accent); }
  #srcpane { display:flex; flex-direction:column; min-width:0; }
  .bar { display:flex; gap:8px; align-items:center; padding:8px 12px; border-bottom:1px solid var(--line); }
  .bar .path { font-weight:600; font-size:13px; margin-right:auto; overflow:hidden;
               text-overflow:ellipsis; white-space:nowrap; }
  .bar button { border:1px solid var(--line); background:#fff; border-radius:6px;
                padding:4px 11px; cursor:pointer; font:13px inherit; }
  .bar button:hover { border-color:var(--accent); color:var(--accent); }
  .bar button:disabled { opacity:.5; cursor:default; }
  #editor { flex:1; width:100%; border:0; outline:none; resize:none; padding:14px 16px;
            font:13px/1.55 ui-monospace,Menlo,monospace; color:#24292f; }
  #pdfpane { display:flex; flex-direction:column; min-width:0; }
  #status { font-size:12px; color:#666; }
  #warnbar { display:none; background:#fff7e0; border-bottom:1px solid #eedc9a; color:#8a6d1a;
             font-size:12px; padding:5px 12px; }
  #pdfwrap { flex:1; overflow:auto; background:#585c60; position:relative; }
  #pages { padding:6px 0; }
  #pages .empty { color:#ddd; text-align:center; padding:40px 20px; }
  .page { position:relative; margin:12px auto; background:#fff; box-shadow:0 1px 8px rgba(0,0,0,.4); }
  .page canvas { display:block; }
  .textLayer { position:absolute; inset:0; overflow:hidden; line-height:1; }
  .textLayer span, .textLayer br { color:transparent; position:absolute; white-space:pre;
                                   cursor:text; transform-origin:0% 0%; }
  .textLayer ::selection { background:rgba(37,99,235,.35); }
  .textLayer mark { color:transparent; background:rgba(255,224,102,.5);
                    border-bottom:2px solid #eab308; cursor:pointer; }
  .textLayer mark.resolvedmark { background:rgba(52,168,83,.22); border-bottom-color:#7fc79b; }
  @keyframes markpulse { 50% { background:rgba(255,145,45,.75); } }
  .textLayer mark.flash { animation:markpulse .55s ease-in-out 3; }
  .syncflash { position:absolute; background:rgba(255,224,102,.45); border:1px solid #eab308;
               border-radius:3px; pointer-events:none; z-index:3;
               animation:markpulse .55s ease-in-out 3; }
  #errlog { display:none; max-height:38%; overflow:auto; border-top:2px solid #d33;
            background:#fff5f5; position:relative; }
  #errlog pre { margin:0; padding:10px 12px; font-size:12px; white-space:pre-wrap; }
  #errClose { position:absolute; top:4px; right:8px; border:0; background:none;
              cursor:pointer; font-size:14px; color:#a33; }
  #panel { border-left:1px solid var(--line); overflow-y:auto; padding:12px; font-size:13px; }
  #panelHead { display:flex; align-items:center; justify-content:space-between;
               font-weight:600; margin-bottom:10px; }
  #panelHead button { border:1px solid var(--line); background:#fff; border-radius:6px;
                      padding:4px 11px; cursor:pointer; font:13px inherit; }
  #panelHead button:hover { border-color:var(--accent); color:var(--accent); }
  .card { border:1px solid var(--line); border-radius:8px; padding:9px 11px; margin-bottom:9px; }
  .card.resolved { opacity:.55; }
  .card .q { color:#666; font-style:italic; display:block; margin-bottom:5px; white-space:nowrap;
             overflow:hidden; text-overflow:ellipsis; cursor:pointer; }
  .card .q:hover { text-decoration:underline; }
  .card .loc { color:#2563eb; font-size:11px; display:block; margin-bottom:3px; }
  .card .orphan { color:#b45309; font-size:11px; font-weight:600; }
  .card .reply { color:#0a7d33; font-style:italic; margin-top:5px; }
  .card .editbox { width:100%; height:56px; font:inherit; border:1px solid var(--accent);
                   border-radius:5px; padding:5px; margin-top:2px; }
  details.resolvedlist { margin-top:12px; }
  details.resolvedlist summary { cursor:pointer; color:#666; font-weight:600;
                                 font-size:12px; margin-bottom:8px; user-select:none; }
  .card .meta { color:#999; font-size:11px; margin-top:5px; display:flex; gap:8px; flex-wrap:wrap; }
  .card .meta button { border:0; background:none; color:var(--accent); cursor:pointer;
                       padding:0; font-size:11px; }
  #pop { position:fixed; display:none; background:#fff; border:1px solid var(--line); border-radius:8px;
         box-shadow:0 4px 18px rgba(0,0,0,.13); padding:9px; width:280px; z-index:10; }
  #pop textarea { width:100%; height:64px; font:inherit; border:1px solid var(--line);
                  border-radius:5px; padding:6px; }
  #pop button { margin-top:6px; border:0; background:var(--accent); color:#fff; border-radius:5px;
                padding:5px 12px; cursor:pointer; font:inherit; }
  #toast { position:fixed; bottom:18px; left:50%; transform:translateX(-50%); background:#1f2328;
           color:#fff; border-radius:7px; padding:8px 16px; display:none; font-size:13px; z-index:20; }
  .fontctl { display:inline-flex; gap:3px; }
  .fontctl button { border:1px solid var(--line); background:#fff; border-radius:5px;
                    padding:1px 7px; cursor:pointer; font-size:11px; color:#555; }
  .fontctl button:hover { border-color:var(--accent); color:var(--accent); }
  #panelToggle.off { opacity:.4; }
  .empty { color:#999; }
</style></head><body>
<div id="app">
  <nav id="side"></nav>
  <section id="srcpane">
    <div class="bar" id="bar" style="visibility:hidden">
      <span class="path" id="path"></span>
      <span class="fontctl"><button data-f="editor" data-d="-1" title="Smaller editor text">A−</button><button data-f="editor" data-d="1" title="Larger editor text">A+</button></span>
      <button id="saveBtn">Save</button>
      <button id="revealBtn" title="Highlight this cursor line in the PDF (SyncTeX)">Reveal →</button>
    </div>
    <textarea id="editor" spellcheck="false" placeholder="Loading LaTeX sources..."></textarea>
  </section>
  <div id="gutter" title="drag to resize; double-click to reset"></div>
  <section id="pdfpane">
    <div class="bar">
      <span class="path" id="mainName"></span>
      <span id="status"></span>
      <button id="zOut" title="Zoom out">−</button>
      <button id="zIn" title="Zoom in">+</button>
      <button id="zFit" title="Fit width">Fit</button>
      <button id="compileBtn" title="Run latexmk -pdf -synctex=1">Recompile</button>
      <button id="panelToggle" title="Show / hide the comments panel">💬</button>
    </div>
    <div id="warnbar"></div>
    <div id="pdfwrap"><div id="pages"><p class="empty">Loading PDF…</p></div></div>
    <div id="errlog"><button id="errClose" title="Dismiss">✕</button><pre id="errpre"></pre></div>
  </section>
  <aside id="panel">
    <div id="panelHead">
      <span>Comments</span>
      <span class="fontctl"><button data-f="panel" data-d="-1" title="Smaller comments text">A−</button><button data-f="panel" data-d="1" title="Larger comments text">A+</button></span>
      <button id="exportBtn" title="Copy open comments (with ids, file:line targets, and reply instructions) for any AI">Export</button>
    </div>
    <div id="cards"><p class="empty">Select PDF text to comment.</p></div>
  </aside>
</div>
<div id="pop"><textarea id="popText" placeholder="Comment..."></textarea><br>
  <button id="popAdd">Add comment</button></div>
<div id="toast"></div>
<script src="https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.min.js"></script>
<script>
const $ = id => document.getElementById(id);
const WORKER_URL = "https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js";
let state = null;          // {path, mtime} - the open source file
let mainRel = "";
let pdfDoc = null, pdfScale = 1, zoomFactor = 1, loadedMtime = 0, renderToken = 0;
let pageEls = [];          // .page divs, index = page-1
let comments = [];
let pending = null;        // captured PDF selection awaiting comment text
let lastSel = null;        // survives focus steals (right-click after select)
let dirty = false, compiling = false;

const api = async (url, body) => fetch(url, body ? {method:"POST",
  headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)} : undefined);
const toast = msg => { const t=$("toast"); t.textContent=msg; t.style.display="block";
  setTimeout(()=>t.style.display="none", 2400); };
const setDirty = d => { dirty = d; $("saveBtn").textContent = d ? "Save •" : "Save"; };
const el = n => n.nodeType === 1 ? n : n.parentElement;

/* ---------- sidebar: collapsible folders ---------- */
let allFiles = [];
let collapsed = new Set(JSON.parse(localStorage.getItem("texreview.collapsed") || "[]"));
let collapsedSeeded = localStorage.getItem("texreview.collapsed") !== null;
async function loadFiles() {
  allFiles = await (await api("/api/files")).json();
  if (!collapsedSeeded) {
    // first run: fold every folder except the one holding the open file - a paper repo
    // is mostly tables/, code/ and figures/ you are not reading right now
    const keep = state && state.path.includes("/") ? state.path.split("/")[0] + "/" : null;
    for (const f of allFiles) {
      const dir = f.includes("/") ? f.split("/")[0] + "/" : null;
      if (dir && dir !== keep) collapsed.add(dir);
    }
    collapsedSeeded = true;
  }
  renderSidebar();
}
function renderSidebar() {
  const tree = {};
  for (const f of allFiles) {
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
function renderTree(node, elx, depth, prefix) {
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
        localStorage.setItem("texreview.collapsed", JSON.stringify([...collapsed]));
        renderSidebar();
      };
      elx.appendChild(d);
      if (open) renderTree(node[key], elx, depth + 1, path);
    } else {
      const b = document.createElement("button");
      b.textContent = key; b.dataset.path = node[key]; b.style.paddingLeft = (depth*12+6) + "px";
      b.classList.toggle("active", state && state.path === node[key]);
      b.onclick = () => openDoc(node[key]);
      elx.appendChild(b);
    }
  }
}

/* ---------- source editor ---------- */
async function openDoc(path) {
  if (dirty && !confirm("Unsaved changes will be lost. Switch file anyway?")) return;
  const res = await api("/api/doc?path=" + encodeURIComponent(path));
  if (!res.ok) { toast((await res.json()).error); return; }
  const d = await res.json();
  state = { path, mtime: d.mtime };
  $("editor").value = d.content;
  setDirty(false);
  $("bar").style.visibility = "visible";
  $("path").textContent = path;
  // a file opened by a PDF click may live in a folded folder: reveal it so the
  // active highlight is not hidden
  const parts = path.split("/");
  for (let i = 1; i < parts.length; i++) collapsed.delete(parts.slice(0, i).join("/") + "/");
  renderSidebar();
}
$("editor").addEventListener("input", () => { if (state) setDirty(true); });
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
  toast("Saved - Recompile to update the PDF");
}
$("saveBtn").onclick = () => save(false);
document.addEventListener("keydown", ev => {
  if ((ev.metaKey || ev.ctrlKey) && ev.key === "s") { ev.preventDefault(); save(false); }
});
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
async function gotoSource(file, line) {
  if (!state || state.path !== file) await openDoc(file);
  const lines = $("editor").value.split("\n");
  const ln = Math.max(1, Math.min(line, lines.length));
  const pos = lines.slice(0, ln - 1).reduce((a, l) => a + l.length + 1, 0);
  placeCursor(pos, pos + (lines[ln - 1] || "").length);
}

/* ---------- PDF pane ---------- */
async function initWorker() {
  try {
    const src = await (await fetch(WORKER_URL)).text();
    pdfjsLib.GlobalWorkerOptions.workerSrc =
      URL.createObjectURL(new Blob([src], {type: "text/javascript"}));
  } catch (e) { pdfjsLib.GlobalWorkerOptions.workerSrc = WORKER_URL; }
}
async function loadPdf() {
  const info = await (await api("/api/pdfinfo")).json();
  $("mainName").textContent = info.pdf;
  const warn = $("warnbar");
  if (!info.exists) {
    warn.style.display = "none";
    $("pages").innerHTML = '<p class="empty">No compiled PDF yet - hit Recompile.</p>';
    pdfDoc = null; loadedMtime = 0; pageEls = [];
    renderPanel();
    return;
  }
  if (!info.synctex) {
    warn.textContent = "No .synctex.gz next to the PDF - click-to-source is disabled. Recompile regenerates it.";
    warn.style.display = "block";
  } else warn.style.display = "none";
  loadedMtime = info.mtime;
  pdfDoc = await pdfjsLib.getDocument("/api/pdf?ts=" + info.mtime).promise;
  await renderAllPages();
  applyPdfHighlights();
}
async function renderAllPages() {
  const my = ++renderToken;
  const wrap = $("pdfwrap");
  const frac = wrap.scrollHeight ? wrap.scrollTop / wrap.scrollHeight : 0;
  const pages = $("pages");
  pages.innerHTML = ""; pageEls = [];
  const first = await pdfDoc.getPage(1);
  const base = (wrap.clientWidth - 36) / first.getViewport({scale: 1}).width;
  pdfScale = Math.max(0.35, Math.min(5, base * zoomFactor));
  const dpr = window.devicePixelRatio || 1;
  for (let n = 1; n <= pdfDoc.numPages; n++) {
    if (my !== renderToken) return;
    const page = await pdfDoc.getPage(n);
    const vp = page.getViewport({scale: pdfScale});
    const pd = document.createElement("div");
    pd.className = "page"; pd.dataset.page = n;
    pd.style.width = vp.width + "px"; pd.style.height = vp.height + "px";
    pd.style.setProperty("--scale-factor", vp.scale);
    const canvas = document.createElement("canvas");
    canvas.width = Math.floor(vp.width * dpr); canvas.height = Math.floor(vp.height * dpr);
    canvas.style.width = vp.width + "px"; canvas.style.height = vp.height + "px";
    const tl = document.createElement("div"); tl.className = "textLayer";
    pd.append(canvas, tl);
    pages.appendChild(pd); pageEls.push(pd);
    await page.render({canvasContext: canvas.getContext("2d"), viewport: vp,
                       transform: dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : null}).promise;
    const tc = await page.getTextContent();
    await pdfjsLib.renderTextLayer({textContentSource: tc, textContent: tc,
                                    container: tl, viewport: vp, textDivs: []}).promise;
  }
  wrap.scrollTop = frac * wrap.scrollHeight;
}
$("zIn").onclick = () => { zoomFactor = Math.min(4, zoomFactor * 1.15); rezoom(); };
$("zOut").onclick = () => { zoomFactor = Math.max(0.4, zoomFactor / 1.15); rezoom(); };
$("zFit").onclick = () => { zoomFactor = 1; rezoom(); };
async function rezoom() {
  if (!pdfDoc) return;
  await renderAllPages();
  applyPdfHighlights();
}

/* ---------- compile ---------- */
function setCompiling(on) {
  compiling = on;
  $("compileBtn").disabled = on;
  $("status").textContent = on ? "compiling…" : "";
}
$("compileBtn").onclick = async () => {
  const r = await api("/api/compile", {});
  if (!r.ok) { toast((await r.json()).error); return; }
  setCompiling(true);
  pollCompile();
};
async function pollCompile() {
  const s = await (await api("/api/compile")).json();
  if (s.running) { setTimeout(pollCompile, 700); return; }
  setCompiling(false);
  if (s.ok) { $("errlog").style.display = "none"; toast("Compiled ✓"); loadPdf(); }
  else {
    $("errpre").textContent = s.log || "compile failed (no log)";
    $("errlog").style.display = "block";
    toast("Compile failed");
  }
}
$("errClose").onclick = () => $("errlog").style.display = "none";
setInterval(async () => {
  // external builds (editor, latexmk -pvc) also refresh the pane
  if (compiling || document.hidden) return;
  try {
    const info = await (await api("/api/pdfinfo")).json();
    if (info.exists && info.mtime !== loadedMtime) loadPdf();
  } catch (e) {}
}, 2500);

/* ---------- PDF click -> source, select -> comment ---------- */
function capturePdfSelection() {
  const sel = window.getSelection();
  if (!sel.rangeCount || sel.isCollapsed) return null;
  const range = sel.getRangeAt(0);
  const pageDiv = el(range.startContainer)?.closest?.(".page");
  if (!pageDiv || !$("pdfwrap").contains(pageDiv)) return null;
  const tl = pageDiv.querySelector(".textLayer");
  const pre = document.createRange();
  pre.selectNodeContents(tl); pre.setEnd(range.startContainer, range.startOffset);
  const start = pre.toString().length;
  let end;
  if (el(range.endContainer)?.closest?.(".page") === pageDiv) {
    const pre2 = document.createRange();
    pre2.selectNodeContents(tl); pre2.setEnd(range.endContainer, range.endOffset);
    end = pre2.toString().length;
  } else end = tl.textContent.length;      // selection ran past the page: clamp
  const text = tl.textContent;
  const quote = text.slice(start, end);
  if (!quote.trim()) return null;
  const rect = (range.getClientRects()[0] || range.getBoundingClientRect());
  const prect = pageDiv.getBoundingClientRect();
  lastSel = {
    page: +pageDiv.dataset.page, quote,
    prefix: text.slice(Math.max(0, start - 30), start),
    suffix: text.slice(end, end + 30),
    x: (rect.left - prect.left) / pdfScale,
    y: (rect.top - prect.top + rect.height / 2) / pdfScale,
  };
  return lastSel;
}
function openCommentPopover(x, y) {
  const cap = capturePdfSelection() || lastSel;
  if (!cap) return false;
  pending = cap;
  const pop = $("pop");
  pop.style.display = "block";
  pop.style.left = Math.min(x, innerWidth - 300) + "px";
  pop.style.top = (y + 8) + "px";
  $("popText").value = ""; $("popText").focus();
  return true;
}
$("pdfwrap").addEventListener("mouseup", ev => {
  if (ev.button !== 0) return;
  setTimeout(() => {
    const sel = window.getSelection();
    if (!sel.rangeCount || sel.isCollapsed) { $("pop").style.display = "none"; return; }
    if (!el(sel.getRangeAt(0).startContainer)?.closest?.(".page")) return;
    const rect = sel.getRangeAt(0).getBoundingClientRect();
    openCommentPopover(rect.left, rect.bottom);
  }, 0);
});
$("pdfwrap").addEventListener("contextmenu", ev => {
  if (openCommentPopover(ev.clientX, ev.clientY)) ev.preventDefault();
});
$("pdfwrap").addEventListener("click", async ev => {
  const sel = window.getSelection();
  if (sel && !sel.isCollapsed) return;               // a drag-select, not a click
  if (ev.target.closest("mark")) return;             // mark clicks focus the card
  const pageDiv = ev.target.closest(".page");
  if (!pageDiv) return;
  const rect = pageDiv.getBoundingClientRect();
  const r = await api("/api/sync/edit", {
    page: +pageDiv.dataset.page,
    x: (ev.clientX - rect.left) / pdfScale,
    y: (ev.clientY - rect.top) / pdfScale,
  });
  if (!r.ok) { toast((await r.json()).error); return; }
  const {file, line} = await r.json();
  gotoSource(file, line);
});
$("popAdd").onclick = async () => {
  const text = $("popText").value.trim();
  const p = pending;
  if (!text || !p) return;
  $("pop").style.display = "none"; pending = null;
  let loc = {file: null, line: null};
  try {
    const r = await api("/api/sync/edit", {page: p.page, x: p.x, y: p.y});
    if (r.ok) loc = await r.json();
  } catch (e) {}
  await api("/api/comment/add", {page: p.page, quote: p.quote, prefix: p.prefix,
    suffix: p.suffix, file: loc.file, line: loc.line, comment: text});
  refreshComments();
};
document.addEventListener("mousedown", ev => {
  if (!$("pop").contains(ev.target)) $("pop").style.display = "none";
});

/* ---------- reveal: cursor line -> PDF box ---------- */
$("revealBtn").onclick = async () => {
  if (!state) return;
  if (!state.path.endsWith(".tex")) { toast("Reveal works from .tex files"); return; }
  const pos = $("editor").selectionStart;
  const line = $("editor").value.slice(0, pos).split("\n").length;
  const r = await api("/api/sync/view", {file: state.path, line});
  if (!r.ok) { toast((await r.json()).error); return; }
  const {page, h, v, W, H} = await r.json();
  flashPdfBox(page, h, v, W, H);
};
function flashPdfBox(page, h, v, W, H) {
  const pd = pageEls[page - 1];
  if (!pd) { toast("Page " + page + " not rendered"); return; }
  const hh = Math.max(H, 8), ww = W > 2 ? W : 260;
  const box = document.createElement("div");
  box.className = "syncflash";
  box.style.left = (h * pdfScale) + "px";
  box.style.top = ((v - hh) * pdfScale) + "px";
  box.style.width = (ww * pdfScale) + "px";
  box.style.height = (hh * pdfScale + 4) + "px";
  pd.appendChild(box);
  $("pdfwrap").scrollTo({top: pd.offsetTop + (v - hh) * pdfScale - $("pdfwrap").clientHeight / 2,
                         behavior: "smooth"});
  setTimeout(() => box.remove(), 2400);
}

/* ---------- comment highlights + panel ---------- */
function textNodesUnder(elx) {
  const w = document.createTreeWalker(elx, NodeFilter.SHOW_TEXT), out = [];
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
  let pos = 0, first = null;
  for (const node of textNodesUnder(container)) {
    const len = node.length, a = Math.max(start - pos, 0), b = Math.min(end - pos, len);
    if (a < b) {
      const r = document.createRange();
      r.setStart(node, a); r.setEnd(node, b);
      const mk = makeEl();
      try { r.surroundContents(mk); first = first || mk; } catch (e) {}
    }
    pos += len;
    if (pos >= end) break;
  }
  return first;
}
function applyPdfHighlights() {
  for (const mk of $("pdfwrap").querySelectorAll(".textLayer mark"))
    mk.replaceWith(...mk.childNodes);
  for (const pd of pageEls) pd.querySelector(".textLayer").normalize();
  for (const c of comments) {
    const target = (c.resolved && c.fixed) ? c.fixed : c.quote;
    c.anchored = false;
    if (!target) continue;
    // stored page first, then the rest (layout may have shifted after a recompile)
    const order = [...new Set([Math.max(0, (c.page || 1) - 1),
                               ...pageEls.map((_, i) => i)])];
    for (const idx of order) {
      const tl = pageEls[idx]?.querySelector(".textLayer");
      if (!tl) continue;
      const text = tl.textContent;
      const start = (c.resolved && c.fixed) ? text.indexOf(c.fixed) : findAnchor(text, {...c, quote: target});
      if (start < 0) continue;
      wrapTextRange(tl, start, start + target.length, () => {
        const mk = document.createElement("mark");
        mk.dataset.id = c.id;
        if (c.resolved) mk.className = "resolvedmark";
        mk.onclick = ev => { ev.stopPropagation(); focusCard(c.id); };
        return mk;
      });
      c.anchored = true;
      break;
    }
  }
  renderPanel();
}
let resolvedOpen = false;
function commentCard(c) {
  const card = document.createElement("div");
  card.className = "card" + (c.resolved ? " resolved" : "");
  card.id = "card-" + c.id;
  const loc = document.createElement("span"); loc.className = "loc";
  loc.textContent = (c.file ? c.file + ":" + c.line + " · " : "") + "p." + c.page;
  const q = document.createElement("span"); q.className = "q"; q.textContent = '"' + c.quote + '"';
  q.title = "Show this passage in the PDF";
  q.onclick = () => locateComment(c);
  const body = document.createElement("div"); body.textContent = c.comment;
  card.append(loc, q, body);
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
        await api("/api/comment/update", {id: c.id, comment: v});
      refreshComments();
    };
  };
  const res = document.createElement("button");
  res.textContent = c.resolved ? "Reopen" : "Resolve";
  res.onclick = async () => { await api("/api/comment/update",
    {id: c.id, resolved: !c.resolved}); refreshComments(); };
  const del = document.createElement("button");
  del.textContent = "Delete";
  del.onclick = async () => { await api("/api/comment/delete", {id: c.id}); refreshComments(); };
  meta.append(edit, res, del);
  card.appendChild(meta);
  return card;
}
function locateComment(c) {
  const mk = document.querySelector('.textLayer mark[data-id="' + c.id + '"]');
  if (mk) {
    mk.scrollIntoView({behavior: "smooth", block: "center"});
    mk.classList.add("flash");
    setTimeout(() => mk.classList.remove("flash"), 2000);
    return;
  }
  const pd = pageEls[(c.page || 1) - 1];
  if (pd) {
    $("pdfwrap").scrollTo({top: pd.offsetTop - 20, behavior: "smooth"});
    toast("Passage not found on the current PDF (recompiled since?) - showing its page");
  } else toast("Can't locate this passage anymore");
}
function renderPanel() {
  const panel = $("cards"); panel.innerHTML = "";
  if (!comments.length) {
    panel.innerHTML = '<p class="empty">No comments. Select PDF text to add one.</p>';
    return;
  }
  const open = comments.filter(c => !c.resolved);
  const done = comments.filter(c => c.resolved);
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
  comments = await (await api("/api/comments")).json();
  applyPdfHighlights();
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
$("exportBtn").onclick = async () => {
  const res = await api("/api/export");
  await navigator.clipboard.writeText(await res.text());
  toast("Copied comments (with file:line targets) to clipboard");
};

/* ---------- draggable divider + panel toggle + fonts ---------- */
let panelVisible = localStorage.getItem("texreview.panel") !== "hidden";
let splitFrac = 0.5;
function applyLayout() {
  $("panel").style.display = panelVisible ? "" : "none";
  $("app").style.gridTemplateColumns =
    `210px ${splitFrac}fr 6px ${1 - splitFrac}fr ${panelVisible ? "300px" : "0"}`;
  $("panelToggle").classList.toggle("off", !panelVisible);
}
$("panelToggle").onclick = () => {
  panelVisible = !panelVisible;
  localStorage.setItem("texreview.panel", panelVisible ? "shown" : "hidden");
  applyLayout();
};
$("gutter").addEventListener("mousedown", e => {
  e.preventDefault();
  $("gutter").classList.add("dragging");
  document.body.style.userSelect = "none";
  const move = ev => {
    const left = 210, right = panelVisible ? 300 : 0, gw = 6;
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
$("gutter").addEventListener("dblclick", () => { splitFrac = 0.5; applyLayout(); });
const FONT_DEFAULTS = { editor: 13, panel: 13 };
const fonts = {};
for (const k in FONT_DEFAULTS)
  fonts[k] = +(localStorage.getItem("texreview.font." + k) || FONT_DEFAULTS[k]);
function applyFonts() {
  $("editor").style.fontSize = fonts.editor + "px";
  $("panel").style.fontSize = fonts.panel + "px";
}
document.addEventListener("click", ev => {
  const b = ev.target.closest(".fontctl button");
  if (!b || !b.dataset.f) return;
  const k = b.dataset.f;
  fonts[k] = Math.min(24, Math.max(10, fonts[k] + (+b.dataset.d)));
  localStorage.setItem("texreview.font." + k, fonts[k]);
  applyFonts();
});
applyFonts();
applyLayout();

/* ---------- boot ---------- */
(async function boot() {
  const info = await (await api("/api/root")).json();
  mainRel = info.main;
  await initWorker();
  await loadFiles();
  await openDoc(mainRel);
  comments = await (await api("/api/comments")).json();
  await loadPdf();
})();
</script></body></html>"""


def route(root: Path, main_rel: str, method: str, path: str,
          query: dict, body: dict) -> tuple[int, str, object]:
    """Pure dispatcher: (status, content-type, payload). Payload str/bytes => raw, else JSON."""
    try:
        if method == "GET" and path == "/":
            return 200, "text/html; charset=utf-8", PAGE
        if method == "GET" and path == "/api/root":
            return 200, "application/json", {"root": str(root), "main": main_rel,
                                             "tool": "texreview"}
        if method == "GET" and path == "/api/files":
            return 200, "application/json", list_tex_files(root)
        if method == "GET" and path == "/api/doc":
            rel = query["path"][0]
            return 200, "application/json", {**read_doc(root, rel), "path": rel}
        if method == "POST" and path == "/api/doc":
            return 200, "application/json", write_doc(
                root, body["path"], body["content"], body.get("mtime"))
        if method == "GET" and path == "/api/pdfinfo":
            return 200, "application/json", pdf_info(root, main_rel)
        if method == "GET" and path == "/api/pdf":
            p = safe_resolve(root, pdf_info(root, main_rel)["pdf"])
            if not p.is_file():
                raise RequestError(404, "no compiled PDF - run Recompile")
            if p.stat().st_size > MAX_PDF_BYTES:
                raise RequestError(413, "PDF too large")
            return 200, "application/pdf", p.read_bytes()
        if method == "POST" and path == "/api/compile":
            return 200, "application/json", start_compile(root, main_rel)
        if method == "GET" and path == "/api/compile":
            return 200, "application/json", compile_status()
        if method == "POST" and path == "/api/sync/edit":
            pdf = pdf_info(root, main_rel)["pdf"]
            return 200, "application/json", synctex_edit(
                root, pdf, int(body["page"]), float(body["x"]), float(body["y"]))
        if method == "POST" and path == "/api/sync/view":
            pdf = pdf_info(root, main_rel)["pdf"]
            safe_resolve(root, body["file"])
            return 200, "application/json", synctex_view(
                root, pdf, body["file"], int(body["line"]))
        if method == "GET" and path == "/api/export":
            return 200, "text/plain; charset=utf-8", export_text(root, main_rel)
        if method == "GET" and path == "/api/comments":
            return 200, "application/json", load_comments(root)
        if method == "POST" and path == "/api/comment/add":
            return 200, "application/json", add_comment(
                root, body["page"], body["quote"], body.get("prefix", ""),
                body.get("suffix", ""), body.get("file"), body.get("line"), body["comment"])
        if method == "POST" and path == "/api/comment/update":
            fields = {k: body[k] for k in ("resolved", "comment", "reply", "fixed") if k in body}
            return 200, "application/json", update_comment(root, body["id"], fields)
        if method == "POST" and path == "/api/comment/delete":
            delete_comment(root, body["id"])
            return 200, "application/json", {"ok": True}
        return 404, "application/json", {"error": f"no such route: {method} {path}"}
    except RequestError as e:
        return e.status, "application/json", {"error": e.message}
    except (KeyError, IndexError, TypeError, ValueError):
        return 400, "application/json", {"error": "missing or invalid parameter"}


class Handler(BaseHTTPRequestHandler):
    root: Path = Path(".")
    main_rel: str = "main.tex"

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
        self._send(*route(self.root, self.main_rel, "GET", u.path, parse_qs(u.query), {}))

    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            self._send(400, "application/json", {"error": "invalid JSON body"})
            return
        self._send(*route(self.root, self.main_rel, "POST", u.path, parse_qs(u.query), body))


def find_existing(root: Path, start: int) -> str | None:
    """Probe nearby ports for a texreview instance already serving this root."""
    for port in range(start, start + 20):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/root", timeout=0.3) as r:
                info = json.loads(r.read())
                if info.get("root") == str(root) and info.get("tool") == "texreview":
                    return f"http://127.0.0.1:{port}/"
        except (OSError, ValueError):
            continue
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="texreview: local LaTeX + PDF review UI")
    ap.add_argument("--port", type=int, default=8378)
    ap.add_argument("--open", action="store_true", help="open the browser")
    ap.add_argument("--root", default=".", help="manuscript repo (default: resolve from cwd)")
    ap.add_argument("--main", default=None, help="main .tex file (default: auto-detect)")
    args = ap.parse_args()
    root = find_root(Path(args.root).resolve())
    main_rel = find_main_tex(root, args.main)
    for tool, needed_for in (("latexmk", "Recompile"), ("synctex", "click-to-source sync")):
        if shutil.which(tool) is None:
            print(f"warning: {tool} not found on PATH - {needed_for} will not work")
    existing = find_existing(root, args.port)
    if existing:
        print(f"texreview already serving {root}")
        print(f"  {existing}   (reusing the running instance)")
        if args.open:
            webbrowser.open(existing)
        return
    Handler.root = root
    Handler.main_rel = main_rel
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
    print(f"texreview serving {root} (main: {main_rel})")
    print(f"  {url}   (Ctrl-C to stop; comments land in {root / SIDECAR_DIR}/)")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
