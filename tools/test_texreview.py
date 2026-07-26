"""Tests for texreview's server core: run  uv run --with pytest pytest tools/test_texreview.py"""
import json
import subprocess
import time

import pytest

import texreview as tr


@pytest.fixture
def paper(tmp_path):
    (tmp_path / "main.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\nHello reviewers.\n\\end{document}\n")
    (tmp_path / "refs.bib").write_text("@misc{x, title={T}}\n")
    (tmp_path / "sections").mkdir()
    (tmp_path / "sections" / "intro.tex").write_text("Intro text.\n")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "junk.tex").write_text("\\documentclass{article}")
    return tmp_path


# ---------- path safety + discovery ----------

def test_safe_resolve_refuses_escape(paper):
    with pytest.raises(tr.RequestError) as e:
        tr.safe_resolve(paper, "../outside.tex")
    assert e.value.status == 400


def test_list_tex_files_prunes_and_sorts(paper):
    files = tr.list_tex_files(paper)
    assert files == ["main.tex", "refs.bib", "sections/intro.tex"]


def test_find_root_uses_cwd_with_documentclass(paper):
    assert tr.find_root(paper) == paper


def test_find_root_follows_paper_repo_pointer(tmp_path, paper):
    research = tmp_path / "study"
    (research / ".research").mkdir(parents=True)
    (research / ".research" / "paper-repo").write_text(f"{paper}\nhttps://example.com/repo\n")
    assert tr.find_root(research) == paper


def test_find_root_errors_without_tex_or_pointer(tmp_path):
    with pytest.raises(SystemExit):
        tr.find_root(tmp_path)


def test_find_root_errors_on_dangling_pointer(tmp_path):
    (tmp_path / ".research").mkdir()
    (tmp_path / ".research" / "paper-repo").write_text("/nope/definitely/missing\n")
    with pytest.raises(SystemExit):
        tr.find_root(tmp_path)


def test_find_main_tex_prefers_main(paper):
    (paper / "appendix.tex").write_text("\\documentclass{article}")
    assert tr.find_main_tex(paper) == "main.tex"


def test_find_main_tex_override_and_missing(paper):
    assert tr.find_main_tex(paper, "sections/intro.tex") == "sections/intro.tex"
    with pytest.raises(SystemExit):
        tr.find_main_tex(paper, "nope.tex")


def test_find_main_tex_requires_documentclass(tmp_path):
    (tmp_path / "notes.tex").write_text("no preamble here")
    with pytest.raises(SystemExit):
        tr.find_main_tex(tmp_path)


# ---------- docs ----------

def test_read_write_doc_roundtrip(paper):
    doc = tr.read_doc(paper, "main.tex")
    assert "Hello reviewers" in doc["content"]
    out = tr.write_doc(paper, "main.tex", "new content", doc["mtime"])
    assert tr.read_doc(paper, "main.tex")["content"] == "new content"
    assert out["mtime"] >= doc["mtime"]


def test_write_doc_conflict_409(paper):
    doc = tr.read_doc(paper, "main.tex")
    time.sleep(0.01)
    (paper / "main.tex").write_text("changed elsewhere")
    with pytest.raises(tr.RequestError) as e:
        tr.write_doc(paper, "main.tex", "mine", doc["mtime"])
    assert e.value.status == 409


def test_read_doc_missing_404(paper):
    with pytest.raises(tr.RequestError) as e:
        tr.read_doc(paper, "ghost.tex")
    assert e.value.status == 404


# ---------- comments ----------

def test_comment_crud(paper):
    c = tr.add_comment(paper, 2, "quoted text", "pre", "suf", "main.tex", 3, "tighten this")
    assert c["page"] == 2 and c["file"] == "main.tex" and not c["resolved"]
    got = tr.load_comments(paper)
    assert len(got) == 1 and got[0]["id"] == c["id"]
    tr.update_comment(paper, c["id"], {"resolved": True, "reply": "done", "fixed": "new text",
                                       "evil": "ignored"})
    got = tr.load_comments(paper)[0]
    assert got["resolved"] and got["reply"] == "done" and "evil" not in got
    tr.delete_comment(paper, c["id"])
    assert tr.load_comments(paper) == []


def test_comment_missing_id_404(paper):
    with pytest.raises(tr.RequestError) as e:
        tr.update_comment(paper, "nope", {"resolved": True})
    assert e.value.status == 404


def test_comment_without_synctex_location(paper):
    c = tr.add_comment(paper, 1, "q", "", "", None, None, "note")
    assert c["file"] is None and c["line"] is None


# ---------- synctex parsing ----------

EDIT_OUT = """This is SyncTeX command line utility
SyncTeX result begin
Output:main.pdf
Input:./sections/intro.tex
Line:42
Column:-1
Offset:0
SyncTeX result end
"""

VIEW_OUT = """This is SyncTeX command line utility
SyncTeX result begin
Output:main.pdf
Page:3
x:148.712997
y:678.433960
h:133.768005
v:681.912964
W:343.711014
H:8.966003
before:
offset:0
SyncTeX result end
"""


