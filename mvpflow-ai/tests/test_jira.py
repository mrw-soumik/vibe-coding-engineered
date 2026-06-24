"""Jira-integration tests: ADF, payload building, dry-run (no network)."""
from __future__ import annotations

import pytest

from app.integrations import jira
from app.models import JiraTicket


def _ticket(**kw) -> JiraTicket:
    base = dict(
        key="MVP-001", title="Build the thing",
        user_story="As a founder, I want X so that Y.",
        description="desc", acceptance_criteria=["a", "b", "c"],
        priority="High", definition_of_done=["d1", "d2", "d3"],
        suggested_branch="feature/mvp-001-build", story_points=5,
    )
    base.update(kw)
    return JiraTicket(**base)


def test_ticket_to_adf_is_valid_doc():
    adf = jira.ticket_to_adf(_ticket())
    assert adf["type"] == "doc" and adf["version"] == 1
    assert any(node["type"] == "bulletList" for node in adf["content"])


def test_build_issue_payload_includes_points_and_labels():
    payload = jira.build_issue_payload(_ticket(), project_key="WOR", story_points_field="customfield_10016")
    fields = payload["fields"]
    assert fields["project"]["key"] == "WOR"
    assert fields["summary"].startswith("[MVP-001]")
    assert "mvpflow" in fields["labels"] and "priority-high" in fields["labels"]
    assert fields["customfield_10016"] == 5


def test_payload_omits_points_when_no_field():
    payload = jira.build_issue_payload(_ticket(), project_key="WOR", story_points_field=None)
    assert "customfield_10016" not in payload["fields"]


def test_push_tickets_dry_run_makes_no_network_call(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("dry-run must not hit the network")

    monkeypatch.setattr("app.integrations.jira.httpx.post", boom)
    monkeypatch.setattr("app.integrations.jira.httpx.get", boom)
    results = jira.push_tickets([_ticket()], project_key="WOR", dry_run=True)
    assert results[0]["status"] == "dry_run"
    assert results[0]["payload"]["fields"]["summary"].startswith("[MVP-001]")


def test_jira_disabled_without_credentials(monkeypatch):
    from app.config import config
    monkeypatch.setattr(config, "JIRA_BASE_URL", "")
    monkeypatch.setattr(config, "JIRA_EMAIL", "")
    monkeypatch.setattr(config, "JIRA_API_TOKEN", "")
    assert jira.jira_enabled() is False
    assert jira.find_issue_for_ticket(_ticket()) is None
