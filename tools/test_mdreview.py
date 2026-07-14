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
