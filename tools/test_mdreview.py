import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import mdreview as m


@pytest.fixture
def repo(tmp_path):
    (tmp_path / ".research").mkdir()
    (tmp_path / ".research" / "proposal.md").write_text(
        "# Prop\n\nPrior work does X.\n", encoding="utf-8"
    )
    (tmp_path / "README.md").write_text("hello\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "skip.md").write_text("skip", encoding="utf-8")
    return tmp_path


def test_safe_resolve_allows_inside(repo):
    p = m.safe_resolve(repo, ".research/proposal.md")
    assert p == repo / ".research" / "proposal.md"


def test_safe_resolve_blocks_traversal(repo):
    for evil in ("../evil.md", "a/../../evil.md", "/etc/passwd"):
        with pytest.raises(m.RequestError) as e:
            m.safe_resolve(repo, evil)
        assert e.value.status == 400


def test_list_md_files_skips_pruned_dirs(repo):
    assert m.list_md_files(repo) == ["README.md", ".research/proposal.md"]


def test_read_doc(repo):
    doc = m.read_doc(repo, ".research/proposal.md")
    assert doc["content"].startswith("# Prop")
    assert isinstance(doc["mtime"], float)


def test_read_doc_missing(repo):
    with pytest.raises(m.RequestError) as e:
        m.read_doc(repo, "nope.md")
    assert e.value.status == 404


def test_read_doc_rejects_non_utf8(repo):
    (repo / "bin.md").write_bytes(b"\xff\xfe\x00bad")
    with pytest.raises(m.RequestError) as e:
        m.read_doc(repo, "bin.md")
    assert e.value.status == 415


def test_read_doc_rejects_huge(repo):
    (repo / "big.md").write_text("a" * (m.MAX_BYTES + 1), encoding="utf-8")
    with pytest.raises(m.RequestError) as e:
        m.read_doc(repo, "big.md")
    assert e.value.status == 413


def test_write_doc_roundtrip_and_conflict(repo):
    rel = ".research/proposal.md"
    doc = m.read_doc(repo, rel)
    res = m.write_doc(repo, rel, "# New\n", doc["mtime"])
    assert m.read_doc(repo, rel)["content"] == "# New\n"
    stale = res["mtime"] - 100
    with pytest.raises(m.RequestError) as e:
        m.write_doc(repo, rel, "# Newer\n", stale)
    assert e.value.status == 409
    m.write_doc(repo, rel, "# Forced\n", None)  # None skips the guard
    assert m.read_doc(repo, rel)["content"] == "# Forced\n"


def test_write_doc_creates_parents(repo):
    m.write_doc(repo, "paper/new/intro.md", "hi\n", None)
    assert (repo / "paper" / "new" / "intro.md").read_text(encoding="utf-8") == "hi\n"


def test_comments_crud(repo):
    rel = ".research/proposal.md"
    assert m.load_comments(repo, rel) == []
    c = m.add_comment(repo, rel, "Prior work does X", "", ".", "too vague - name the work")
    assert c["resolved"] is False and len(c["id"]) == 12
    assert (repo / ".mdreview" / ".research" / "proposal.md.json").is_file()
    got = m.load_comments(repo, rel)
    assert len(got) == 1 and got[0]["comment"] == "too vague - name the work"
    upd = m.update_comment(repo, rel, c["id"], {"resolved": True})
    assert upd["resolved"] is True
    m.delete_comment(repo, rel, c["id"])
    assert m.load_comments(repo, rel) == []


def test_comment_unknown_id(repo):
    rel = ".research/proposal.md"
    with pytest.raises(m.RequestError) as e:
        m.update_comment(repo, rel, "deadbeef0000", {"resolved": True})
    assert e.value.status == 404


def test_render_md_tables_and_code():
    html = m.render_md("**hi**\n\n| a |\n| - |\n| b |\n\n```py\nx=1\n```\n")
    assert "<strong>hi</strong>" in html and "<table>" in html and "<code" in html


def test_export_includes_unresolved_only(repo):
    rel = ".research/proposal.md"
    keep = m.add_comment(repo, rel, "Prior work does X", "", ".", "name the actual papers")
    done = m.add_comment(repo, rel, "# Prop", "", "", "old note")
    m.update_comment(repo, rel, done["id"], {"resolved": True})
    out = m.export_text(repo, rel)
    assert out.startswith("Review this document and address each reviewer comment")
    assert ".mdreview/.research/proposal.md.json" in out   # tells file-access AIs where to reply
    assert "RESOLUTIONS" in out                            # fallback block for clipboard AIs
    assert f"[id: {keep['id']}]" in out                    # ids included for the reply loop
    assert "Prior work does X." in out            # full source present
    assert "name the actual papers" in out        # unresolved comment present
    assert "old note" not in out                  # resolved comment omitted
    assert "## Reviewer comments" in out


def test_update_comment_stores_reply(repo):
    rel = ".research/proposal.md"
    c = m.add_comment(repo, rel, "12 CWE classes", "", "", "list them")
    upd = m.update_comment(repo, rel, c["id"], {"resolved": True, "reply": "added appendix table A1"})
    assert upd["resolved"] is True and upd["reply"] == "added appendix table A1"
    assert m.load_comments(repo, rel)[0]["reply"] == "added appendix table A1"


def test_route_files_and_doc(repo):
    status, ctype, payload = m.route(repo, "GET", "/api/files", {}, {})
    assert status == 200 and payload == ["README.md", ".research/proposal.md"]
    status, _, doc = m.route(repo, "GET", "/api/doc", {"path": [".research/proposal.md"]}, {})
    assert status == 200 and "<h1>" in doc["html"] and doc["comments"] == []


def test_route_error_mapping(repo):
    status, _, err = m.route(repo, "GET", "/api/doc", {"path": ["../evil.md"]}, {})
    assert status == 400 and "escapes root" in err["error"]
    status, _, _ = m.route(repo, "GET", "/api/doc", {}, {})
    assert status == 400
    status, _, _ = m.route(repo, "GET", "/api/nope", {}, {})
    assert status == 404


def test_route_save_and_comment_flow(repo):
    rel = ".research/proposal.md"
    _, _, doc = m.route(repo, "GET", "/api/doc", {"path": [rel]}, {})
    status, _, res = m.route(repo, "POST", "/api/doc",
                             {}, {"path": rel, "content": "# Edited\n", "mtime": doc["mtime"]})
    assert status == 200 and "mtime" in res
    status, _, c = m.route(repo, "POST", "/api/comment/add",
                           {}, {"path": rel, "quote": "Edited", "prefix": "# ",
                                "suffix": "", "comment": "why edited?"})
    assert status == 200 and c["quote"] == "Edited"
    status, _, c2 = m.route(repo, "POST", "/api/comment/update",
                            {}, {"path": rel, "id": c["id"], "resolved": True})
    assert status == 200 and c2["resolved"] is True
    status, _, _ = m.route(repo, "POST", "/api/comment/delete", {}, {"path": rel, "id": c["id"]})
    assert status == 200 and m.load_comments(repo, rel) == []


def test_missing_body_keys_are_400(repo):
    status, _, _ = m.route(repo, "POST", "/api/doc", {}, {})
    assert status == 400  # route() itself: missing keys
    # the handler maps unparseable JSON to 400 before route(); covered via curl smoke test


def test_route_render_live_preview(repo):
    status, _, res = m.route(repo, "POST", "/api/render", {}, {"content": "# Hi\n\n*there*"})
    assert status == 200 and "<h1>" in res["html"] and "<em>there</em>" in res["html"]


def test_route_root_identity(repo):
    status, _, res = m.route(repo, "GET", "/api/root", {}, {})
    assert status == 200 and res == {"root": str(repo)}
