"""API-layer tests: health, workflow endpoint, input validation, history.

Exercises the FastAPI app end to end with the deterministic pipeline (LLM off),
covering bugs that previously had no coverage: the /health DB check, anonymous
access to /workflow (optional-auth), and execution persistence.
"""
from __future__ import annotations


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    # The text() fix means the DB connectivity check actually passes.
    assert body["database"] == "healthy"


def test_workflow_anonymous_ok(client):
    """Anonymous request must succeed (optional-auth fix) and return all sections."""
    r = client.post(
        "/api/v1/workflow",
        json={"notes": "Restaurant owners answer the same questions all day.", "domain": "restaurant"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["requirements"]["problem"]
    assert len(data["jira_tickets"]) >= 5
    assert data["evaluation"]["overall_score"] >= 1
    # Security/timing middleware actually runs now.
    assert r.headers.get("X-Request-ID")
    assert r.headers.get("X-Process-Time")


def test_workflow_rejects_short_notes(client):
    r = client.post("/api/v1/workflow", json={"notes": "too short", "domain": "restaurant"})
    assert r.status_code == 422  # Pydantic min_length


def test_workflow_rejects_script_injection(client):
    r = client.post(
        "/api/v1/workflow",
        json={"notes": "Hello <script>alert(1)</script> world, this is long enough.", "domain": "x"},
    )
    assert r.status_code == 422  # sanitize_notes validator rejects


def test_executions_history(client):
    # Ensure at least one execution exists, then list.
    client.post("/api/v1/workflow", json={"notes": "Founder notes long enough to pass.", "domain": "saas"})
    r = client.get("/api/v1/executions")
    assert r.status_code == 200
    body = r.json()
    assert "executions" in body and isinstance(body["executions"], list)
    assert body["total"] >= 1
