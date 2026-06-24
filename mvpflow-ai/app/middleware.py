"""Middleware and production utilities for MVPFlow AI.

Provides request/response tracking, rate limiting, CORS, security headers,
and other production features.
"""
from __future__ import annotations
import uuid
import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging.handlers
from pathlib import Path

from app.config import config

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID tracking."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to request and response.

        Args:
            request: FastAPI request object.
            call_next: Next middleware/handler callable.

        Returns:
            Response with request ID header.
        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to track request execution time."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track request execution time.

        Args:
            request: FastAPI request object.
            call_next: Next middleware/handler callable.

        Returns:
            Response with timing header.
        """
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.debug(
            f"Request {request.method} {request.url.path} "
            f"completed in {process_time:.2f}ms with status {response.status_code}"
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response.

        Args:
            request: FastAPI request object.
            call_next: Next middleware/handler callable.

        Returns:
            Response with security headers.
        """
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable browser XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # HTTPS enforcement
        if config.REQUIRE_HTTPS:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


def setup_cors(app) -> None:
    """Setup CORS middleware.
    
    Args:
        app: FastAPI application instance.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )
    logger.info(f"CORS configured for origins: {config.ALLOWED_ORIGINS}")


def setup_custom_middleware(app) -> None:
    """Setup custom middleware.
    
    Args:
        app: FastAPI application instance.
    """
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    logger.info("Custom middleware configured")


def setup_rate_limiter() -> Limiter:
    """Setup rate limiter.
    
    Returns:
        Configured Limiter instance.
    """
    if config.RATE_LIMIT_ENABLED:
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[f"{config.RATE_LIMIT_REQUESTS}/{config.RATE_LIMIT_WINDOW} seconds"]
        )
        logger.info(
            f"Rate limiting enabled: {config.RATE_LIMIT_REQUESTS} requests per {config.RATE_LIMIT_WINDOW}s"
        )
        return limiter
    else:
        logger.info("Rate limiting disabled")
        return Limiter(key_func=get_remote_address, default_limits=[])


def setup_logging() -> None:
    """Setup production logging configuration."""
    # Ensure logs directory exists
    log_dir = Path(config.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config.LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)
    console_formatter = logging.Formatter(config.LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
    )
    file_handler.setLevel(config.LOG_LEVEL)
    file_formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    logger.info(f"Logging configured: level={config.LOG_LEVEL}, file={config.LOG_FILE}")


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request.
    
    Handles X-Forwarded-For header for proxied requests.
    
    Args:
        request: FastAPI request object.
        
    Returns:
        Client IP address.
    """
    if "x-forwarded-for" in request.headers:
        # Returns first IP in X-Forwarded-For list
        return request.headers["x-forwarded-for"].split(",")[0].strip()
    
    if request.client:
        return request.client.host
    
    return "unknown"
