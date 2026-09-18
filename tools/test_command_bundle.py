"""Public command handoffs and installation upgrades, using throwaway directories."""
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parent.parent
PUBLIC = {
    "proposal", "relatedwork", "feasibility", "plan", "implement", "write",
    "review", "mdreview", "texreview",
}
RETIRED = {"init", "constitution", "tasks", "style", "analyze", "ae", "rebuttal"}


def test_public_surface_and_documented_handoffs():
    stages = {p.stem.removeprefix("research.") for p in (ROOT / "commands").glob("*.md")}
    assert stages == PUBLIC
    sources = [ROOT / name for name in ("README.md", "CLAUDE.md", "CONTRIBUTING.md")]
    sources += list((ROOT / "docs").glob("*.md"))
    for directory in ("commands", "guides", "templates", "skills"):
        sources += list((ROOT / directory).rglob("*.md"))
    for source in sources:
        # Match invocations, not paths like .research/tasks.md or placeholder names.
        targets = set(re.findall(r"/research\.([a-z]+)\b", source.read_text()))
        assert targets <= PUBLIC, (source, targets - PUBLIC)
    documented = set(re.findall(r"^\| `/research\.([a-z]+)`", (ROOT / "README.md").read_text(), re.M))
    assert documented == PUBLIC


def test_bundle_guides_and_concrete_template_references_resolve():
    for directory in ("commands", "guides", "templates"):
        for source in (ROOT / directory).rglob("*.md"):
            text = source.read_text()
            for guide in re.findall(r"(?:<bundle>/)?guides/([a-z-]+\.md)", text):
                assert (ROOT / "guides" / guide).is_file(), (source, guide)
            for template in re.findall(r"\.research/templates/([a-z/-]+\.md)", text):
                assert (ROOT / "templates" / template).is_file(), (source, template)
    for command in (ROOT / "commands").glob("*.md"):
        assert "<bundle>/guides/setup.md" in command.read_text(), command


def install_env(tmp_path):
    env = os.environ.copy()
    for key, directory in (
        ("CLAUDE_COMMANDS_DIR", "claude"),
        ("CODEX_PROMPTS_DIR", "codex"),
        ("COPILOT_AGENTS_DIR", "copilot"),
        ("RESEARCH_KIT_HOME", "staging"),
    ):
        env[key] = str(tmp_path / directory)
    return env


def run_install(script, env, *args):
    result = subprocess.run(
        ["sh", str(script), *args], env=env, text=True,
        capture_output=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


@pytest.mark.parametrize("mode", [[], ["--symlink"]], ids=["copy", "symlink"])
def test_upgrade_prunes_retired_commands_and_ships_shared_resources(tmp_path, mode):
    old = tmp_path / "old-bundle"
    old.mkdir()
    shutil.copy2(ROOT / "install.sh", old / "install.sh")
    for directory in ("commands", "guides", "templates", "tools"):
        shutil.copytree(ROOT / directory, old / directory,
                        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    for stage in RETIRED:
        (old / "commands" / f"research.{stage}.md").write_text(
            f"---\ndescription: Retired {stage} fixture\n---\nOld stage.\n"
        )
    (old / "templates" / "ae-checklist.md").write_text("old template\n")
    env = install_env(tmp_path)
    run_install(old / "install.sh", env, "--all", *mode)
    destinations = [(tmp_path / agent, suffix) for agent, suffix in (
        ("claude", ".md"), ("codex", ".md"), ("copilot", ".agent.md"),
    )]
    for dest, _ in destinations:
        (dest / "research.personal.md").write_text("user command\n")

    for _ in range(2):
        run_install(ROOT / "install.sh", env, "--all", *mode)
        for dest, suffix in destinations:
            expected = {f"research.{stage}{suffix}" for stage in PUBLIC}
            assert {p.name for p in dest.glob("research.*")} == expected | {"research.personal.md"}
            assert (dest / "research.personal.md").read_text() == "user command\n"
        for directory in ("guides", "templates"):
            for source in (ROOT / directory).rglob("*.md"):
                staged = tmp_path / "staging" / source.relative_to(ROOT)
                assert staged.read_bytes() == source.read_bytes(), source
        assert not (tmp_path / "staging/templates/ae-checklist.md").exists()
        for tool in ("mdreview.py", "texreview.py"):
            assert (tmp_path / "staging/tools" / tool).is_file()
        for stage in PUBLIC:
            adapter = (tmp_path / "copilot" / f"research.{stage}.agent.md").read_text()
            assert "Do not run it unless requested" in adapter
            assert "read and write only under" not in adapter
            metadata = yaml.safe_load(adapter.split("---", 2)[1])
            assert isinstance(metadata["description"], str)

    # The existing uninstall removes the namespace, so remove our user-owned
    # upgrade sentinel before invoking it; the test concerns managed uninstall.
    for dest, _ in destinations:
        (dest / "research.personal.md").unlink()
    run_install(ROOT / "install.sh", env, "--uninstall")
    assert not (tmp_path / "staging").exists()
    assert all(not list(dest.glob("research.*")) for dest, _ in destinations)


def test_setup_copy_preserves_existing_project_state(tmp_path):
    project = tmp_path / "paper"
    local = project / ".research/templates"
    local.mkdir(parents=True)
    customized = local / "style-template.md"
    customized.write_text("user's custom template\n")
    snapshots = {
        ".research/tasks.md": "- [x] T001 completed with evidence\n",
        ".research/writing/style.md": "## Standing instructions\nUse direct sentences.\n",
        ".research/memory/constitution.md": "Existing project preferences\n",
        ".research/rebuttal/rebuttal.md": "Existing author response\n",
    }
    for name, content in snapshots.items():
        p = project / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    guide = (ROOT / "guides/setup.md").read_text()
    script = re.search(r"```sh\n(.*?)\n\s*```", guide, re.S).group(1)
    env = dict(os.environ, RESEARCH_KIT_BUNDLE=str(ROOT))
    for _ in range(2):
        result = subprocess.run(["sh", "-c", script], cwd=project, env=env,
                                text=True, capture_output=True, timeout=10)
        assert result.returncode == 0, result.stderr
    assert customized.read_text() == "user's custom template\n"
    assert (local / "sections/manuscript-procedure.md").is_file()
    for name, content in snapshots.items():
        assert (project / name).read_text() == content
