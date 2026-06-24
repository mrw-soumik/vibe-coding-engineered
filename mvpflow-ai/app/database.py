"""Database models and setup for MVPFlow AI.

Provides SQLAlchemy ORM models for workflow execution history,
user sessions, and audit logs.
"""
from __future__ import annotations
from datetime import datetime, UTC
from sqlalchemy import Column, String, Text, Float, DateTime, Integer, Boolean, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


def _utcnow() -> datetime:
    """Return the current UTC time.

    Used as a SQLAlchemy ``default``/``onupdate`` *callable* so the timestamp is
    evaluated per row at insert/update time. Passing ``datetime.now(UTC)`` (a
    value) instead would freeze every row to the process start time.
    """
    return datetime.now(UTC)


class WorkflowExecution(Base):
    """Workflow execution record for history and auditing."""

    __tablename__ = "workflow_executions"

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(255), nullable=True)  # Optional user identifier
    domain = Column(String(50), nullable=False, default="restaurant")
    input_notes = Column(Text, nullable=False)
    requirements = Column(JSON, nullable=False)
    mvp_plan = Column(JSON, nullable=False)
    architecture = Column(JSON, nullable=False)
    jira_tickets = Column(JSON, nullable=False)
    evaluation = Column(JSON, nullable=False)
    final_summary = Column(Text, nullable=False)
    overall_score = Column(Float, nullable=False)
    execution_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)
    error_message = Column(Text, nullable=True)
    status = Column(String(20), default="success")  # success, error, pending

    def __repr__(self) -> str:
        return f"<WorkflowExecution(id={self.id}, domain={self.domain}, score={self.overall_score})>"


class APIUser(Base):
    """API user for authentication."""

    __tablename__ = "api_users"

    id = Column(String(36), primary_key=True)  # UUID
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<APIUser(id={self.id}, username={self.username})>"


class APIKey(Base):
    """API key for authentication (alternative to JWT)."""

    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), nullable=False, index=True)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, name={self.name})>"


class AuditLog(Base):
    """Audit log for tracking API requests and changes."""

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), nullable=True)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(255), nullable=False)
    resource_id = Column(String(255), nullable=True)
    status_code = Column(Integer, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, status={self.status_code})>"


class DatabaseManager:
    """Database connection and session management."""

    def __init__(self, database_url: str):
        """Initialize database manager.
        
        Args:
            database_url: SQLAlchemy database URL.
        """
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None

    def initialize(self) -> None:
        """Initialize database engine and create tables."""
        logger.info(f"Initializing database: {self.database_url}")
        self.engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {},
            pool_pre_ping=True,  # Test connections before using
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create all tables
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")

    def get_session(self) -> Session:
        """Get a new database session.
        
        Returns:
            SQLAlchemy Session instance.
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal()

    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# Global database manager instance
db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance.
    
    Returns:
        DatabaseManager instance.
        
    Raises:
        RuntimeError: If database manager is not initialized.
    """
    if db_manager is None:
        raise RuntimeError("Database manager not initialized")
    return db_manager


def init_db(database_url: str) -> DatabaseManager:
    """Initialize and return the database manager.
    
    Args:
        database_url: SQLAlchemy database URL.
        
    Returns:
        Initialized DatabaseManager instance.
    """
    global db_manager
    db_manager = DatabaseManager(database_url)
    db_manager.initialize()
    return db_manager


async def get_db_session() -> Session:
    """Dependency for getting database session in FastAPI endpoints.
    
    Yields:
        Database session for the request.
    """
    db = get_db_manager().get_session()
    try:
        yield db
    finally:
        db.close()
