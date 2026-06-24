"""Jira Cloud integration for MVPFlow AI.

Turns the generated :class:`~app.models.JiraTicket` objects into real issues in
a Jira Cloud project via the REST API v3 (``POST /rest/api/3/issue``).

Security & safety design:

* Credentials are read **only** from environment variables, never hardcoded,
  never passed through the chat. Set ``JIRA_BASE_URL``, ``JIRA_EMAIL``,
  ``JIRA_API_TOKEN`` (an Atlassian API token), and ``JIRA_PROJECT_KEY``.
* Creating issues is an irreversible, outward-facing action, so
  :func:`push_tickets` defaults to ``dry_run=True``, it prints what *would* be
  created and makes no network calls until you explicitly opt in.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import List, Optional

import httpx

from app.config import config
from app.models import JiraTicket

logger = logging.getLogger(__name__)

# Jira Cloud REST API v3 endpoints (relative to the site base URL).
_CREATE_ISSUE_PATH = "/rest/api/3/issue"
_FIELD_PATH = "/rest/api/3/field"
_DEFAULT_ISSUE_TYPE = "Story"
_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

# Field names Jira uses for story points (team-managed vs company-managed).
_STORY_POINT_FIELD_NAMES = {"story point estimate", "story points"}


def jira_enabled() -> bool:
    """Return True when Jira credentials are fully configured."""
    return bool(config.JIRA_BASE_URL and config.JIRA_EMAIL and config.JIRA_API_TOKEN)


def _auth() -> tuple[str, str]:
    return (config.JIRA_EMAIL, config.JIRA_API_TOKEN)


@lru_cache(maxsize=1)
def discover_story_points_field() -> Optional[str]:
    """Resolve the Story Points custom field id for this Jira instance.

    Uses ``JIRA_STORY_POINTS_FIELD`` if set; otherwise queries the Jira field
    list and matches by name. Returns ``None`` if it can't be determined (in
    which case issues are still created, just without story points).
    """
    if config.JIRA_STORY_POINTS_FIELD:
        return config.JIRA_STORY_POINTS_FIELD
    if not jira_enabled():
        return None
    try:
        base = config.JIRA_BASE_URL.rstrip("/")
        resp = httpx.get(
            f"{base}{_FIELD_PATH}",
            auth=_auth(),
            headers={"Accept": "application/json"},
            timeout=30.0,
        )
        resp.raise_for_status()
        for field in resp.json():
            if field.get("name", "").strip().lower() in _STORY_POINT_FIELD_NAMES:
                logger.info("Resolved Story Points field: %s (%s)", field["id"], field["name"])
                return field["id"]
        logger.warning("No Story Points field found on this Jira instance")
    except httpx.HTTPError as e:
        logger.warning("Could not discover Story Points field: %s", e)
    return None


def _adf_paragraph(text: str) -> dict:
    """Build a single ADF paragraph node from plain text."""
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def _adf_bullet_list(items: List[str]) -> dict:
    """Build an ADF bullet list from a list of strings."""
    return {
        "type": "bulletList",
        "content": [
            {"type": "listItem", "content": [_adf_paragraph(item)]}
            for item in items
        ],
    }


def _adf_heading(text: str) -> dict:
    """Build an ADF level-3 heading node."""
    return {"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": text}]}


def ticket_to_adf(ticket: JiraTicket) -> dict:
    """Render a JiraTicket as an Atlassian Document Format (ADF) document.

    Jira Cloud REST API v3 requires the ``description`` field to be ADF, not
    plain text or wiki markup.
    """
    content: List[dict] = [
        _adf_paragraph(ticket.user_story),
        _adf_paragraph(ticket.description),
        _adf_heading("Acceptance Criteria"),
        _adf_bullet_list(ticket.acceptance_criteria),
        _adf_heading("Definition of Done"),
        _adf_bullet_list(ticket.definition_of_done),
        _adf_paragraph(f"Suggested branch: {ticket.suggested_branch}"),
        _adf_paragraph(f"Source: MVPFlow AI ({ticket.key})"),
    ]
    return {"type": "doc", "version": 1, "content": content}


def build_issue_payload(
    ticket: JiraTicket,
    project_key: Optional[str] = None,
    story_points_field: Optional[str] = None,
) -> dict:
    """Build the JSON payload for a Jira create-issue request.

    Priority is encoded as a label rather than the ``priority`` field, because
    the priority scheme (and its required option IDs) varies per Jira project;
    labels are universally accepted and avoid a 400 on instances without it.

    Story points are written to ``story_points_field`` (the instance-specific
    custom field id) when both that field and ``ticket.story_points`` are known.
    """
    project_key = project_key or config.JIRA_PROJECT_KEY
    fields = {
        "project": {"key": project_key},
        "summary": f"[{ticket.key}] {ticket.title}",
        "description": ticket_to_adf(ticket),
        "issuetype": {"name": _DEFAULT_ISSUE_TYPE},
        "labels": ["mvpflow", f"priority-{ticket.priority.lower()}"],
    }
    if story_points_field and ticket.story_points is not None:
        fields[story_points_field] = ticket.story_points
    return {"fields": fields}


def create_issue(ticket: JiraTicket, project_key: Optional[str] = None) -> dict:
    """Create a single Jira issue and return ``{"key", "url"}``.

    Raises:
        RuntimeError: If Jira is not configured.
        httpx.HTTPStatusError: If Jira rejects the request.
    """
    if not jira_enabled():
        raise RuntimeError(
            "Jira is not configured. Set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN."
        )

    base = config.JIRA_BASE_URL.rstrip("/")
    payload = build_issue_payload(ticket, project_key, discover_story_points_field())

    resp = httpx.post(
        f"{base}{_CREATE_ISSUE_PATH}",
        json=payload,
        auth=_auth(),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=30.0,
    )
    resp.raise_for_status()
    data = resp.json()
    key = data.get("key", "")
    return {"key": key, "url": f"{base}/browse/{key}"}


def find_issue_for_ticket(ticket: JiraTicket, project_key: Optional[str] = None) -> Optional[dict]:
    """Find the live Jira issue created for ``ticket`` (matched by its [MVP-xxx]
    summary marker). Returns ``{"key", "url"}`` or None if not found.
    """
    if not jira_enabled():
        return None
    project_key = project_key or config.JIRA_PROJECT_KEY
    base = config.JIRA_BASE_URL.rstrip("/")
    jql = f'project = {project_key} AND summary ~ "\\"[{ticket.key}]\\"" ORDER BY created DESC'
    try:
        resp = httpx.get(
            f"{base}/rest/api/3/search/jql",
            params={"jql": jql, "maxResults": 1, "fields": "summary"},
            auth=_auth(), headers=_HEADERS, timeout=30.0,
        )
        resp.raise_for_status()
        issues = resp.json().get("issues", [])
        if issues:
            key = issues[0]["key"]
            return {"key": key, "url": f"{base}/browse/{key}"}
    except httpx.HTTPError as e:
        logger.warning("Issue lookup for %s failed: %s", ticket.key, e)
    return None


def add_comment(issue_key: str, text: str) -> bool:
    """Add a plain-text comment to a Jira issue. Returns True on success."""
    if not jira_enabled():
        raise RuntimeError("Jira is not configured.")
    base = config.JIRA_BASE_URL.rstrip("/")
    body = {"body": {"type": "doc", "version": 1, "content": [_adf_paragraph(text)]}}
    resp = httpx.post(
        f"{base}/rest/api/3/issue/{issue_key}/comment",
        json=body, auth=_auth(), headers=_HEADERS, timeout=30.0,
    )
    if resp.status_code >= 300:
        logger.warning("Comment on %s failed: %s %s", issue_key, resp.status_code, resp.text[:200])
        return False
    return True


def transition_issue(issue_key: str, target_status: str) -> bool:
    """Move an issue to a status by name (e.g. 'In Progress', 'Done').

    Looks up the available transitions for the issue and applies the one whose
    target status name matches (case-insensitive). Returns True on success,
    False if no matching transition is available (e.g. already in that status).
    """
    if not jira_enabled():
        raise RuntimeError("Jira is not configured.")
    base = config.JIRA_BASE_URL.rstrip("/")
    url = f"{base}/rest/api/3/issue/{issue_key}/transitions"

    resp = httpx.get(url, auth=_auth(), headers=_HEADERS, timeout=30.0)
    resp.raise_for_status()
    target = target_status.strip().lower()
    match = next(
        (t for t in resp.json().get("transitions", [])
         if t.get("to", {}).get("name", "").strip().lower() == target),
        None,
    )
    if not match:
        logger.info("No '%s' transition available for %s (already there?)", target_status, issue_key)
        return False

    post = httpx.post(url, json={"transition": {"id": match["id"]}}, auth=_auth(), headers=_HEADERS, timeout=30.0)
    if post.status_code >= 300:
        logger.warning("Transition of %s failed: %s %s", issue_key, post.status_code, post.text[:200])
        return False
    logger.info("Transitioned %s -> %s", issue_key, target_status)
    return True


def push_tickets(
    tickets: List[JiraTicket],
    project_key: Optional[str] = None,
    dry_run: bool = True,
) -> List[dict]:
    """Create the given tickets in Jira.

    Args:
        tickets: Generated tickets to create.
        project_key: Override the configured project key (default: JIRA_PROJECT_KEY).
        dry_run: When True (default), no network call is made; the payloads that
            *would* be sent are returned with ``"status": "dry_run"`` so you can
            review them before opting in to a real write.

    Returns:
        One result dict per ticket.
    """
    project_key = project_key or config.JIRA_PROJECT_KEY
    sp_field = discover_story_points_field()
    results: List[dict] = []

    for ticket in tickets:
        if dry_run:
            logger.info("[dry-run] Would create Jira issue in %s: %s", project_key, ticket.title)
            results.append({
                "ticket": ticket.key,
                "status": "dry_run",
                "story_points": ticket.story_points,
                "story_points_field": sp_field,
                "payload": build_issue_payload(ticket, project_key, sp_field),
            })
            continue

        try:
            created = create_issue(ticket, project_key)
            logger.info("Created Jira issue %s for %s", created["key"], ticket.key)
            results.append({"ticket": ticket.key, "status": "created", **created})
        except httpx.HTTPStatusError as e:
            body = e.response.text[:300]
            logger.error("Jira rejected %s: %s %s", ticket.key, e.response.status_code, body)
            results.append({
                "ticket": ticket.key,
                "status": "error",
                "status_code": e.response.status_code,
                "detail": body,
            })

    return results
