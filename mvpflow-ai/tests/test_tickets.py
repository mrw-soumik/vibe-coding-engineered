"""Tests for writing tickets to disk as agent-ready Markdown."""
from app.models import JiraTicket
from app.core.tickets import render_ticket_md, write_tickets


def _ticket() -> JiraTicket:
    return JiraTicket(
        key="MVP-001",
        title="Client Onboarding",
        user_story="As a coach, I want to onboard clients.",
        description="Create client profiles.",
        acceptance_criteria=["Profiles have name and email", "Coach can edit a profile"],
        priority="High",
        definition_of_done=["Implemented and tested"],
        suggested_branch="feature/mvp-001-onboarding",
        story_points=8.0,
    )


def test_render_ticket_md_has_key_criteria_and_points():
    md = render_ticket_md(_ticket())
    assert "# MVP-001: Client Onboarding" in md
    assert "- [ ] Profiles have name and email" in md
    assert "## Definition of done" in md
    assert "Story points:** 8" in md  # 8.0 rendered cleanly as 8


def test_write_tickets_creates_ticket_agents_and_index(tmp_path):
    written = write_tickets([_ticket()], tmp_path, "fitness")

    ticket_file = tmp_path / "MVP-001.md"
    agents = tmp_path / "AGENTS.md"
    index = tmp_path / "README.md"

    assert ticket_file.exists()
    assert agents.exists()
    assert index.exists()
    assert "fitness" in agents.read_text(encoding="utf-8")
    assert "MVP-001" in index.read_text(encoding="utf-8")
    assert ticket_file in written


def test_write_tickets_does_not_clobber_existing_agents(tmp_path):
    (tmp_path / "AGENTS.md").write_text("CUSTOM RULES", encoding="utf-8")
    write_tickets([_ticket()], tmp_path, "fitness")
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "CUSTOM RULES"
