"""DB-layer tests: table creation and per-row timestamp defaults."""
from __future__ import annotations

import tempfile
import os
from datetime import datetime, timedelta, UTC

from app.database import DatabaseManager, WorkflowExecution


def _temp_manager() -> DatabaseManager:
    fd, path = tempfile.mkstemp(suffix=".db", prefix="mvpflow_dbtest_")
    os.close(fd)
    mgr = DatabaseManager(f"sqlite:///{path}")
    mgr.initialize()
    return mgr


def test_initialize_creates_tables_and_persists():
    mgr = _temp_manager()
    session = mgr.get_session()
    try:
        rec = WorkflowExecution(
            id="exec-1", domain="restaurant", input_notes="notes",
            requirements={}, mvp_plan={}, architecture={}, jira_tickets=[],
            evaluation={}, final_summary="s", overall_score=4.5, execution_time_ms=10,
            status="success",
        )
        session.add(rec)
        session.commit()

        got = session.query(WorkflowExecution).filter_by(id="exec-1").one()
        assert got.overall_score == 4.5
        # created_at default is a per-row callable (not frozen at import) → recent.
        # SQLite returns naive datetimes, so compare tz-agnostically.
        assert isinstance(got.created_at, datetime)
        now_naive = datetime.now(UTC).replace(tzinfo=None)
        created_naive = got.created_at.replace(tzinfo=None)
        assert now_naive - created_naive < timedelta(minutes=5)
    finally:
        session.close()
        mgr.close()
