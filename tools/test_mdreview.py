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
