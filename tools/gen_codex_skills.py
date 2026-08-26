#!/usr/bin/env python3
"""Generate the Codex plugin layout (.codex-plugin/ + skills/) from commands/.

Codex reads a plugin's `skills/<name>/SKILL.md`; this bundle authors its stages as
`commands/research.<x>.md`. Rather than copy each command into a skill - a mirror that
would rot the moment a command changed - each generated SKILL.md is a POINTER: it carries
only the frontmatter Codex needs for discovery, plus the note that adapts the slash-command
form to a skill, and then tells the agent to read the command file that ships in the same
plugin. The instructions have exactly one home.

Run `python3 tools/gen_codex_skills.py` after adding or renaming a command;
`tools/test_codex_skills.py` fails if the committed tree does not match this generator.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMANDS = ROOT / "commands"
SKILLS = ROOT / "skills"
MANIFEST_DIR = ROOT / ".codex-plugin"

# Claude's manifest is the one a human edits; everything here is derived from it so the two
# plugin manifests cannot disagree about what version shipped.
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"


def read_frontmatter(md: str) -> dict[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", md, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def skill_body(stage: str, hint: str) -> str:
    """A pointer, not a copy. `stage` is e.g. research.write."""
    arg_line = (
        f"> - Where it references `$ARGUMENTS`, that means the user's latest message to you -\n"
        f">   their free-text input for this stage ({hint}). When they gave none, follow the\n"
        f">   step's \"if empty\" guidance or ask for it; never invent one.\n"
        if hint else
        "> - Where it references `$ARGUMENTS`, that means the user's latest message to you.\n"
        ">   When they gave none, follow the step's \"if empty\" guidance; never invent one.\n"
    )
    return (
        f"> **research-kit stage - `/{stage}`.**\n"
        f">\n"
        f"> The instructions for this stage are not duplicated here. Read\n"
        f"> `commands/{stage}.md` from this plugin's own directory - the folder two levels above\n"
        f"> this file - and follow it end to end. If you cannot find it, say so and stop rather\n"
        f"> than reconstructing the stage from memory.\n"
        f">\n"
        f"> Two adaptations from its original slash-command form:\n"
        f">\n"
        f"{arg_line}"
        f"> - Where a step ends with `Next: /research.<x>`, run the `research.<x>` skill next.\n"
        f">\n"
        f"> Everything else is unchanged: read and write only under `./.research/`, follow the\n"
        f"> command contract, and stay paper-type aware.\n"
    )


def build() -> list[Path]:
    manifest = json.loads(CLAUDE_MANIFEST.read_text())
    written: list[Path] = []

    if SKILLS.exists():
        shutil.rmtree(SKILLS)          # regenerate wholesale so a renamed stage cannot linger
    SKILLS.mkdir()

    for src in sorted(COMMANDS.glob("research.*.md")):
        stage = src.stem
        fm = read_frontmatter(src.read_text())
        desc = fm.get("description", "").strip().strip('"')
        hint = fm.get("argument-hint", "").strip().strip('"')
        if not desc:
            sys.exit(f"error: {src.name} has no description in its frontmatter")
        out = SKILLS / stage / "SKILL.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            "---\n"
            f"name: {stage}\n"
            f"description: {desc}\n"
            # Claude Code auto-discovers a plugin's skills/ and would otherwise let the model
            # fire a research stage on its own; every stage here is strictly user-driven.
            "disable-model-invocation: true\n"
            "---\n\n"
            + skill_body(stage, hint)
        )
        written.append(out)

    MANIFEST_DIR.mkdir(exist_ok=True)
    codex_manifest = MANIFEST_DIR / "plugin.json"
    codex_manifest.write_text(json.dumps({
        "name": manifest["name"],
        "version": manifest["version"],
        "description": manifest["description"],
        "skills": "./skills/",
    }, indent=2) + "\n")
    written.append(codex_manifest)
    return written


if __name__ == "__main__":
    files = build()
    print(f"generated {len(files) - 1} skills + {MANIFEST_DIR.name}/plugin.json")
