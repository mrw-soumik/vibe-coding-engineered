"""Optional observability wiring (error tracking / APM).

Honest, no-op-by-default hook: error tracking is enabled only when ``SENTRY_DSN``
is set *and* ``sentry-sdk`` is installed (it's in the optional ``monitoring``
extra). With no DSN this does nothing, there is no fake/partial APM. This is
the integration point you extend for Sentry, Datadog, OpenTelemetry, etc.
"""
from __future__ import annotations

import logging

from app.config import config

logger = logging.getLogger(__name__)


def init_observability() -> bool:
    """Initialize error tracking if configured. Returns True if enabled."""
    if not config.SENTRY_DSN:
        logger.info("Monitoring not configured (SENTRY_DSN unset), skipping.")
        return False
    try:
        import sentry_sdk
    except ImportError:
        logger.warning("SENTRY_DSN is set but sentry-sdk is not installed "
                       "(pip install '.[monitoring]'). Skipping.")
        return False

    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        environment=config.APP_ENV,
        traces_sample_rate=0.0,  # set >0 to enable performance tracing
    )
    logger.info("Sentry error tracking initialized (env=%s).", config.APP_ENV)
    return True
