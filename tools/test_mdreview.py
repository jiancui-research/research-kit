import re
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
    assert "<strong>hi</strong>" in html and "<table" in html and "<code" in html


def test_render_md_nested_lists_two_space_indent():
    # GitHub-style 2-space nesting must produce nested lists (python-markdown wanted 4)
    html = m.render_md("- **Probe, two parts.**\n  - **Part 1** check\n  - **Part 2** estimate\n")
    assert html.count("<ul") == 2 and "<strong>Part 1</strong>" in html


def test_render_md_mermaid_fence_keeps_language_class():
    html = m.render_md("```mermaid\nflowchart LR\nA-->B\n```\n")
    assert 'class="language-mermaid"' in html


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


def test_update_comment_stores_reply_and_fixed(repo):
    rel = ".research/proposal.md"
    c = m.add_comment(repo, rel, "12 CWE classes", "", "", "list them")
    upd = m.update_comment(repo, rel, c["id"],
                           {"resolved": True, "reply": "added appendix table A1",
                            "fixed": "all 12 classes are listed in Table A1"})
    assert upd["resolved"] is True and upd["reply"] == "added appendix table A1"
    saved = m.load_comments(repo, rel)[0]
    assert saved["reply"] == "added appendix table A1"
    assert saved["fixed"] == "all 12 classes are listed in Table A1"


def test_export_mentions_fixed_field(repo):
    rel = ".research/proposal.md"
    m.add_comment(repo, rel, "Prior work does X", "", ".", "name the papers")
    out = m.export_text(repo, rel)
    assert '"fixed"' in out and '"reply"' in out


def test_route_files_and_doc(repo):
    status, ctype, payload = m.route(repo, "GET", "/api/files", {}, {})
    assert status == 200 and payload == ["README.md", ".research/proposal.md"]
    status, _, doc = m.route(repo, "GET", "/api/doc", {"path": [".research/proposal.md"]}, {})
    assert status == 200 and "<h1" in doc["html"] and doc["comments"] == []


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
    assert status == 200 and "<h1" in res["html"] and "<em>there</em>" in res["html"]


def test_route_root_identity(repo):
    status, _, res = m.route(repo, "GET", "/api/root", {}, {})
    assert status == 200 and res == {"root": str(repo), "build": m.BUILD, "mode": m.UI_MODE}


def test_root_reports_a_build_fingerprint(repo):
    # find_existing() refuses to reuse a server whose build differs, so that a
    # process started before an update is not silently kept alive
    _, _, res = m.route(repo, "GET", "/api/root", {}, {})
    assert len(res["build"]) == 12 and all(c in "0123456789abcdef" for c in res["build"])


def test_route_serves_repo_images(repo):
    png = b"\x89PNG\r\n\x1a\nfakepngdata"
    (repo / ".research" / "figs").mkdir()
    (repo / ".research" / "figs" / "plot.png").write_bytes(png)
    status, ctype, payload = m.route(repo, "GET", "/.research/figs/plot.png", {}, {})
    assert status == 200 and ctype == "image/png" and payload == png


def test_route_image_with_encoded_space(repo):
    (repo / "my plot.svg").write_text("<svg/>", encoding="utf-8")
    status, ctype, payload = m.route(repo, "GET", "/my%20plot.svg", {}, {})
    assert status == 200 and ctype == "image/svg+xml" and payload == b"<svg/>"


def test_route_image_traversal_blocked(repo):
    status, _, err = m.route(repo, "GET", "/../evil.png", {}, {})
    assert status == 400 and "escapes root" in err["error"]


def test_route_non_image_files_stay_404(repo):
    (repo / "x.exe").write_bytes(b"MZ")
    status, _, _ = m.route(repo, "GET", "/x.exe", {}, {})
    assert status == 404


def _ranges(html, tag=r"\w+"):
    return [(t, int(a), int(b)) for t, a, b in
            re.findall(r'<(' + tag + r')[^>]*data-l0="(\d+)" data-l1="(\d+)"', html)]


