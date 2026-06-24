"""Environment configuration for MVPFlow AI.

Loads configuration from environment variables with sensible defaults.
Uses python-dotenv to load from .env file in development.
"""
from __future__ import annotations
import os
from typing import Literal
from dotenv import load_dotenv

# Load .env file if it exists (development mode)
load_dotenv()


class Config:
    """Base configuration."""

    # Application
    APP_NAME = "MVPFlow AI"
    APP_VERSION = "1.0.0"
    DEBUG = False
    TESTING = False
    APP_ENV = os.getenv("APP_ENV", "development")  # Add APP_ENV as class attribute

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./mvpflow.db"  # Default to SQLite for development
    )
    
    # API
    API_V1_STR = "/api/v1"
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-change-in-production-DO-NOT-USE-IN-PROD"
    )
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    ALLOWED_ORIGINS = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8000"
    ).split(",")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/mvpflow.log")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security
    REQUIRE_HTTPS = os.getenv("REQUIRE_HTTPS", "false").lower() == "true"
    SECURE_COOKIES = os.getenv("SECURE_COOKIES", "false").lower() == "true"
    SAME_SITE = os.getenv("SAME_SITE", "lax")
    
    # Feature Flags
    ENABLE_SWAGGER_UI = os.getenv("ENABLE_SWAGGER_UI", "true").lower() == "true"
    ENABLE_JWT_AUTH = os.getenv("ENABLE_JWT_AUTH", "false").lower() == "true"

    # LLM (Claude) integration
    # When ANTHROPIC_API_KEY is set and USE_LLM is true, the workflow uses live
    # Claude calls for generation/extraction; otherwise it falls back to the
    # deterministic templates (which keeps the workshop demo and tests stable).
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    # Default off so the workshop demo is deterministic and never depends on a
    # live API call. Set USE_LLM=true (with ANTHROPIC_API_KEY) to enable Claude.
    USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"
    LLM_MODEL = os.getenv("LLM_MODEL", "claude-opus-4-8")
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    # Use the web-search tool for the research step (requires a web-search-capable
    # model + account). Falls back to knowledge-only research if off or unavailable.
    USE_WEB_SEARCH = os.getenv("USE_WEB_SEARCH", "true").lower() == "true"

    # Alternative provider: Groq (OpenAI-compatible API). Used only if no
    # ANTHROPIC_API_KEY is set. Structured output is done via JSON mode +
    # schema validation; adaptive thinking and native web search are Anthropic-only.
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    # Monitoring (optional). Set SENTRY_DSN to enable error tracking; no-op if
    # unset or the sentry-sdk package isn't installed.
    SENTRY_DSN = os.getenv("SENTRY_DSN", "")

    # Jira Cloud integration (optional)
    # Credentials are read from the environment only, never hardcode them.
    # Generate an API token at https://id.atlassian.com/manage-profile/security/api-tokens
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "")          # e.g. https://yoursite.atlassian.net
    JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")                # Atlassian account email
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")        # Atlassian API token
    JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "WOR")  # target project key
    # Story Points custom field id (e.g. "customfield_10016"). Leave blank to
    # auto-discover by field name ("Story point estimate" / "Story Points").
    JIRA_STORY_POINTS_FIELD = os.getenv("JIRA_STORY_POINTS_FIELD", "")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mvpflow_dev.db")
    ENABLE_JWT_AUTH = False


class TestingConfig(Config):
    """Testing configuration."""

    DEBUG = True
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
    ENABLE_JWT_AUTH = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False
    ENABLE_JWT_AUTH = True
    SECURE_COOKIES = True
    REQUIRE_HTTPS = True


def _validate_production_config() -> None:
    """Validate production configuration at runtime."""
    if not os.getenv("DATABASE_URL"):
        raise ValueError("DATABASE_URL environment variable must be set in production")
    
    if os.getenv("SECRET_KEY") == "dev-secret-key-change-in-production-DO-NOT-USE-IN-PROD":
        raise ValueError("SECRET_KEY environment variable must be set to a strong value in production")


def get_config() -> Config:
    """Get configuration based on APP_ENV environment variable.
    
    Returns:
        Config instance for the appropriate environment.
        
    Raises:
        ValueError: If production configuration is invalid.
    """
    env = os.getenv("APP_ENV", "development").lower()
    
    if env == "production":
        _validate_production_config()
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()


# Current configuration
config = get_config()
