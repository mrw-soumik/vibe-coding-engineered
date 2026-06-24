"""Domain/market research step for MVPFlow AI.

Grounds the planning in real domain context before scoping. When web search is
enabled and available, it gathers live findings; otherwise it falls back to a
knowledge-only analysis. Returns structured :class:`ResearchFindings`.

This step only runs when the Claude integration is enabled; the deterministic
workflow skips it (research is inherently generative, not template-able).
"""
from __future__ import annotations

import logging
from typing import Optional

from app.config import config
from app.llm.client import llm_enabled, generate_structured, web_search
from app.models import ResearchFindings

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are a startup market/domain researcher. Given founder notes and a "
    "domain, produce grounded research that will inform MVP planning: the real "
    "problem context, how it's solved today (existing tools/alternatives), "
    "domain-specific risks (safety, privacy, regulation), and the industry best "
    "practices a team should follow. Be concrete and domain-appropriate; do not "
    "invent statistics. If web findings are provided, ground your answer in them "
    "and include the source URLs."
)


def research_enabled() -> bool:
    return llm_enabled()


def conduct_research(notes: str, domain: str) -> Optional[ResearchFindings]:
    """Research the domain/problem. Returns None if the LLM is disabled."""
    if not llm_enabled():
        return None

    web_text = ""
    if config.USE_WEB_SEARCH:
        try:
            web_text = web_search(
                f"Research the '{domain}' domain for building an MVP that addresses: "
                f"{notes[:600]}. Cover existing solutions, domain risks, and best practices."
            )
        except Exception as e:  # web search unavailable/unsupported -> knowledge-only
            logger.warning("Web search unavailable, using knowledge-only research: %s", e)

    prompt = (
        f"Domain: {domain}\n\nFounder/customer notes:\n\"\"\"\n{notes}\n\"\"\"\n\n"
        f"Web findings (may be empty):\n\"\"\"\n{web_text or '(none)'}\n\"\"\"\n\n"
        "Return summary, key_insights, alternatives, domain_risks, best_practices, sources."
    )
    try:
        return generate_structured(_SYSTEM, prompt, ResearchFindings)
    except Exception as e:
        logger.warning("Research step failed, continuing without it: %s", e)
        return None