def test_render_tags_every_block_with_its_source_lines():
    # the review UI turns a rendered block back into markdown using these ranges, so
    # editing in the rendered view never converts HTML back into markdown
    src = "# Title\n\npara one\n\n- a\n- b\n\n```py\nx=1\n```\n"
    top = [(t, a, b) for t, a, b in _ranges(m.render_md(src)) if t != "li"]
    assert top == [("h1", 0, 1), ("p", 2, 3), ("ul", 4, 7), ("code", 7, 10)]
    lines = src.split("\n")
    assert lines[0:1] == ["# Title"]
    assert lines[2:3] == ["para one"]
    assert lines[4:7] == ["- a", "- b", ""]


def test_list_items_and_table_rows_get_their_own_range():
    # clicking one task in a queue must edit that task, not the whole list
    src = ("- [ ] T001 first\n- [ ] T002 second\n  continued here\n- [x] T003 done\n"
           "\n| a | b |\n| - | - |\n| 1 | 2 |\n| 3 | 4 |\n")
    html = m.render_md(src)
    items = [(a, b) for t, a, b in _ranges(html, "li")]
    # the multi-line item keeps both lines; the last item absorbs the trailing blank,
    # which blockSource() strips for display and restores on commit
    assert items == [(0, 1), (1, 3), (3, 5)]
    rows = [(a, b) for t, a, b in _ranges(html, "tr")]
    assert rows == [(5, 6), (7, 8), (8, 9)]          # header row + one range per body row
    lines = src.split("\n")
    assert lines[1:3] == ["- [ ] T002 second", "  continued here"]
    assert lines[7:8] == ["| 1 | 2 |"]
    assert lines[3:5] == ["- [x] T003 done", ""]


def test_nested_ranges_are_contained_not_overlapping():
    # a fine-grained range must sit inside its parent block, never straddle two blocks
    src = "# A\n\nfirst\n\n- outer\n  - nested\n\n| a |\n| - |\n| 1 |\n\nlast\n"
    rs = [(a, b) for _, a, b in _ranges(m.render_md(src))]
    for i, (a, b) in enumerate(rs):
        for c, d in rs[i + 1:]:
            disjoint = d <= a or b <= c
            contained = (a <= c and d <= b) or (c <= a and b <= d)
            assert disjoint or contained, f"({a},{b}) straddles ({c},{d}) in {rs}"


def test_split_mode_server_is_not_reused_for_review_mode(repo, monkeypatch):
    # the two commands share this server; reusing a split instance for /research.mdreview
    # would silently hand back the wrong UI
    monkeypatch.setattr(m, "UI_MODE", "split")
    _, _, split_root = m.route(repo, "GET", "/api/root", {}, {})
    monkeypatch.setattr(m, "UI_MODE", "review")
    _, _, review_root = m.route(repo, "GET", "/api/root", {}, {})
    assert split_root["mode"] == "split" and review_root["mode"] == "review"
    assert split_root["build"] == review_root["build"]   # same file, so only mode differs


# ---------- request origin ----------

def test_request_is_local_accepts_our_own_page():
    assert m.request_is_local("127.0.0.1:8377", None)
    assert m.request_is_local("localhost:8377", "http://127.0.0.1:8377")
    assert m.request_is_local("[::1]:8377", "http://localhost:8377")


def test_request_is_local_refuses_a_page_that_steered_us():
    # any site the user browses can POST to loopback; these tools write files and compile
    assert not m.request_is_local("127.0.0.1:8377", "https://evil.example")
    assert not m.request_is_local("127.0.0.1:8377", "null")


def test_request_is_local_refuses_a_rebound_hostname():
    # DNS rebinding: attacker.example resolving to 127.0.0.1 still reaches us
    assert not m.request_is_local("attacker.example:8377", None)
