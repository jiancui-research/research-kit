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


PAGE = "<!doctype html><title>mdreview</title>"  # replaced by the full UI in the next commit


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
