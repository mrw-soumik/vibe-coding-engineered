"""Shared test configuration and fixtures.

Sets test-friendly environment BEFORE the app package is imported, so the
config singleton picks up a throwaway SQLite file and the deterministic
(LLM-off) path. Keeps tests hermetic, no real network or model calls.
"""
from __future__ import annotations

import os
import tempfile

# Must run before any `import app.*` so app.config reads these.
os.environ["USE_LLM"] = "false"
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
_DB_FD, _DB_PATH = tempfile.mkstemp(suffix=".db", prefix="mvpflow_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_PATH}"

# Neutralize any real provider/Jira credentials from a local .env so tests are
# hermetic (load_dotenv uses override=False, so these empty values win).
for _k in ("ANTHROPIC_API_KEY", "GROQ_API_KEY", "JIRA_BASE_URL", "JIRA_EMAIL",
           "JIRA_API_TOKEN", "JIRA_STORY_POINTS_FIELD"):
    os.environ[_k] = ""

import pytest


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient with lifespan run (initializes the DB on the temp file)."""
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def _cleanup_temp_db():
    yield
    # Dispose the SQLAlchemy engine first so Windows releases the SQLite file
    # lock; otherwise removing the temp DB raises PermissionError at teardown
    # (shows as a spurious "error" in an otherwise all-green run).
    try:
        from app.database import db_manager
        if db_manager is not None:
            db_manager.close()
    except Exception:
        pass
    try:
        os.close(_DB_FD)
    except OSError:
        pass
    try:
        if os.path.exists(_DB_PATH):
            os.remove(_DB_PATH)
    except OSError:
        pass
