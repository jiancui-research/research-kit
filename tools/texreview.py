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
import hashlib
import json
import os
import re
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
# A server bakes its HTML in at startup, so one left running after the tool is updated
# keeps serving the old UI. Fingerprint the source so a stale instance is not reused.
try:
    BUILD = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]
except OSError:
    BUILD = "unknown"


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


_SECT_RE = re.compile(r"\\(part|chapter|section|subsection|subsubsection)\*?\s*(?:\[[^\]]*\])?\s*\{")
_INC_RE = re.compile(r"\\(?:input|include)\s*\{\s*([^}]+?)\s*\}")
_SECT_LEVEL = {"part": 0, "chapter": 1, "section": 2, "subsection": 3, "subsubsection": 4}
_TITLE_CLEAN = re.compile(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?|[{}$]")


def _strip_comment(line: str) -> str:
    """Drop an unescaped % and everything after it."""
    for i, ch in enumerate(line):
        if ch == "%" and (i == 0 or line[i - 1] != "\\"):
            return line[:i]
    return line


def _braced(s: str, i: int) -> str:
    """s[i] is '{'; return its balanced contents (rest of line when unbalanced)."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{" and (j == 0 or s[j - 1] != "\\"):
            depth += 1
        elif s[j] == "}" and (j == 0 or s[j - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return s[i + 1:j]
    return s[i + 1:]


def outline(root: Path, main_rel: str) -> list[dict]:
    """Headings in reading order, following \\input/\\include out from the main file.

    Document order is what makes this navigable, so includes are walked in place
    rather than collected per file - a section's position depends on where its
    file was pulled in, not on the filename."""
    out: list[dict] = []
    seen: set[str] = set()

    def walk(rel: str, depth: int) -> None:
        if depth > 8 or rel in seen:
            return          # \input cycles are legal LaTeX and would hang us
        seen.add(rel)
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        for n, raw in enumerate(text.splitlines(), 1):
            line = _strip_comment(raw)
            events = [(m.start(), "sect", m) for m in _SECT_RE.finditer(line)]
            events += [(m.start(), "inc", m) for m in _INC_RE.finditer(line)]
            for _, kind, m in sorted(events, key=lambda e: e[0]):
                if kind == "sect":
                    title = _TITLE_CLEAN.sub("", _braced(line, m.end() - 1)).strip()
                    out.append({"level": _SECT_LEVEL[m.group(1)],
                                "title": " ".join(title.split()) or m.group(1),
                                "file": rel, "line": n})
                else:
                    tgt = m.group(1).strip()
                    if not tgt.lower().endswith(".tex"):
                        tgt += ".tex"
                    try:
                        q = safe_resolve(root, tgt)
                    except Exception:
                        continue
                    if q.is_file():
                        walk(q.relative_to(root.resolve()).as_posix(), depth + 1)

    walk(main_rel, 0)
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
    mtime = p.stat().st_mtime      # before the read: a later stat could describe content
    try:                           # newer than what we are about to send, and the client
        content = p.read_text(encoding="utf-8")   # would then save over it unwarned
    except UnicodeDecodeError:
        raise RequestError(415, f"not UTF-8 text: {rel}")
    return {"content": content, "mtime": mtime}


def _atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".texreview-tmp")
    try:
        if path.exists():          # mkstemp makes 0600; keep the file's own mode
            os.chmod(tmp, path.stat().st_mode & 0o7777)
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


# ---------- where you were (server-side so it survives a port change) ----------

def _state_path(root: Path) -> Path:
    return root / SIDECAR_DIR / "state.json"


def load_state(root: Path) -> dict:
    sp = _state_path(root)
    if not sp.is_file():
        return {}
    try:
        st = json.loads(sp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}          # a corrupt state file must never block opening the paper
    return st if isinstance(st, dict) else {}


def save_state(root: Path, st: dict) -> dict:
    """Persist the reading position. Kept server-side rather than in localStorage
    because the port is chosen by scanning for a free one, and a different port is a
    different browser origin - the saved position would be invisible after a restart."""
    keep = {}
    path = st.get("path")
    if isinstance(path, str) and (root / path).is_file():
        keep["path"] = safe_resolve(root, path).relative_to(root.resolve()).as_posix()
    for k in ("sel", "edScroll"):
        v = st.get(k)
        if isinstance(v, (int, float)) and v >= 0:
            keep[k] = int(v)
    pdf = st.get("pdf")
    if isinstance(pdf, dict):
        keep["pdf"] = {k: float(pdf[k]) for k in ("page", "into", "xmid")
                       if isinstance(pdf.get(k), (int, float))}
    _atomic_write(_state_path(root), json.dumps(keep, indent=1))
    # comments.json is meant to be committed - an agent reads it. A cursor position is
    # not: it would churn on every scroll. Ignore it, without touching a file the user wrote.
    gi = root / SIDECAR_DIR / ".gitignore"
    if not gi.exists():
        _atomic_write(gi, "state.json\n")
    return keep


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
                file: str | None, line: int | None, comment: str,
                origin: str = "pdf") -> dict:
    entry = {
        "id": uuid.uuid4().hex[:12],
        # where it was written: "pdf" quotes rendered text, "source" quotes LaTeX. Which
        # pane a click on the comment should open follows from this rather than from
        # whether the quoted words happen to appear in both.
        "origin": "source" if origin == "source" else "pdf",
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


def tex_bin_dir() -> str | None:
    """Directory holding the TeX toolchain, when PATH does not already have it.

    MacTeX installs to /Library/TeX/texbin and puts it on PATH through
    /etc/paths.d/TeX, which only `path_helper` in a *login* shell reads. A server
    launched from anywhere else therefore sees no TeX at all and Recompile fails with
    "latexmk not found" on a machine where it is plainly installed.
    """
    if shutil.which("latexmk"):
        return None
    cands = [Path("/Library/TeX/texbin")]
    for base in (Path("/usr/local/texlive"), Path("/opt/texlive")):
        if base.is_dir():
            cands += sorted(base.glob("*/bin/*"), reverse=True)
    cands += [Path("/opt/homebrew/bin"), Path("/usr/local/bin")]
    for d in cands:
        if (d / "latexmk").is_file():
            return str(d)
    return None


def tex_env() -> dict:
    """Environment for TeX subprocesses. The directory must go on PATH rather than
    just resolving latexmk, because latexmk shells out to pdflatex and bibtex."""
    env = os.environ.copy()
    d = tex_bin_dir()
    if d:
        env["PATH"] = d + os.pathsep + env.get("PATH", "")
    return env


def has_synctex(root: Path, main_rel: str) -> bool:
    return any((root / Path(main_rel).with_suffix(sfx).as_posix()).is_file()
               for sfx in (".synctex.gz", ".synctex"))


def compile_cmd(root: Path, main_rel: str) -> list[str]:
    """latexmk's up-to-date check does not know the requested output set changed, so a
    paper last built without -synctex=1 leaves an fdb that makes every later run a
    no-op ("Nothing to do") and the synctex file is never produced. Force that first
    build so click-to-source and Reveal start working instead of failing forever."""
    force = [] if has_synctex(root, main_rel) else ["-g"]
    return ["latexmk", *force, "-pdf", "-synctex=1", "-interaction=nonstopmode", main_rel]


def _run_compile(root: Path, main_rel: str) -> None:
    ok, log = False, ""
    try:
        # errors="replace": a single latin-1 byte in a .bib or a pasted author name makes
        # latexmk's log undecodable, and the exception would otherwise kill this thread
        # before the status update, wedging "a compile is already running" until restart
        p = subprocess.run(
            compile_cmd(root, main_rel), env=tex_env(), cwd=root, capture_output=True,
            encoding="utf-8", errors="replace", timeout=COMPILE_TIMEOUT)
        ok = p.returncode == 0
        log = "" if ok else latexmk_error_tail(p.stdout + "\n" + p.stderr)
    except FileNotFoundError:
        log = "latexmk not found on PATH - install TeX Live / MacTeX"
    except subprocess.TimeoutExpired:
        log = f"compile timed out after {COMPILE_TIMEOUT}s"
    except Exception as e:                      # never leave the lock latched
        log = f"compile failed: {type(e).__name__}: {e}"
    finally:
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
        raise RequestError(404, "No PDF position for that line - it produces no output "
                                "(preamble, a macro definition, or a comment)")
    return {"page": int(rec["page"]), "h": rec.get("h", 0.0), "v": rec.get("v", 0.0),
            "W": rec.get("W", 0.0), "H": rec.get("H", 0.0)}


def _run_synctex(root: Path, args: list[str]) -> str:
    try:
        p = subprocess.run(["synctex", *args], cwd=root, env=tex_env(),
                           capture_output=True, encoding="utf-8", errors="replace",
                           timeout=10)
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


_TEX_CMD = re.compile(r"\\[a-zA-Z@]+\*?(\[[^\]]*\])?")
_COMMENT = re.compile(r"(?<!\\)%.*$")
# lines that own no prose of their own: SyncTeX blames them for text declared
# elsewhere (acmart typesets \begin{abstract} during \maketitle, for instance)
_STRUCTURAL = re.compile(
    r"^\s*\\(maketitle|begin\{document\}|end\{document\}|input|include|documentclass"
    r"|title|author|affiliation|email|institution|thanks|tableofcontents"
    r"|bibliography|bibliographystyle|newpage|clearpage|balance)\b", re.I)


def _normalize(s: str) -> str:
    """Source or PDF text -> comparable letters+digits, LaTeX markup removed."""
    s = _COMMENT.sub("", s)
    s = _TEX_CMD.sub(" ", s)
    return re.sub(r"[^0-9a-zA-Z]+", " ", s).lower().strip()


def _normalized_index(root: Path, rel: str) -> tuple[str, list[int]]:
    """A file as one normalized string, plus offset -> source line number."""
    try:
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "", []
    parts: list[str] = []
    line_of: list[int] = []
    for i, line in enumerate(text.splitlines(), 1):
        n = _normalize(line)
        if not n:
            continue
        parts.append(n)
        line_of.extend([i] * (len(n) + 1))
    return " ".join(parts), line_of


def find_text(root: Path, needle: str) -> dict | None:
    """Locate PDF text in the sources by normalized substring; -> {'file','line'}.

    Longest probe wins across ALL files before any shorter one is tried, so a full
    match in the section file beats an incidental prefix match in the title."""
    key = _normalize(needle)
    if len(key) < 25:
        return None
    files = [f for f in list_tex_files(root) if f.endswith(".tex")]
    index = {rel: _normalized_index(root, rel) for rel in files}
    for probe in (key, key[:80], key[:50], key[:30]):
        if len(probe) < 25:
            break
        for rel in files:
            hay, line_of = index[rel]
            idx = hay.find(probe)
            if idx >= 0 and line_of:
                return {"file": rel, "line": line_of[min(idx, len(line_of) - 1)]}
    return None


def is_structural(root: Path, rel: str, line: int) -> bool:
    """True when that source line carries no prose, so a text search would do better."""
    try:
        lines = (root / rel).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return True
    if not 1 <= line <= len(lines):
        return True   # past the end of the file it names: not somewhere you can edit
    raw = lines[line - 1]
    return bool(_STRUCTURAL.match(raw)) or not _normalize(raw)


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
    return {"pdf": pdf, "main": main_rel, "exists": p.is_file(),
            "mtime": p.stat().st_mtime if p.is_file() else 0,
            "synctex": has_synctex(root, main_rel)}


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
            bits = []
            if c.get("file"):
                bits.append(f"`{c['file']}:{c['line']}`")
            if c.get("page"):
                bits.append(f"page {c['page']}")
            where = ", ".join(bits) or "location unknown"
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
  /* Catppuccin: Latte by day, Mocha by night. Follows the OS unless you pick one. */
  :root {
    --bg:#eff1f5; --bg-alt:#e6e9ef; --surface:#fff; --raised:#dce0e8;
    --line:#ccd0da; --text:#4c4f69; --muted:#6c6f85; --faint:#9ca0b0;
    --accent:#1e66f5; --accent-soft:#dce4fb; --on-accent:#fff;
    --pdf-bg:#bcc0cc; --page-shadow:rgba(76,79,105,.3);
    --hl:rgba(223,142,29,.28); --hl-line:#df8e1d; --hl-pulse:rgba(254,100,11,.6);
    --ok:#40a02b; --ok-soft:rgba(64,160,43,.18); --ok-line:#a6d29a;
    --warn:#df8e1d; --warn-bg:#faf3e0; --warn-line:#e6d4a8;
    --err:#d20f39; --err-bg:#fdeef1; --sel:rgba(30,102,245,.3);
    --find:rgba(223,142,29,.35); --find-cur:rgba(254,100,11,.5);
    --tex-comment:#8c8fa1; --tex-cmd:#8839ef; --tex-math:#179299;
    --tex-brace:#7c7f93; --tex-env:#df8e1d;
    --brace-hit:rgba(30,102,245,.28); --brace-bad:rgba(210,15,57,.28);
    --reflink:rgba(30,102,245,.16); --reflink-line:rgba(30,102,245,.45);
  }
  :root[data-theme="dark"] {
    --bg:#1e1e2e; --bg-alt:#181825; --surface:#313244; --raised:#45475a;
    --line:#45475a; --text:#cdd6f4; --muted:#a6adc8; --faint:#7f849c;
    --accent:#89b4fa; --accent-soft:#313d57; --on-accent:#11111b;
    --pdf-bg:#11111b; --page-shadow:rgba(0,0,0,.55);
    --hl:rgba(249,226,175,.3); --hl-line:#f9e2af; --hl-pulse:rgba(250,179,135,.65);
    --ok:#a6e3a1; --ok-soft:rgba(166,227,161,.18); --ok-line:#57794f;
    --warn:#f9e2af; --warn-bg:#33302a; --warn-line:#5c5232;
    --err:#f38ba8; --err-bg:#302430; --sel:rgba(137,180,250,.32);
    --find:rgba(249,226,175,.32); --find-cur:rgba(250,179,135,.62);
    --tex-comment:#6c7086; --tex-cmd:#cba6f7; --tex-math:#94e2d5;
    --tex-brace:#9399b2; --tex-env:#f9e2af;
    --brace-hit:rgba(137,180,250,.34); --brace-bad:rgba(243,139,168,.34);
    --reflink:rgba(137,180,250,.2); --reflink-line:rgba(137,180,250,.5);
  }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
         color:var(--text); background:var(--bg); }
  #app { display:grid; grid-template-columns:210px 1fr 6px 1fr 300px; height:100vh; }
  /* grid/flex items default to min-height:auto, so a long PDF would stretch the grid
     past 100vh and scroll the page (taking the toolbars with it); force pane scrolling */
  #app > * { min-width:0; min-height:0; }
  #pdfwrap, #edarea { min-height:0; }
  #gutter { cursor:col-resize; background:var(--bg-alt); border-left:1px solid var(--line);
            border-right:1px solid var(--line); }
  #gutter:hover, #gutter.dragging { background:var(--accent); }
  #side { overflow-y:auto; border-right:1px solid var(--line); padding:10px; font-size:13px;
          background:var(--bg-alt); }
  #side .dir { font-weight:600; margin-top:6px; color:var(--muted); }
  #sidetabs { display:flex; gap:4px; margin:-10px -10px 8px; padding:6px; position:sticky;
              top:-10px; background:var(--bg-alt); border-bottom:1px solid var(--line); z-index:2; }
  #sidetabs button { flex:1; text-align:center; font-size:11px; padding:3px 0; border-radius:4px;
                     border:1px solid transparent; color:var(--muted); }
  #sidetabs button.on { background:var(--surface); color:var(--text); border-color:var(--line); }
  /* the outline is a reading order, so depth is carried by indent and weight, not bullets */
  #side .sec.l0, #side .sec.l1, #side .sec.l2 { font-weight:600; }
  #side .sec.l3, #side .sec.l4 { color:var(--muted); font-size:12px; }
  #side .sec.here { background:var(--accent-soft); color:var(--accent); }
  #side .dir .count { font-weight:400; color:var(--faint); }
  #side button { display:block; width:100%; text-align:left; border:0; background:none;
                 padding:3px 6px; border-radius:5px; cursor:pointer; font:inherit; color:var(--text); }
  #side button:hover { background:var(--raised); }
  #side button.active { background:var(--accent-soft); color:var(--accent); }
  #srcpane { display:flex; flex-direction:column; min-width:0; background:var(--bg); }
  .bar { display:flex; gap:8px; align-items:center; padding:8px 12px;
         border-bottom:1px solid var(--line); background:var(--bg-alt); }
  .bar .path { font-weight:600; font-size:13px; margin-right:auto; overflow:hidden;
               text-overflow:ellipsis; white-space:nowrap; }
  .bar button { border:1px solid var(--line); background:var(--surface); color:var(--text);
                border-radius:6px; padding:4px 11px; cursor:pointer; font:13px inherit; }
  .bar button:hover { border-color:var(--accent); color:var(--accent); }
  .bar button:disabled { opacity:.5; cursor:default; }
  /* A textarea cannot paint line numbers or highlight matches, so an identically
     wrapped mirror div sits under a transparent textarea and paints both. Sizes are
     in em so the A+/A- control scales the gutter with the text. */
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
  #mirror .tc { color:var(--tex-comment); }
  #mirror .tk { color:var(--tex-cmd); }
  #mirror .tm { color:var(--tex-math); }
  #mirror .tb { color:var(--tex-brace); }
  #mirror .te { color:var(--tex-env); }
  #mirror mark { background:var(--find); border-radius:2px; }
  #mirror mark.cur { background:var(--find-cur); }
  /* background only - a weight or style change here would shift the glyph advance and
     slide the mirror out of register with the textarea underneath it */
  #mirror .bm { background:var(--brace-hit); border-radius:2px; }
  #mirror .bm.bad { background:var(--brace-bad); }
  /* the mirror paints the text; the textarea keeps only the caret and the selection */
  #editor { outline:none; resize:none; overflow:auto; background:transparent;
            color:transparent; caret-color:var(--accent); }
  #editor::placeholder { color:var(--faint); }
  #editor::selection { background:var(--sel); }
  #edarea.composing #editor { color:var(--text); }
  #edarea.composing #mirror, #edarea.composing #mirror * { color:transparent; }
  #findbar { display:none; align-items:center; gap:6px; padding:6px 12px;
             border-bottom:1px solid var(--line); background:var(--bg-alt); }
  #findbar input { flex:1; min-width:0; border:1px solid var(--line); border-radius:6px;
                   padding:4px 8px; font:13px inherit; outline:none;
                   background:var(--surface); color:var(--text); }
  #findbar input:focus { border-color:var(--accent); }
  #findbar button { border:1px solid var(--line); background:var(--surface); color:var(--text);
                    border-radius:6px; padding:3px 9px; cursor:pointer; font:13px inherit; }
  #findbar button:hover { border-color:var(--accent); color:var(--accent); }
  #findCount { font-size:12px; color:var(--faint); min-width:44px; text-align:right; }
  #pdfpane { display:flex; flex-direction:column; min-width:0; }
  #status { font-size:12px; color:var(--muted); }
  #autoWrap { display:inline-flex; align-items:center; gap:3px; font-size:12px; color:var(--muted);
              user-select:none; cursor:pointer; }
  #autoWrap input { margin:0; cursor:pointer; accent-color:var(--accent); }
  #warnbar { display:none; background:var(--warn-bg); border-bottom:1px solid var(--warn-line);
             color:var(--warn); font-size:12px; padding:5px 12px; }
  #pdfwrap { flex:1; overflow:auto; background:var(--pdf-bg); position:relative; }
  #pages { padding:6px 0; transform-origin:top center; }
  #pages .empty { color:var(--faint); text-align:center; padding:40px 20px; }
  .page { position:relative; margin:12px auto; background:#fff;
          box-shadow:0 2px 12px var(--page-shadow); border-radius:2px; }
  .page canvas { display:block; border-radius:2px; }
  /* internal \ref / \cite / \eqref targets, sitting above the text layer so a click
     navigates instead of syncing to source. Invisible until hovered - hyperref already
     colours the words underneath. */
  .linkLayer { position:absolute; inset:0; overflow:hidden; }
  .linkLayer a { position:absolute; display:block; border-radius:2px; cursor:pointer; }
  .linkLayer a:hover { background:var(--reflink); outline:1px solid var(--reflink-line); }
  .textLayer { position:absolute; inset:0; overflow:hidden; line-height:1; }
  .textLayer span, .textLayer br { color:transparent; position:absolute; white-space:pre;
                                   cursor:text; transform-origin:0% 0%; }
  .textLayer ::selection { background:var(--sel); }
  .textLayer mark { color:transparent; background:var(--hl);
                    border-bottom:2px solid var(--hl-line); cursor:pointer; }
  .textLayer mark.resolvedmark { background:var(--ok-soft); border-bottom-color:var(--ok-line); }
  @keyframes markpulse { 50% { background:var(--hl-pulse); } }
  .textLayer mark.flash { animation:markpulse .55s ease-in-out 3; }
  .syncflash { position:absolute; background:var(--hl); border:1px solid var(--hl-line);
               border-radius:3px; pointer-events:none; z-index:3;
               animation:markpulse .55s ease-in-out 3; }
  #errlog { display:none; max-height:38%; overflow:auto; border-top:2px solid var(--err);
            background:var(--err-bg); position:relative; }
  #errlog pre { margin:0; padding:10px 12px; font-size:12px; white-space:pre-wrap; color:var(--text); }
  #errClose { position:absolute; top:4px; right:8px; border:0; background:none;
              cursor:pointer; font-size:14px; color:var(--err); }
  #panel { border-left:1px solid var(--line); overflow-y:auto; padding:12px; font-size:13px;
           background:var(--bg-alt); }
  #panelHead { display:flex; align-items:center; justify-content:space-between;
               font-weight:600; margin-bottom:10px; }
  #panelHead button { border:1px solid var(--line); background:var(--surface); color:var(--text);
                      border-radius:6px; padding:4px 11px; cursor:pointer; font:13px inherit; }
  #panelHead button:hover { border-color:var(--accent); color:var(--accent); }
  .card { border:1px solid var(--line); border-radius:8px; padding:9px 11px; margin-bottom:9px;
          background:var(--surface); }
  .card.resolved { opacity:.6; }
  .card .q { color:var(--muted); font-style:italic; display:block; margin-bottom:5px;
             white-space:nowrap; overflow:hidden; text-overflow:ellipsis; cursor:pointer; }
  .card .q:hover { text-decoration:underline; }
  .card .loc { color:var(--accent); font-size:11px; display:block; margin-bottom:3px;
               font-family:ui-monospace,Menlo,monospace; }
  .card .orphan { color:var(--warn); font-size:11px; font-weight:600; }
  .card .reply { color:var(--ok); font-style:italic; margin-top:5px; }
  .card .editbox { width:100%; height:56px; font:inherit; border:1px solid var(--accent);
                   border-radius:5px; padding:5px; margin-top:2px;
                   background:var(--bg); color:var(--text); }
  details.resolvedlist { margin-top:12px; }
  details.resolvedlist summary { cursor:pointer; color:var(--muted); font-weight:600;
                                 font-size:12px; margin-bottom:8px; user-select:none; }
  .card .meta { color:var(--faint); font-size:11px; margin-top:5px; display:flex; gap:8px;
                flex-wrap:wrap; }
  .card .meta button { border:0; background:none; color:var(--accent); cursor:pointer;
                       padding:0; font-size:11px; }
  #pop { position:fixed; display:none; background:var(--surface); border:1px solid var(--line);
         border-radius:8px; box-shadow:0 8px 26px var(--page-shadow); padding:9px;
         width:280px; z-index:10; }
  #pop textarea { width:100%; height:64px; font:inherit; border:1px solid var(--line);
                  border-radius:5px; padding:6px; background:var(--bg); color:var(--text); }
  #pop button { margin-top:6px; border:0; background:var(--accent); color:var(--on-accent);
                border-radius:5px; padding:5px 12px; cursor:pointer; font:inherit; font-weight:600; }
  #toast { position:fixed; bottom:18px; left:50%; transform:translateX(-50%);
           background:var(--text); color:var(--bg); border-radius:7px; padding:8px 16px;
           display:none; font-size:13px; z-index:20; box-shadow:0 6px 20px var(--page-shadow); }
  .fontctl { display:inline-flex; gap:3px; }
  .fontctl button { border:1px solid var(--line); background:var(--surface); border-radius:5px;
                    padding:1px 7px; cursor:pointer; font-size:11px; color:var(--muted); }
  .fontctl button:hover { border-color:var(--accent); color:var(--accent); }
  #themeBtn { border:1px solid var(--line); background:var(--surface); color:var(--muted);
              border-radius:6px; padding:3px 8px; cursor:pointer; font-size:13px; }
  #themeBtn:hover { border-color:var(--accent); color:var(--accent); }
  #panelToggle.off { opacity:.4; }
  .empty { color:var(--faint); }
</style></head><body>
<div id="app">
  <nav id="side"><div id="sidetabs"><button id="tabFiles" class="on" title="Files in this repo">Files</button><button id="tabOutline" title="Sections, in reading order">Outline</button></div><div id="sidebody"></div></nav>
  <section id="srcpane">
    <div class="bar" id="bar" style="visibility:hidden">
      <span class="path" id="path"></span>
      <span class="fontctl"><button data-f="editor" data-d="-1" title="Smaller editor text">A−</button><button data-f="editor" data-d="1" title="Larger editor text">A+</button></span>
      <button id="findBtn" title="Find in this file (⌘F)">Find</button>
      <button id="saveBtn">Save</button>
      <button id="revealBtn" title="Highlight this cursor line in the PDF (SyncTeX)">Reveal →</button>
    </div>
    <div id="findbar">
      <input id="findInput" type="text" placeholder="Find in file…" spellcheck="false">
      <span id="findCount"></span>
      <button id="findPrev" title="Previous (⇧⏎)">↑</button>
      <button id="findNext" title="Next (⏎)">↓</button>
      <button id="findClose" title="Close (Esc)">✕</button>
    </div>
    <div id="edarea">
      <div id="gutterbg"></div>
      <div id="mirror" aria-hidden="true"></div>
      <textarea id="editor" spellcheck="false" placeholder="Loading LaTeX sources..."></textarea>
    </div>
  </section>
  <div id="gutter" title="drag to resize; double-click to reset"></div>
  <section id="pdfpane">
    <div class="bar">
      <span class="path" id="mainName"></span>
      <span id="status"></span>
      <button id="pdfBack" title="Back to where you were before the last link jump" disabled>↩</button>
      <button id="zOut" title="Zoom out">−</button>
      <button id="zIn" title="Zoom in">+</button>
      <button id="zFit" title="Fit width">Fit</button>
      <button id="compileBtn" title="Run latexmk -pdf -synctex=1">Recompile</button>
      <label id="autoWrap" title="Recompile automatically after every save"><input type="checkbox" id="autoChk"> auto</label>
      <button id="themeBtn" title="Light / dark theme">◐</button>
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
<div id="pop"><textarea id="popText" placeholder="Comment on the selection..."></textarea><br>
  <button id="popAdd">Add comment</button></div>
<div id="toast"></div>
<script src="https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.min.js"></script>
<script>
const $ = id => document.getElementById(id);
const WORKER_URL = "https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js";

/* ---------- theme: follow the OS until you pick one ---------- */
const prefersDark = () => matchMedia("(prefers-color-scheme: dark)").matches;
function applyTheme() {
  const saved = localStorage.getItem("texreview.theme");
  const dark = saved ? saved === "dark" : prefersDark();
  document.documentElement.dataset.theme = dark ? "dark" : "light";
  const b = document.getElementById("themeBtn");
  if (b) b.textContent = dark ? "☾" : "☀";
}
applyTheme();
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
  if (!localStorage.getItem("texreview.theme")) applyTheme();
});
let state = null;          // {path, mtime} - the open source file
let mainRel = "";
let pdfDoc = null, pdfScale = 1, zoomFactor = 1, loadedMtime = 0, renderToken = 0;
let pageEls = [];          // .page divs, index = page-1
let comments = [];
let pending = null;        // captured selection awaiting comment text
let lastSel = null;        // last PDF selection; survives the focus steal on right-click
let lastSrcSel = null;     // same, for a selection in the LaTeX editor
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
let sideMode = localStorage.getItem("texreview.sideMode") || "files";
let outlineData = [];
function renderSidebar() {
  const body = $("sidebody");
  $("tabFiles").classList.toggle("on", sideMode === "files");
  $("tabOutline").classList.toggle("on", sideMode === "outline");
  body.innerHTML = "";
  if (sideMode === "outline") { renderOutline(body); return; }
  const tree = {};
  for (const f of allFiles) {
    const parts = f.split("/"); let node = tree;
    for (const p of parts.slice(0, -1)) node = (node[p + "/"] ??= {});
    node[parts.at(-1)] = f;
  }
  renderTree(tree, body, 0, "");
}
function setSideMode(m) {
  sideMode = m;
  localStorage.setItem("texreview.sideMode", m);
  if (m === "outline" && !outlineData.length) loadOutline(); else renderSidebar();
}
$("tabFiles").onclick = () => setSideMode("files");
$("tabOutline").onclick = () => setSideMode("outline");
async function loadOutline() {
  try {
    const r = await api("/api/outline");
    if (r.ok) outlineData = await r.json();
  } catch (e) { /* an outline is a convenience; never block the editor on it */ }
  renderSidebar();
}
function renderOutline(body) {
  if (!outlineData.length) {
    const p = document.createElement("p");
    p.className = "empty";
    p.textContent = "No \\section commands found in the main file.";
    body.appendChild(p);
    return;
  }
  const top = Math.min(...outlineData.map(e => e.level));
  for (const e of outlineData) {
    const b = document.createElement("button");
    b.className = "sec l" + e.level;
    b.textContent = e.title;
    b.title = e.file + ":" + e.line;
    b.style.paddingLeft = ((e.level - top) * 11 + 6) + "px";
    b.classList.toggle("here", !!state && state.path === e.file && e.line === activeSecLine);
    b.onclick = () => gotoSection(e);
    body.appendChild(b);
  }
}
let activeSecLine = -1;
// the point of the outline is landing in BOTH panes: the source jump is local, the
// PDF jump needs SyncTeX, and a paper that has not compiled yet still gets the source
async function gotoSection(e) {
  activeSecLine = e.line;
  await gotoSource(e.file, e.line);
  renderSidebar();
  try {
    const r = await api("/api/sync/view", {file: e.file, line: e.line});
    if (r.ok) { const {page, h, v, W, H} = await r.json(); flashPdfBox(page, h, v, W, H); }
  } catch (err) { /* no synctex yet - the source pane already moved */ }
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
  lastSrcSel = null;              // a selection belongs to the file it was made in
  $("editor").value = d.content;
  findHits = []; findAt = -1; $("findCount").textContent = "";   // offsets were the old file's
  braceHi = null;                 // ditto - these are offsets into the file we just closed
  queueMirror();
  setDirty(false);
  $("bar").style.visibility = "visible";
  $("path").textContent = path;
  // a file opened by a PDF click may live in a folded folder: reveal it so the
  // active highlight is not hidden
  const parts = path.split("/");
  for (let i = 1; i < parts.length; i++) collapsed.delete(parts.slice(0, i).join("/") + "/");
  renderSidebar();
}
$("editor").addEventListener("input", () => { syncBrace(); queueMirror(); if (state) setDirty(true); });
// caret moves (arrows, click, drag) do not fire `input`; selectionchange covers all of them
document.addEventListener("selectionchange", () => {
  if (document.activeElement === $("editor")) syncBrace();
});
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
  if (autoCompile) { toast("Saved - compiling…"); startCompile(); }
  else toast("Saved - Recompile to update the PDF");
}
$("saveBtn").onclick = () => save(false);

/* ---------- find in file ---------- */
let findHits = [], findAt = -1;
function openFind() {
  $("findbar").style.display = "flex";
  const sel = $("editor").value.slice($("editor").selectionStart, $("editor").selectionEnd);
  if (sel && !sel.includes("\n")) $("findInput").value = sel;
  $("findInput").select();
  $("findInput").focus();
  runFind();
}
function closeFind() {
  $("findbar").style.display = "none";
  findHits = []; findAt = -1;
  queueMirror();
  $("editor").focus();
}
function runFind() {
  const q = $("findInput").value;
  findHits = [];
  if (q) {
    const hay = $("editor").value.toLowerCase(), needle = q.toLowerCase();
    let i = hay.indexOf(needle);
    while (i >= 0) { findHits.push(i); i = hay.indexOf(needle, i + Math.max(1, needle.length)); }
  }
  // jump to the first hit at or after the cursor
  const cur = $("editor").selectionStart;
  findAt = findHits.findIndex(i => i >= cur);
  if (findAt < 0) findAt = findHits.length ? 0 : -1;
  showFind();
}
function showFind() {
  const q = $("findInput").value;
  $("findCount").textContent = !q ? "" : findHits.length ? `${findAt + 1}/${findHits.length}` : "0/0";
  queueMirror();
  if (findAt < 0) return;
  placeCursor(findHits[findAt], findHits[findAt] + q.length);
  $("findInput").focus();   // keep typing; the textarea keeps its selection
}
function stepFind(d) {
  if (!findHits.length) return;
  findAt = (findAt + d + findHits.length) % findHits.length;
  showFind();
}
$("findBtn").onclick = openFind;
$("findClose").onclick = closeFind;
$("findNext").onclick = () => stepFind(1);
$("findPrev").onclick = () => stepFind(-1);
$("findInput").addEventListener("input", runFind);
$("findInput").addEventListener("keydown", ev => {
  if (ev.key === "Enter") { ev.preventDefault(); stepFind(ev.shiftKey ? -1 : 1); }
  else if (ev.key === "Escape") { ev.preventDefault(); closeFind(); }
});

/* ---------- mirror: line numbers + find highlights ---------- */
function esc(s) { return s.replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }
// One class letter per character: c comment, k command, m math, b brace, e env/ref
// name. Line-at-a-time, so a display-math block spanning lines is simply not tinted -
// acceptable for a highlighter that must never disagree with the textarea's layout.
const REF_CMD = /^(begin|end|cite[a-z]*|ref|autoref|eqref|cref|Cref|label|input|include|usepackage|documentclass|bibliography[a-z]*)$/;
function texScan(line) {
  const n = line.length, out = new Array(n).fill(" ");
  let i = 0, math = false;
  while (i < n) {
    const ch = line[i];
    if (ch === "%") { for (let j = i; j < n; j++) out[j] = "c"; return out; }
    if (ch === "\\") {
      const name = (/^[a-zA-Z@]+\*?/.exec(line.slice(i + 1)) || [""])[0];
      if (!name) { out[i] = "k"; if (i + 1 < n) out[i + 1] = "k"; i += 2; continue; }
      for (let j = 0; j <= name.length; j++) out[i + j] = "k";
      i += 1 + name.length;
      if (REF_CMD.test(name.replace("*", ""))) {   // tint the {argument} that names a thing
        let j = i;
        while (j < n && line[j] === " ") j++;
        if (line[j] === "[") { const c = line.indexOf("]", j); j = c < 0 ? n : c + 1; }
        while (j < n && line[j] === " ") j++;
        if (line[j] === "{") {
          const close = line.indexOf("}", j), end = close < 0 ? n : close;
          out[j] = "b";
          for (let k = j + 1; k < end; k++) out[k] = "e";
          if (close >= 0) out[close] = "b";
          i = close < 0 ? n : close + 1;
        }
      }
      continue;
    }
    if (ch === "$") { math = !math; out[i] = "m"; i++; continue; }
    if (math) { out[i] = "m"; i++; continue; }
    if (ch === "{" || ch === "}" || ch === "[" || ch === "]") out[i] = "b";
    i++;
  }
  return out;
}
/* Bracket matching. A bracket only delimits when it is neither escaped (\{ is a literal)
   nor inside a comment, so both tests gate every candidate. The scan walks the whole
   document, which is cheap next to the repaint it feeds, and only ever inspects bracket
   characters - inComment's walk back to the line start is paid per bracket, not per char. */
const OPENB = { "{": "}", "[": "]" }, CLOSEB = { "}": "{", "]": "[" };
function escapedAt(t, i) {
  let b = 0;
  for (let j = i - 1; j >= 0 && t[j] === "\\"; j--) b++;
  return b % 2 === 1;   // \{ is literal, \\{ is a delimiter after an escaped backslash
}
function inComment(t, i) {
  for (let j = i - 1; j >= 0 && t[j] !== "\n"; j--)
    if (t[j] === "%" && !escapedAt(t, j)) return true;
  return false;
}
// -> [from, to, matched] or null. Checks the character after the caret, then before it.
function matchBrace(t, caret) {
  for (const p of [caret, caret - 1]) {
    const ch = t[p];
    if (!ch || (!OPENB[ch] && !CLOSEB[ch])) continue;
    if (escapedAt(t, p) || inComment(t, p)) continue;
    const fwd = !!OPENB[ch], want = fwd ? OPENB[ch] : CLOSEB[ch];
    let depth = 0;
    for (let i = p; fwd ? i < t.length : i >= 0; i += fwd ? 1 : -1) {
      if (t[i] !== ch && t[i] !== want) continue;
      if (escapedAt(t, i) || inComment(t, i)) continue;
      depth += t[i] === ch ? 1 : -1;
      if (!depth) return [Math.min(p, i), Math.max(p, i), true];
    }
    // an unbalanced brace is a compile error worth flagging; an unbalanced [ is ordinary prose
    return (ch === "{" || ch === "}") ? [p, p, false] : null;
  }
  return null;
}
let braceHi = null;
function syncBrace() {
  const ed = $("editor");
  // with a selection the textarea paints its own highlight over the same glyphs
  const m = ed.selectionStart === ed.selectionEnd ? matchBrace(ed.value, ed.selectionStart) : null;
  const same = (!m && !braceHi) ||
    (m && braceHi && m[0] === braceHi[0] && m[1] === braceHi[1] && m[2] === braceHi[2]);
  if (same) return;   // most caret moves change nothing, so most cost no repaint
  braceHi = m;
  queueMirror();
}
function renderLine(line, base, q, cur) {
  const n = line.length;
  if (!n) return "";
  const cls = texScan(line);
  let ba = -1, bb = -1, bok = true;
  if (braceHi) {
    bok = braceHi[2];
    if (braceHi[0] >= base && braceHi[0] < base + n) ba = braceHi[0] - base;
    if (braceHi[1] >= base && braceHi[1] < base + n) bb = braceHi[1] - base;
  }
  // 0 = no hit, otherwise the hit's 1-based index so two adjacent hits stay distinct
  let mk = null, curIdx = -1;
  if (q) {
    mk = new Array(n).fill(0);
    const hay = line.toLowerCase(), needle = q.toLowerCase();
    let i = hay.indexOf(needle), h = 0;
    while (i >= 0) {
      h++;
      for (let j = i; j < i + q.length && j < n; j++) mk[j] = h;
      if (base + i === cur) curIdx = h;
      i = hay.indexOf(needle, i + q.length);
    }
  }
  let out = "", j = 0;
  while (j < n) {
    const m = mk ? mk[j] : 0;
    let k = j + 1;
    if (m) {   // a hit wins over syntax colour, so each hit stays one <mark>
      while (k < n && mk[k] === m) k++;
      out += "<mark" + (m === curIdx ? ' class="cur"' : "") + ">" + esc(line.slice(j, k)) + "</mark>";
    } else if (j === ba || j === bb) {   // one character, so it never joins a run
      out += '<span class="bm' + (bok ? "" : " bad") + '">' + esc(line[j]) + "</span>";
    } else {
      const c = cls[j];
      while (k < n && !(mk && mk[k]) && k !== ba && k !== bb && cls[k] === c) k++;
      const txt = esc(line.slice(j, k));
      out += c === " " ? txt : '<span class="t' + c + '">' + txt + "</span>";
    }
    j = k;
  }
  return out;
}
let mirrorQueued = false;
function paintMirror() {
  mirrorQueued = false;
  const ed = $("editor");
  // a write that bypasses syncBrace (replaceRange, a reload) can leave these offsets
  // pointing at characters that are no longer brackets - drop them rather than paint a lie
  if (braceHi && !(/[{}[\]]/.test(ed.value[braceHi[0]] || "") && /[{}[\]]/.test(ed.value[braceHi[1]] || "")))
    braceHi = null;
  const q = $("findbar").style.display === "flex" ? $("findInput").value : "";
  const cur = findAt >= 0 ? findHits[findAt] : -1;
  const lines = ed.value.split("\n");
  let pos = 0, out = "";
  for (let i = 0; i < lines.length; i++) {
    const inner = renderLine(lines[i], pos, q, cur);
    // an empty row would collapse to zero height; the textarea keeps one line
    out += '<div class="row" data-n="' + (i + 1) + '">' + (inner || "&#8203;") + "</div>";
    pos += lines[i].length + 1;
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

/* ---------- comment toggle (⌘/) ---------- */
/* ---------- wrap the selection in a LaTeX command (Overleaf-style) ---------- */
// setRangeText does NOT push an undo entry in Chrome, so ⌘Z would not reverse these.
// execCommand("insertText") is deprecated but is the only mutation the textarea's own
// undo stack records - it also fires `input`, which repaints the mirror and marks dirty.
function replaceRange(el, from, to, text) {
  el.focus();
  el.setSelectionRange(from, to);
  if (!document.execCommand("insertText", false, text)) {
    el.setRangeText(text, from, to, "end");            // fallback: correct, but not undoable
    el.dispatchEvent(new Event("input", {bubbles: true}));
  }
}
function wrapCmd(cmd) {
  const ed = $("editor"), v = ed.value, open = "\\" + cmd + "{";
  let a = ed.selectionStart, b = ed.selectionEnd;
  // a double-click usually grabs the trailing space; \textbf{word } puts it inside the group
  while (a < b && /\s/.test(v[a])) a++;
  while (b > a && /\s/.test(v[b - 1])) b--;
  const sel = v.slice(a, b);
  let from, to, text, caret;
  if (sel.startsWith(open) && sel.endsWith("}")) {          // the selection is the whole call
    from = a; to = b; text = sel.slice(open.length, -1); caret = [from, from + text.length];
  } else if (v.slice(a - open.length, a) === open && v[b] === "}") {   // wrapped just outside
    from = a - open.length; to = b + 1; text = sel; caret = [from, from + text.length];
  } else {                                                  // wrap, or insert an empty call
    from = a; to = b; text = open + sel + "}";
    caret = [a + open.length, a + open.length + sel.length];
  }
  replaceRange(ed, from, to, text);
  ed.setSelectionRange(caret[0], caret[1]);
}

function toggleComment() {
  const ed = $("editor"), v = ed.value;
  const selStart = ed.selectionStart, selEnd = ed.selectionEnd;
  const from = v.lastIndexOf("\n", selStart - 1) + 1;
  let to = v.indexOf("\n", selEnd);
  if (to < 0) to = v.length;
  const lines = v.slice(from, to).split("\n");
  const commented = lines.every(l => !l.trim() || /^\s*%/.test(l));
  const out = lines.map(l => {
    if (!l.trim()) return l;
    if (commented) return l.replace(/^(\s*)%\s?/, "$1");
    const indent = l.match(/^\s*/)[0];
    return indent + "% " + l.slice(indent.length);
  }).join("\n");
  replaceRange(ed, from, to, out);
  ed.setSelectionRange(from, from + out.length);
}

addEventListener("beforeunload", ev => {
  if (dirty) { ev.preventDefault(); ev.returnValue = ""; }   // same guard as switching files
});
// macOS reports ev.key as the UNSHIFTED character while Cmd is held, so a bare
// `ev.key === "s"` also matches Cmd+Shift+S and Cmd+Alt+S - and preventDefault() then
// swallows the browser's own shortcut. Require the plain chord for letter keys.
const chord = (ev, k) => (ev.metaKey || ev.ctrlKey) && !ev.shiftKey && !ev.altKey
                         && (ev.key || "").toLowerCase() === k;
document.addEventListener("keydown", ev => {
  if (chord(ev, "s")) { ev.preventDefault(); save(false); }
  if (chord(ev, "f") && state) { ev.preventDefault(); openFind(); }
  if (chord(ev, "b") && document.activeElement === $("editor")) {
    ev.preventDefault(); wrapCmd("textbf");
  }
  if (chord(ev, "i") && document.activeElement === $("editor")) {
    ev.preventDefault(); wrapCmd("textit");
  }
  // "/" is a shifted key on several layouts, so only Alt is disqualifying here
  if ((ev.metaKey || ev.ctrlKey) && !ev.altKey && ev.key === "/"
      && document.activeElement === $("editor")) {
    ev.preventDefault(); toggleComment();
  }
  if (ev.key === "Escape" && $("findbar").style.display === "flex") closeFind();
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
  $("mirror").scrollTop = ed.scrollTop;
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
  lastSel = null;                 // page coordinates do not survive a re-layout
  renderToken++;                  // strand any in-flight render before the doc goes away
  const prevDoc = pdfDoc; pdfDoc = null;
  try { await prevDoc?.destroy(); } catch (e) {}   // else every reload leaks a pdf.js worker
  pdfDoc = await pdfjsLib.getDocument("/api/pdf?ts=" + info.mtime).promise;
  await renderAllPages();
  applyPdfHighlights();
}
/* Where the reader is, as a page plus how far into it. A recompile usually shifts
   content, so this survives far better than a fraction of total scroll height. */
function viewAnchor() {
  const w = $("pdfwrap"), top = w.scrollTop;
  // vertically you read top-down, so hold the top of the view; horizontally you want
  // the middle to stay put, which is what zooming past the pane width disturbs
  const xmid = w.scrollWidth > w.clientWidth
    ? (w.scrollLeft + w.clientWidth / 2) / w.scrollWidth : 0.5;
  for (let i = 0; i < pageEls.length; i++) {
    const pd = pageEls[i];
    if (pd.offsetTop + pd.offsetHeight > top)
      return {page: i + 1, into: (top - pd.offsetTop) / (pd.offsetHeight || 1), xmid};
  }
  return null;
}
function gotoAnchor(a) {
  if (!a || !pageEls.length) return;
  const w = $("pdfwrap");
  const pd = pageEls[Math.min(a.page, pageEls.length) - 1];
  w.scrollTop = Math.max(0, pd.offsetTop + a.into * pd.offsetHeight);
  w.scrollLeft = Math.max(0, a.xmid * w.scrollWidth - w.clientWidth / 2);
}
// draw the page being read first, then outward, so a recompile shows your place
// immediately instead of after every earlier page has rasterized
function drawOrder(from) {
  const order = [];
  for (let d = 0; d < pageEls.length; d++) {
    if (from + d < pageEls.length) order.push(from + d);
    if (d && from - d >= 0) order.push(from - d);
  }
  return order;
}
async function renderAllPages() {
  const my = ++renderToken;
  const wrap = $("pdfwrap"), pages = $("pages");
  const anchor = viewAnchor();
  pages.innerHTML = ""; pageEls = [];
  const first = await pdfDoc.getPage(1);
  const base = (wrap.clientWidth - 36) / first.getViewport({scale: 1}).width;
  pdfScale = Math.max(0.35, Math.min(5, base * zoomFactor));
  const dpr = window.devicePixelRatio || 1;
  // 1. lay every page out at its true size before drawing anything, so the scrollbar
  //    is correct and the view is restored up front rather than after the last page
  const vps = [];
  for (let n = 1; n <= pdfDoc.numPages; n++) {
    if (my !== renderToken) return;
    const page = await pdfDoc.getPage(n);
    const vp = page.getViewport({scale: pdfScale});
    vps.push({page, vp});
    const pd = document.createElement("div");
    pd.className = "page"; pd.dataset.page = n;
    pd.style.width = vp.width + "px"; pd.style.height = vp.height + "px";
    pd.style.setProperty("--scale-factor", vp.scale);
    const canvas = document.createElement("canvas");
    canvas.width = Math.floor(vp.width * dpr); canvas.height = Math.floor(vp.height * dpr);
    canvas.style.width = vp.width + "px"; canvas.style.height = vp.height + "px";
    const tl = document.createElement("div"); tl.className = "textLayer";
    const ll = document.createElement("div"); ll.className = "linkLayer";
    pd.append(canvas, tl, ll);
    pages.appendChild(pd); pageEls.push(pd);
  }
  gotoAnchor(anchor);
  // 2. rasterize, nearest to the viewport first
  for (const i of drawOrder(anchor ? Math.min(anchor.page, pageEls.length) - 1 : 0)) {
    if (my !== renderToken) return;
    const {page, vp} = vps[i];
    const pd = pageEls[i];
    await page.render({canvasContext: pd.querySelector("canvas").getContext("2d"),
                       viewport: vp,
                       transform: dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : null}).promise;
    const tc = await page.getTextContent();
    await pdfjsLib.renderTextLayer({textContentSource: tc, textContent: tc,
                                    container: pd.querySelector(".textLayer"),
                                    viewport: vp, textDivs: []}).promise;
    await paintLinks(page, vp, pd.querySelector(".linkLayer"));
  }
}
/* ---------- internal PDF links (\ref, \cite, \eqref via hyperref) ---------- */
// hyperref emits a GoTo annotation per cross-reference. External URLs are left alone:
// an inert-looking anchor is worse than none, and clicking through belongs elsewhere.
async function paintLinks(page, vp, layer) {
  layer.textContent = "";
  let annots;
  try { annots = await page.getAnnotations({intent: "display"}); } catch (e) { return; }
  for (const a of annots) {
    if (a.subtype !== "Link" || !a.dest) continue;
    const r = vp.convertToViewportRectangle(a.rect);
    const el = document.createElement("a");
    el.style.left = Math.min(r[0], r[2]) + "px";
    el.style.top = Math.min(r[1], r[3]) + "px";
    el.style.width = Math.abs(r[2] - r[0]) + "px";
    el.style.height = Math.abs(r[3] - r[1]) + "px";
    el.title = "Go to reference";
    el.addEventListener("click", ev => {
      ev.preventDefault(); ev.stopPropagation();
      // a drag that ended on a link is a text selection, not a click on it
      if (!String(window.getSelection() || "")) followDest(a.dest);
    });
    layer.appendChild(el);
  }
}
let pdfBackStack = [];
function pushBack() {
  pdfBackStack.push(viewAnchor());
  if (pdfBackStack.length > 50) pdfBackStack.shift();
  $("pdfBack").disabled = false;
}
async function followDest(dest) {
  try {
    const d = typeof dest === "string" ? await pdfDoc.getDestination(dest) : dest;
    if (!Array.isArray(d) || !d.length) return;
    const idx = await pdfDoc.getPageIndex(d[0]);
    const pd = pageEls[idx];
    if (!pd) return;
    pushBack();
    // An /XYZ destination carries the target's top edge in PDF user space, measured
    // from the page bottom; anything else (/Fit, /FitH) just means the page top.
    let into = 0;
    const page = await pdfDoc.getPage(idx + 1);
    const y = d[3];
    if (d[1] && d[1].name === "XYZ" && typeof y === "number") {
      const h = page.getViewport({scale: 1}).height;
      into = Math.min(0.92, Math.max(0, (h - y) / h));
    }
    const w = $("pdfwrap");
    // leave a little headroom so the target is not flush against the pane's top edge
    w.scrollTop = Math.max(0, pd.offsetTop + into * pd.offsetHeight - 12);
    flashPage(pd, into);
  } catch (e) { /* a malformed destination is not worth interrupting the user over */ }
}
function flashPage(pd, into) {
  const box = document.createElement("div");
  box.className = "syncflash";
  box.style.left = "0"; box.style.width = "100%";
  box.style.top = Math.max(0, into * pd.offsetHeight - 6) + "px";
  box.style.height = "2.2em";
  pd.appendChild(box);
  setTimeout(() => box.remove(), 1400);
}
$("pdfBack").onclick = () => {
  const a = pdfBackStack.pop();
  if (a) gotoAnchor(a);
  $("pdfBack").disabled = !pdfBackStack.length;
};
$("zIn").onclick = () => setZoom(zoomFactor * 1.15);
$("zOut").onclick = () => setZoom(zoomFactor / 1.15);
$("zFit").onclick = () => setZoom(1);
async function rezoom() {
  if (!pdfDoc) return;
  await renderAllPages();
  applyPdfHighlights();
}
/* pinch on a trackpad arrives as wheel + ctrlKey; preview with a CSS scale for
   instant feedback, then re-render once the gesture settles so text stays sharp */
let renderedZoom = 1, zoomTimer = null;
function setZoom(z) {
  const wrap = $("pdfwrap");
  zoomFactor = Math.min(6, Math.max(0.25, z));
  // anchor the scale at the top of what you are looking at, so zooming in does not
  // shove the current page out of view; scrollTop is fixed for the whole gesture
  // because the wheel handler preventDefaults, so the origin never jumps mid-pinch
  $("pages").style.transformOrigin =
    `${wrap.scrollLeft + wrap.clientWidth / 2}px ${wrap.scrollTop}px`;
  $("pages").style.transform = `scale(${zoomFactor / renderedZoom})`;
  $("status").textContent = Math.round(zoomFactor * 100) + "%";
  clearTimeout(zoomTimer);
  zoomTimer = setTimeout(async () => {
    $("pages").style.transform = "";
    renderedZoom = zoomFactor;
    await rezoom();   // renderAllPages re-anchors the view by page, at the new scale
    if (!compiling) $("status").textContent = "";
  }, 180);
}
$("pdfwrap").addEventListener("wheel", ev => {
  if (!ev.ctrlKey && !ev.metaKey) return;      // plain scrolling stays scrolling
  ev.preventDefault();
  // a pinch's deltaY is proportional to how far you pinched. A fixed step per event
  // ignored that, so a quick pinch fired dozens of events and slammed into the clamp.
  // The clamp keeps one notch of a discrete mouse wheel from jumping too far.
  const d = Math.max(-50, Math.min(50, ev.deltaY));
  setZoom(zoomFactor * Math.exp(-d * 0.01));
}, {passive: false});

/* ---------- compile ---------- */
function setCompiling(on) {
  compiling = on;
  $("compileBtn").disabled = on;
  $("status").textContent = on ? "compiling…" : "";
}
let autoCompile = localStorage.getItem("texreview.autocompile") !== "off";
let compileQueued = false;
$("autoChk").checked = autoCompile;
$("autoChk").onchange = () => {
  autoCompile = $("autoChk").checked;
  localStorage.setItem("texreview.autocompile", autoCompile ? "on" : "off");
};
async function startCompile() {
  // a save landing mid-compile queues exactly one more run, so rapid saves
  // collapse into a single follow-up instead of stacking or erroring
  if (compiling) { compileQueued = true; return; }
  const r = await api("/api/compile", {});
  if (!r.ok) { toast((await r.json()).error); return; }
  setCompiling(true);
  pollCompile();
}
$("compileBtn").onclick = startCompile;
async function pollCompile() {
  const s = await (await api("/api/compile")).json();
  if (s.running) { setTimeout(pollCompile, 700); return; }
  setCompiling(false);
  if (s.ok) { $("errlog").style.display = "none"; toast("Compiled ✓"); loadPdf(); loadOutline(); }
  else {
    $("errpre").textContent = s.log || "compile failed (no log)";
    $("errlog").style.display = "block";
    toast("Compile failed");
  }
  if (compileQueued) { compileQueued = false; startCompile(); }
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
/* A selection in the LaTeX editor. file and line are known outright here, so this skips
   the SyncTeX lookup the PDF path needs and resolves the page on the way out instead. */
function captureSourceSelection() {
  const ed = $("editor");
  if (!state) return null;
  const a = ed.selectionStart, b = ed.selectionEnd;
  if (a === b) return null;
  const v = ed.value, quote = v.slice(a, b);
  if (!quote.trim()) return null;
  lastSrcSel = {
    origin: "source", file: state.path, line: v.slice(0, a).split("\n").length, quote,
    prefix: v.slice(Math.max(0, a - 30), a),
    suffix: v.slice(b, b + 30),
  };
  return lastSrcSel;
}
$("editor").addEventListener("select", captureSourceSelection);
function openCommentPopover(x, y, cap) {
  cap = cap || capturePdfSelection() || lastSel;
  if (!cap) return false;
  pending = cap.origin ? cap : {...cap, origin: "pdf"};
  const pop = $("pop");
  pop.style.display = "block";
  pop.style.left = Math.min(x, innerWidth - 300) + "px";
  pop.style.top = (y + 8) + "px";
  $("popText").value = ""; $("popText").focus();
  return true;
}
// Selecting text no longer pops the comment box open by itself - it got in the way of
// simply reading and re-selecting. Right-click on the selection to comment, in either pane.
$("pdfwrap").addEventListener("mouseup", ev => {
  if (ev.button !== 0) return;
  setTimeout(() => {
    const sel = window.getSelection();
    if (!sel.rangeCount || sel.isCollapsed) $("pop").style.display = "none";
  }, 0);
});
$("pdfwrap").addEventListener("contextmenu", ev => {
  if (openCommentPopover(ev.clientX, ev.clientY)) ev.preventDefault();
});
$("editor").addEventListener("contextmenu", ev => {
  // the fallback exists only to survive the focus steal of the right-click itself, so it
  // must still belong to the file on screen - otherwise a right-click with nothing selected
  // would file the comment against whatever was last selected in some other file
  const stale = !lastSrcSel || !state || lastSrcSel.file !== state.path;
  const cap = captureSourceSelection() || (stale ? null : lastSrcSel);
  if (cap && openCommentPopover(ev.clientX, ev.clientY, cap)) ev.preventDefault();
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
    text: textNearPoint(ev.clientX, ev.clientY),
  });
  if (!r.ok) { toast((await r.json()).error); return; }
  const {file, line} = await r.json();
  gotoSource(file, line);
});
function textNearPoint(x, y) {
  // the words under the cursor, used to locate the source when SyncTeX only
  // knows the structural line (e.g. an abstract typeset inside \maketitle)
  let node = null;
  if (document.caretRangeFromPoint) {
    const r = document.caretRangeFromPoint(x, y);
    if (r) node = r.startContainer;
  } else if (document.caretPositionFromPoint) {
    const p = document.caretPositionFromPoint(x, y);
    if (p) node = p.offsetNode;
  }
  let span = node && node.nodeType === 3 ? node.parentElement : null;
  if (!span || !span.closest(".textLayer")) return "";
  let out = span.textContent || "";
  for (let s = span.nextElementSibling; s && out.length < 120; s = s.nextElementSibling)
    out += " " + s.textContent;
  return out.slice(0, 200);
}
$("popAdd").onclick = async () => {
  const text = $("popText").value.trim();
  const p = pending;
  if (!text || !p) return;
  $("pop").style.display = "none"; pending = null;
  lastSel = lastSrcSel = null;    // spent; must not seed the next comment
  let page = p.page || 0, file = p.file ?? null, line = p.line ?? null;
  try {
    if (p.origin === "source") {
      // known file:line -> which PDF page, so the card can still jump into the paper
      const r = await api("/api/sync/view", {file: p.file, line: p.line});
      if (r.ok) page = (await r.json()).page;
    } else {
      const r = await api("/api/sync/edit", {page: p.page, x: p.x, y: p.y});
      if (r.ok) ({file, line} = await r.json());
    }
  } catch (e) {}
  await api("/api/comment/add", {page, quote: p.quote, prefix: p.prefix,
    suffix: p.suffix, file, line, comment: text, origin: p.origin});
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
  loc.textContent = [c.file ? c.file + ":" + c.line : "", c.page ? "p." + c.page : ""]
    .filter(Boolean).join(" · ");
  const q = document.createElement("span"); q.className = "q"; q.textContent = '"' + c.quote + '"';
  q.title = "Show this passage";
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
  // written against the LaTeX? show it there, even when the same words also render
  if (c.origin === "source" && c.file) { gotoSource(c.file, c.line); return; }
  const mk = document.querySelector('.textLayer mark[data-id="' + c.id + '"]');
  if (mk) {
    mk.scrollIntoView({behavior: "smooth", block: "center"});
    mk.classList.add("flash");
    setTimeout(() => mk.classList.remove("flash"), 2000);
    return;
  }
  // a comment made on the LaTeX source quotes markup that never appears in the PDF,
  // so fall back to the place it was actually written
  if (c.file) { gotoSource(c.file, c.line); return; }
  const pd = pageEls[(c.page || 1) - 1];
  if (pd) {
    $("pdfwrap").scrollTo({top: pd.offsetTop - 20, behavior: "smooth"});
    toast("Passage not found on the current PDF (recompiled since?) - showing its page");
  } else toast("Can't locate this passage anymore");
}
function renderPanel() {
  const panel = $("cards"); panel.innerHTML = "";
  if (!comments.length) {
    panel.innerHTML = '<p class="empty">No comments. Select text in the PDF or in the '
      + 'LaTeX source, then right-click it to comment.</p>';
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
$("themeBtn").onclick = () => {
  localStorage.setItem("texreview.theme",
    document.documentElement.dataset.theme === "dark" ? "light" : "dark");
  applyTheme();
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
  $("edarea").style.fontSize = fonts.editor + "px";
  $("panel").style.fontSize = fonts.panel + "px";
  queueMirror();   // a font change re-wraps every line, so the numbers move
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
/* ---------- reading position, so a reload does not send you back to page 1 ---------- */
let stateSaveTimer = null;
function rememberPosition() {
  if (!state) return;
  clearTimeout(stateSaveTimer);
  // debounced: this fires on every scroll and caret move, and the point is where you
  // came to rest, not every pixel on the way there
  stateSaveTimer = setTimeout(() => {
    const ed = $("editor");
    api("/api/state", {path: state.path, sel: ed.selectionStart, edScroll: ed.scrollTop,
                       pdf: viewAnchor()}).catch(() => {});
  }, 700);
}
$("editor").addEventListener("scroll", rememberPosition);
$("pdfwrap").addEventListener("scroll", rememberPosition);
document.addEventListener("selectionchange", () => {
  if (document.activeElement === $("editor")) rememberPosition();
});

(async function boot() {
  const info = await (await api("/api/root")).json();
  mainRel = info.main;
  await initWorker();
  await loadFiles();
  let saved = {};
  try { saved = await (await api("/api/state")).json(); } catch (e) {}
  await openDoc(saved.path && allFiles.includes(saved.path) ? saved.path : mainRel);
  if (saved.path === state?.path && typeof saved.sel === "number") {
    const ed = $("editor");
    const sel = Math.min(saved.sel, ed.value.length);   // the file may have shrunk since
    ed.setSelectionRange(sel, sel);
    ed.scrollTop = saved.edScroll || 0;
    $("mirror").scrollTop = ed.scrollTop;
    syncBrace();
  }
  comments = await (await api("/api/comments")).json();
  await loadPdf();
  // loadPdf renders from the top; put the PDF back where it was, after it has pages
  if (saved.pdf && typeof saved.pdf.page === "number") gotoAnchor(saved.pdf);
  loadOutline();
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
                                             "tool": "texreview", "build": BUILD}
        if method == "GET" and path == "/api/outline":
            return 200, "application/json", outline(root, main_rel)
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
            try:
                hit = {**synctex_edit(root, pdf, int(body["page"]),
                                      float(body["x"]), float(body["y"])), "via": "synctex"}
            except RequestError:
                hit = None
            # Fall back to the words actually selected when SyncTeX's answer is not
            # somewhere you can edit: a prose-free structural line (acmart typesets
            # \begin{abstract} during \maketitle), a generated file (the comment
            # package rewrites skipped blocks through comment.cut), or a line past the
            # end of the file it names.
            text = body.get("text") or ""
            found = find_text(root, text) if text else None
            editable = set(list_tex_files(root))
            unusable = (hit is None or hit["file"] not in editable
                        or is_structural(root, hit["file"], hit["line"])
                        # A selection dragged across columns or sections resolves from a
                        # single anchor point that can land in an unrelated file, and the
                        # comment would then carry one file's quote with another's target.
                        # Words that were actually matched outrank a point query.
                        or (found is not None and found["file"] != hit["file"]))
            if found and unusable:
                return 200, "application/json", {**found, "via": "text"}
            if hit is None:
                raise RequestError(404, "SyncTeX has no source mapping for that spot")
            if hit["file"] not in editable:
                raise RequestError(404, f"maps into a generated file ({hit['file']})")
            return 200, "application/json", hit
        if method == "POST" and path == "/api/sync/view":
            pdf = pdf_info(root, main_rel)["pdf"]
            safe_resolve(root, body["file"])
            return 200, "application/json", synctex_view(
                root, pdf, body["file"], int(body["line"]))
        if method == "GET" and path == "/api/export":
            return 200, "text/plain; charset=utf-8", export_text(root, main_rel)
        if method == "GET" and path == "/api/state":
            return 200, "application/json", load_state(root)
        if method == "POST" and path == "/api/state":
            return 200, "application/json", save_state(root, body)
        if method == "GET" and path == "/api/comments":
            return 200, "application/json", load_comments(root)
        if method == "POST" and path == "/api/comment/add":
            return 200, "application/json", add_comment(
                root, body["page"], body["quote"], body.get("prefix", ""),
                body.get("suffix", ""), body.get("file"), body.get("line"), body["comment"],
                body.get("origin", "pdf"))
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
    except OSError as e:
        return 500, "application/json", {"error": f"filesystem error: {e.strerror or e}"}


LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


def request_is_local(host: str | None, origin: str | None) -> bool:
    """Reject requests steered here by another site.

    The server binds to loopback, but any page the user browses can still POST to
    127.0.0.1 - and these tools write files (and run latexmk). Same-origin requests from our own
    page carry Host: 127.0.0.1:<port> and either no Origin or our own; a cross-site
    request carries that site's Origin, so requiring both settles it without a token.
    """
    hostname = (host or "").rsplit(":", 1)[0].strip("[]").lower()
    if hostname and hostname not in LOCAL_HOSTS:
        return False
    if origin:
        o = urlparse(origin).hostname
        if (o or "").lower() not in LOCAL_HOSTS:
            return False
    return True


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

    def _local_only(self) -> bool:
        if request_is_local(self.headers.get("Host"), self.headers.get("Origin")):
            return True
        self._send(403, "application/json", {"error": "cross-site request refused"})
        return False

    def do_GET(self):
        if not self._local_only():
            return
        u = urlparse(self.path)
        self._send(*route(self.root, self.main_rel, "GET", u.path, parse_qs(u.query), {}))

    def do_POST(self):
        if not self._local_only():
            return
        u = urlparse(self.path)
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            self._send(400, "application/json", {"error": "invalid JSON body"})
            return
        self._send(*route(self.root, self.main_rel, "POST", u.path, parse_qs(u.query), body))


def find_existing(root: Path, start: int) -> tuple[str | None, str | None]:
    """Probe nearby ports for a texreview instance already serving this root.

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
        if info.get("root") != str(root) or info.get("tool") != "texreview":
            continue
        url = f"http://127.0.0.1:{port}/"
        if info.get("build") == BUILD:
            return url, None
        stale = stale or url
    return None, stale


def main() -> None:
    ap = argparse.ArgumentParser(description="texreview: local LaTeX + PDF review UI")
    ap.add_argument("--port", type=int, default=8378)
    ap.add_argument("--open", action="store_true", help="open the browser")
    ap.add_argument("--root", default=".", help="manuscript repo (default: resolve from cwd)")
    ap.add_argument("--main", default=None, help="main .tex file (default: auto-detect)")
    args = ap.parse_args()
    root = find_root(Path(args.root).resolve())
    main_rel = find_main_tex(root, args.main)
    texdir = tex_bin_dir()
    for tool, needed_for in (("latexmk", "Recompile"), ("synctex", "click-to-source sync")):
        if shutil.which(tool) is None and not (texdir and (Path(texdir) / tool).is_file()):
            print(f"warning: {tool} not found on PATH - {needed_for} will not work")
    if texdir:
        print(f"note: using the TeX toolchain in {texdir} (not on this shell's PATH)")
    existing, stale = find_existing(root, args.port)
    if existing:
        print(f"texreview already serving {root}")
        print(f"  {existing}   (reusing the running instance)")
        if args.open:
            webbrowser.open(existing)
        return
    if stale:
        print(f"note: {stale} runs an older build of texreview and was not reused.")
        print("      stop it (Ctrl-C in its terminal) and close that tab to avoid confusion.")
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
