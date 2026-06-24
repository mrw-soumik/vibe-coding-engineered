"""Claude (Anthropic) integration for MVPFlow AI.

This module is the single point where the workflow talks to a live LLM. The
core modules (requirements extraction, MVP scope, evaluation) call
:func:`generate_structured` when :func:`llm_enabled` is true, and otherwise fall
back to their deterministic templates. That keeps the workshop demo and the
test suite stable with no API key, while making the "AI" real when a key is set.

Defaults to Claude Opus 4.8 (``claude-opus-4-8``) with adaptive thinking and
structured outputs (``messages.parse``), so responses validate against the same
Pydantic models the rest of the app already uses.
"""
from __future__ import annotations

import json
import logging
import time
from functools import lru_cache
from typing import Optional, Type, TypeVar

import httpx
from pydantic import BaseModel

from app.config import config

logger = logging.getLogger(__name__)

# Import is optional: the deterministic path must work even if the SDK isn't
# installed (e.g. CI runs the template-based tests without `anthropic`).
try:
    import anthropic
except ImportError:  # pragma: no cover - exercised only when SDK is absent
    anthropic = None

T = TypeVar("T", bound=BaseModel)


def provider() -> Optional[str]:
    """Which LLM provider is configured: 'anthropic' (preferred), 'groq', or None."""
    if anthropic and config.ANTHROPIC_API_KEY:
        return "anthropic"
    if config.GROQ_API_KEY:
        return "groq"
    return None


def llm_enabled() -> bool:
    """Return True when live LLM calls should be used (any supported provider)."""
    return config.USE_LLM and provider() is not None


@lru_cache(maxsize=1)
def _get_client():
    """Return a cached Anthropic client (one per process)."""
    if not anthropic:
        raise RuntimeError("anthropic SDK is not installed")
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def generate_structured(system: str, prompt: str, schema: Type[T]) -> T:
    """Call Claude and parse the response into ``schema``.

    Uses adaptive thinking and structured outputs so the returned object is a
    validated instance of the given Pydantic model.

    Args:
        system: System prompt describing the role and constraints.
        prompt: The user message (typically the founder notes plus a task).
        schema: Pydantic model the response must conform to.

    Returns:
        A validated instance of ``schema``.

    Raises:
        RuntimeError: If the model declines or returns no parseable output.
        Exception: Any underlying SDK/transport error (callers fall back).
    """
    if provider() == "groq":
        return _generate_groq(system, prompt, schema)

    client = _get_client()
    logger.debug("Calling Claude model=%s for schema=%s", config.LLM_MODEL, schema.__name__)

    response = client.messages.parse(
        model=config.LLM_MODEL,
        max_tokens=config.LLM_MAX_TOKENS,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{"role": "user", "content": prompt}],
        output_format=schema,
    )

    if response.stop_reason == "refusal":
        raise RuntimeError("Claude refused the request for safety reasons")

    parsed = response.parsed_output
    if parsed is None:
        raise RuntimeError("Claude returned no parseable structured output")

    return parsed


def _generate_groq(system: str, prompt: str, schema: Type[T]) -> T:
    """Structured generation via Groq's OpenAI-compatible API.

    Groq has no equivalent to Anthropic's ``messages.parse``; we use JSON mode and
    embed the target JSON Schema in the system prompt, then validate the response
    against the Pydantic model. Validation failure raises so callers can fall back.
    """
    schema_json = json.dumps(schema.model_json_schema())
    system_full = (
        f"{system}\n\nReturn ONLY a single JSON object that conforms to this JSON "
        f"Schema. No markdown, no prose, no code fences.\n\nSchema:\n{schema_json}"
    )
    logger.debug("Calling Groq model=%s for schema=%s", config.GROQ_MODEL, schema.__name__)
    payload = {
        "model": config.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_full},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
        "max_tokens": config.LLM_MAX_TOKENS,
    }
    headers = {"Authorization": f"Bearer {config.GROQ_API_KEY}", "Content-Type": "application/json"}
    url = f"{config.GROQ_BASE_URL.rstrip('/')}/chat/completions"

    # Free-tier Groq rate-limits aggressively; retry on 429 honoring Retry-After.
    last_exc: Optional[Exception] = None
    for attempt in range(5):
        resp = httpx.post(url, headers=headers, json=payload, timeout=120.0)
        if resp.status_code == 429:
            wait = float(resp.headers.get("retry-after", 2 ** attempt))
            wait = min(wait, 30.0)
            logger.warning("Groq 429; retrying in %.1fs (attempt %d/5)", wait, attempt + 1)
            time.sleep(wait)
            last_exc = httpx.HTTPStatusError("429", request=resp.request, response=resp)
            continue
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return schema.model_validate_json(content)
    raise RuntimeError("Groq rate limit not cleared after retries") from last_exc


def web_search(query: str, max_uses: int = 5) -> str:
    """Run a web-search-grounded Claude query and return the answer text.

    Anthropic-only (server-side web search tool). Raises for other providers so
    the research step falls back to a knowledge-only path.
    """
    if provider() != "anthropic":
        raise RuntimeError("web search requires the Anthropic provider")
    client = _get_client()
    response = client.messages.create(
        model=config.LLM_MODEL,
        max_tokens=config.LLM_MAX_TOKENS,
        tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": max_uses}],
        messages=[{"role": "user", "content": query}],
    )
    parts = [b.text for b in response.content if getattr(b, "type", None) == "text"]
    return "\n".join(parts).strip()
