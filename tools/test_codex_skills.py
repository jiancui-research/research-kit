"""The committed Codex plugin layout must match what gen_codex_skills.py produces.

skills/ and .codex-plugin/plugin.json are generated from commands/. Generated files that
live in a repo rot silently - this repo has already lost time to two of them - so the
suite regenerates into a scratch copy and diffs.

Run: uv run --with pytest pytest tools/test_codex_skills.py
"""
import json
import re
from pathlib import Path

import pytest

import gen_codex_skills as gen

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
COMMANDS = ROOT / "commands"
CODEX_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"


def stages():
    return sorted(p.stem for p in COMMANDS.glob("research.*.md"))


def test_every_command_has_a_skill():
    assert sorted(p.name for p in SKILLS.iterdir() if p.is_dir()) == stages()


def test_no_orphan_skill():
    """A renamed or deleted command must not leave its skill behind."""
    for d in SKILLS.iterdir():
        if d.is_dir():
            assert (COMMANDS / f"{d.name}.md").is_file(), f"{d.name} has no command"


@pytest.mark.parametrize("stage", stages())
def test_skill_matches_generator(stage, tmp_path, monkeypatch):
    """Byte-for-byte: regenerate into a scratch tree and compare."""
    scratch = tmp_path / "repo"
    (scratch / "commands").mkdir(parents=True)
    (scratch / ".claude-plugin").mkdir()
    for p in COMMANDS.glob("research.*.md"):
        (scratch / "commands" / p.name).write_text(p.read_text())
    (scratch / ".claude-plugin" / "plugin.json").write_text(CLAUDE_MANIFEST.read_text())
    monkeypatch.setattr(gen, "ROOT", scratch)
    monkeypatch.setattr(gen, "COMMANDS", scratch / "commands")
    monkeypatch.setattr(gen, "SKILLS", scratch / "skills")
    monkeypatch.setattr(gen, "MANIFEST_DIR", scratch / ".codex-plugin")
    monkeypatch.setattr(gen, "CLAUDE_MANIFEST", scratch / ".claude-plugin" / "plugin.json")
    gen.build()
    fresh = (scratch / "skills" / stage / "SKILL.md").read_text()
    committed = (SKILLS / stage / "SKILL.md").read_text()
    assert committed == fresh, f"{stage}: run python3 tools/gen_codex_skills.py"


def test_skill_frontmatter_is_what_codex_needs():
    """Codex documents name + description; the third field is Claude's guard."""
    for stage in stages():
        fm = gen.read_frontmatter((SKILLS / stage / "SKILL.md").read_text())
        assert fm.get("name") == stage
        assert fm.get("description"), f"{stage}: empty description"
        # Claude Code auto-discovers a plugin's skills/; without this a research stage
        # could fire on its own, which no stage in this pipeline is allowed to do.
        assert fm.get("disable-model-invocation") == "true", stage


def test_description_matches_its_command():
    for stage in stages():
        cmd_fm = gen.read_frontmatter((COMMANDS / f"{stage}.md").read_text())
        skill_fm = gen.read_frontmatter((SKILLS / stage / "SKILL.md").read_text())
        assert skill_fm["description"] == cmd_fm["description"].strip().strip('"'), stage


def test_skill_points_at_its_command_and_copies_nothing():
    """The pointer must name its own command file, and stay short enough to be a pointer."""
    for stage in stages():
        body = (SKILLS / stage / "SKILL.md").read_text()
        assert f"commands/{stage}.md" in body, f"{stage}: does not name its command"
        assert len(body.splitlines()) < 40, f"{stage}: too long to be a pointer, not a copy"


def test_codex_manifest_tracks_the_claude_one():
    codex = json.loads(CODEX_MANIFEST.read_text())
    claude = json.loads(CLAUDE_MANIFEST.read_text())
    assert codex["version"] == claude["version"], "run python3 tools/gen_codex_skills.py"
    assert codex["name"] == claude["name"]
    assert codex["skills"] == "./skills/"


def test_manifest_version_is_semver():
    v = json.loads(CODEX_MANIFEST.read_text())["version"]
    assert re.fullmatch(r"\d+\.\d+\.\d+", v), v
