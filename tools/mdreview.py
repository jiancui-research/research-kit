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