def test_parse_synctex_edit():
    rec = tr.parse_synctex_edit(EDIT_OUT)
    assert rec == {"input": "./sections/intro.tex", "line": 42}


def test_parse_synctex_edit_no_result_404():
    with pytest.raises(tr.RequestError) as e:
        tr.parse_synctex_edit("This is SyncTeX\nno records here\n")
    assert e.value.status == 404


def test_parse_synctex_view():
    rec = tr.parse_synctex_view(VIEW_OUT)
    assert rec["page"] == 3
    assert rec["v"] == pytest.approx(681.912964)
    assert rec["H"] == pytest.approx(8.966003)


def test_parse_synctex_view_no_result_404():
    with pytest.raises(tr.RequestError):
        tr.parse_synctex_view("nothing\n")


def test_synctex_edit_rejects_paths_outside_root(paper, monkeypatch):
    monkeypatch.setattr(tr, "_run_synctex",
                        lambda root, args: "Input:/usr/share/texmf/article.cls\nLine:5\n")
    with pytest.raises(tr.RequestError) as e:
        tr.synctex_edit(paper, "main.pdf", 1, 100, 100)
    assert e.value.status == 404


def test_find_text_locates_prose(paper):
    (paper / "sections" / "abstract.tex").write_text(
        "\\begin{abstract}\n"
        "Multi-agent collaboration systems (\\textit{MACS}), powered by large language\n"
        "models, solve complex problems.\n\\end{abstract}\n")
    hit = tr.find_text(paper, "Multi-agent collaboration systems (MACS), powered by large language models")
    assert hit == {"file": "sections/abstract.tex", "line": 2}


def test_find_text_prefers_full_match_over_prefix_elsewhere(paper):
    # the title line shares a prefix; the section file holds the whole sentence
    (paper / "main.tex").write_text(
        "\\documentclass{article}\n"
        "\\title{Multi-agent collaboration systems for privacy}\n"
        "\\begin{document}\\input{sections/abstract}\\end{document}\n")
    (paper / "sections" / "abstract.tex").write_text(
        "Multi-agent collaboration systems, powered by large language models, are hard.\n")
    hit = tr.find_text(paper, "Multi-agent collaboration systems, powered by large language models, are hard")
    assert hit["file"] == "sections/abstract.tex"


def test_find_text_ignores_comments_and_short_needles(paper):
    (paper / "sections" / "intro.tex").write_text(
        "% Ethics of the work and review was rewritten by an assistant here\n"
        "\\noindent Ethics of the work and review. No IRB was required for this study.\n")
    hit = tr.find_text(paper, "Ethics of the work and review. No IRB was required for this study")
    assert hit == {"file": "sections/intro.tex", "line": 2}
    assert tr.find_text(paper, "too short") is None


def test_is_structural_flags_prose_free_lines(paper):
    (paper / "main.tex").write_text(
        "\\documentclass{article}\n\\maketitle\n"
        "Real prose lives here and should not be structural.\n\n")
    assert tr.is_structural(paper, "main.tex", 2)      # \maketitle
    assert tr.is_structural(paper, "main.tex", 4)      # blank
    assert not tr.is_structural(paper, "main.tex", 3)  # prose


def test_route_sync_edit_falls_back_for_generated_file(paper, monkeypatch):
    # the comment package rewrites skipped blocks through comment.cut
    (paper / "comment.cut").write_text("Ethics of the work and review. No IRB was required.\n")
    (paper / "sections" / "ethics.tex").write_text(
        "\\noindent Ethics of the work and review. No IRB was required for this study here.\n")
    monkeypatch.setattr(tr, "_run_synctex",
                        lambda root, args: "Input:./comment.cut\nLine:1\n")
    status, _, payload = tr.route(paper, "main.tex", "POST", "/api/sync/edit", {}, {
        "page": 1, "x": 10, "y": 10,
        "text": "Ethics of the work and review. No IRB was required for this study here"})
    assert status == 200 and payload["file"] == "sections/ethics.tex" and payload["via"] == "text"


def test_route_sync_edit_rejects_generated_file_without_text(paper, monkeypatch):
    (paper / "comment.cut").write_text("x\n")
    monkeypatch.setattr(tr, "_run_synctex",
                        lambda root, args: "Input:./comment.cut\nLine:1\n")
    status, _, payload = tr.route(paper, "main.tex", "POST", "/api/sync/edit", {}, {
        "page": 1, "x": 10, "y": 10})
    assert status == 404 and "generated file" in payload["error"]


def test_route_sync_edit_keeps_synctex_when_line_has_prose(paper, monkeypatch):
    (paper / "sections" / "intro.tex").write_text("Body text that SyncTeX resolved correctly.\n")
    monkeypatch.setattr(tr, "_run_synctex",
                        lambda root, args: "Input:./sections/intro.tex\nLine:1\n")
    status, _, payload = tr.route(paper, "main.tex", "POST", "/api/sync/edit", {}, {
        "page": 1, "x": 10, "y": 10, "text": "Body text that SyncTeX resolved correctly"})
    assert payload == {"file": "sections/intro.tex", "line": 1, "via": "synctex"}


