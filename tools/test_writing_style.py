"""Instruction contracts, not an end-to-end test of agent writing behavior."""
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent


def read(relative: str) -> str:
    return " ".join((ROOT / relative).read_text().split())


def test_recover_existing_choices_before_asking():
    guide = read("guides/writing-style.md")
    assert guide.index("Recover before asking") < guide.index("Ask only when unresolved")
    for source in ("legacy style files", "project notes", "accessible conversation"):
        assert source in guide
    assert "A citation or an unapproved candidate list is not a selection" in guide


def test_one_analyzed_example_does_not_require_another_approval():
    guide = read("guides/writing-style.md")
    assert "One relevant, selected paper with full-text analysis is enough" in guide
    assert "Do not ask for a waiver or more papers merely to reach a count" in guide
    assert "At least two papers are needed only to infer shared patterns" in guide


def test_delegated_selection_is_distinct_from_suggest_only():
    guide = read("guides/writing-style.md")
    assert "**Suggest only:**" in guide
    assert "**Find and choose:**" in guide
    assert "without another selection approval" in guide
    assert "user-selected, recovered, or agent-selected under delegated research" in guide
    assert "Suggestions alone are not authorization to choose" in guide


def test_recovery_preserves_scope_and_does_not_invent_analysis():
    guide = read("guides/writing-style.md")
    assert "do not extend an explicit section-only choice" in guide
    assert "Unreadable or abstract-only papers do not count as analyzed examples" in guide
    assert "A request-only skip does not carry forward" in guide
    assert "Report conflicts that would change the topic, paper type, or scope" in guide


@pytest.mark.parametrize("stage", ["write", "implement"])
def test_both_writing_entry_points_use_the_shared_decision(stage):
    command = read(f"commands/research.{stage}.md")
    assert "<bundle>/guides/writing-style.md" in command
    assert "recover existing choices" in command
    assert "delegated selection" in command
    assert "use 2–3 relevant example papers" not in command
    assert "ask and wait" not in command.lower()


def test_style_template_records_authority_without_requiring_two_papers():
    template = read("templates/style-template.md")
    assert "**Selection basis:**" in template
    assert "One relevant paper read in full is sufficient" in template
    assert "at least two papers read in full" not in template