def test_synctex_edit_relativizes_input(paper, monkeypatch):
    monkeypatch.setattr(tr, "_run_synctex",
                        lambda root, args: f"Input:{paper}/sections/intro.tex\nLine:7\n")
    assert tr.synctex_edit(paper, "main.pdf", 1, 10, 10) == {
        "file": "sections/intro.tex", "line": 7}


# ---------- compile ----------

def test_latexmk_error_tail_extracts_bang_blocks():
    log = "junk\n" * 100 + "! Undefined control sequence.\nl.12 \\oops\ncontext\n" + "more\n" * 50
    tail = tr.latexmk_error_tail(log)
    assert tail.startswith("! Undefined control sequence.")
    assert "l.12" in tail


def test_latexmk_error_tail_falls_back_to_tail():
    log = "\n".join(f"line{i}" for i in range(100))
    tail = tr.latexmk_error_tail(log)
    assert "line99" in tail and "line10\n" not in tail


def test_run_compile_reports_failure(paper, monkeypatch):
    def fake_run(cmd, **kw):
        assert cmd[0] == "latexmk" and "-synctex=1" in cmd
        return subprocess.CompletedProcess(cmd, 1, stdout="! Emergency stop.\nboom\n", stderr="")
    monkeypatch.setattr(tr.subprocess, "run", fake_run)
    tr._run_compile(paper, "main.tex")
    s = tr.compile_status()
    assert s["ok"] is False and "Emergency stop" in s["log"] and not s["running"]


def test_start_compile_refuses_concurrent(paper):
    with tr._compile_lock:
        pass
    tr._compile.update(running=True)
    try:
        with pytest.raises(tr.RequestError) as e:
            tr.start_compile(paper, "main.tex")
        assert e.value.status == 409
    finally:
        tr._compile.update(running=False)


# ---------- pdf info + export ----------

def test_pdf_info_flags(paper):
    info = tr.pdf_info(paper, "main.tex")
    assert info == {"pdf": "main.pdf", "main": "main.tex", "exists": False,
                    "mtime": 0, "synctex": False}
    (paper / "main.pdf").write_bytes(b"%PDF-fake")
    (paper / "main.synctex.gz").write_bytes(b"gz")
    info = tr.pdf_info(paper, "main.tex")
    assert info["exists"] and info["synctex"] and info["mtime"] > 0


def test_export_text_targets_and_instructions(paper):
    tr.add_comment(paper, 3, "vague claim", "", "", "main.tex", 120, "cite or cut")
    tr.add_comment(paper, 1, "typo here", "", "", None, None, "fix spelling")
    resolved = tr.add_comment(paper, 1, "old", "", "", None, None, "gone")
    tr.update_comment(paper, resolved["id"], {"resolved": True})
    text = tr.export_text(paper, "main.tex")
    assert "`main.tex:120`, page 3" in text
    assert "page 1" in text and "typo here" in text
    assert "old" not in text                      # resolved comments stay out
    assert ".texreview/comments.json" in text and "RESOLUTIONS" in text
    assert "Hello reviewers" not in text          # no full-source embed by design


def test_export_text_no_open_comments(paper):
    assert "(no open comments)" in tr.export_text(paper, "main.tex")


# ---------- route ----------

def test_route_root_reports_tool(paper):
    status, ctype, payload = tr.route(paper, "main.tex", "GET", "/api/root", {}, {})
    assert status == 200 and payload["tool"] == "texreview" and payload["main"] == "main.tex"


def test_route_unknown_404_and_missing_param_400(paper):
    assert tr.route(paper, "main.tex", "GET", "/api/nope", {}, {})[0] == 404
    assert tr.route(paper, "main.tex", "GET", "/api/doc", {}, {})[0] == 400


def test_route_pdf_missing_404(paper):
    assert tr.route(paper, "main.tex", "GET", "/api/pdf", {}, {})[0] == 404


def test_route_export(paper):
    tr.add_comment(paper, 1, "q", "", "", "main.tex", 3, "c")
    status, ctype, text = tr.route(paper, "main.tex", "GET", "/api/export", {}, {})
    assert status == 200 and ctype.startswith("text/plain")
    assert "RESOLUTIONS" in text and "`main.tex:3`" in text


def test_route_comment_flow(paper):
    status, _, entry = tr.route(paper, "main.tex", "POST", "/api/comment/add", {}, {
        "page": 1, "quote": "q", "comment": "c"})
    assert status == 200 and entry["prefix"] == "" and entry["file"] is None
    status, _, got = tr.route(paper, "main.tex", "GET", "/api/comments", {}, {})
    assert status == 200 and len(got) == 1
