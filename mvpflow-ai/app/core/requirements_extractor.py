from __future__ import annotations
import logging
from app.models import RequirementExtraction
from app.utils.text_utils import normalize_text, contains_any
from app.llm.client import llm_enabled, generate_structured
from app.constants import (
    DOMAIN_CONFIGS,
    DEFAULT_DOMAIN_CONFIG,
    PRIVACY_KEYWORDS,
    RECOMMENDED_NOTES_LENGTH,
)

logger = logging.getLogger(__name__)

_EXTRACTION_SYSTEM = (
    "You are a product discovery analyst. Read the founder/customer notes and "
    "extract a structured requirements summary for the given business domain. "
    "Ground every field in the actual notes; do not invent facts that are not "
    "implied. Identify the core operational problem, the specific target user, "
    "the concrete customer pain points, the domain/technical/regulatory risks, "
    "and the key assumptions a builder should validate before committing to a "
    "build. Flag privacy- or safety-sensitive handling explicitly in risks."
)


def _extract_with_llm(text: str, domain: str) -> RequirementExtraction:
    """Extract requirements using a live Claude call."""
    prompt = (
        f"Business domain: {domain}\n\n"
        f"Founder/customer notes:\n\"\"\"\n{text}\n\"\"\"\n\n"
        "Return the problem, target_user, pain_points, risks, and assumptions."
    )
    return generate_structured(_EXTRACTION_SYSTEM, prompt, RequirementExtraction)


def extract_requirements(notes: str, domain: str = "restaurant") -> RequirementExtraction:
    """Extract problem, user, pain points, risks, and assumptions from founder notes.

    Identifies the core business problem, target user segment, customer pain points,
    technical/domain risks, and key assumptions that guide MVP scope definition.

    When LLM integration is enabled (see :func:`app.llm.client.llm_enabled`) this
    uses a live Claude call grounded in the actual notes; otherwise it falls back
    to the deterministic domain templates.

    Args:
        notes: Raw founder or customer notes (min 10 characters).
        domain: Business domain for domain-specific evaluation (default: "restaurant").

    Returns:
        RequirementExtraction with problem, target_user, pain_points, risks, assumptions.

    Raises:
        ValueError: If notes are too short or empty after normalization.
    """
    text = normalize_text(notes)
    if not text:
        raise ValueError("Notes cannot be empty after normalization")

    if llm_enabled():
        try:
            return _extract_with_llm(text, domain)
        except Exception as e:  # fall back to deterministic templates on any failure
            logger.warning("LLM requirements extraction failed, using template: %s", e)

    lower = text.lower()
    
    # Get domain-specific config or use default
    domain_lower = domain.lower()
    config = DOMAIN_CONFIGS.get(domain_lower, DEFAULT_DOMAIN_CONFIG)
    
    # Extract basic fields from config
    problem = config["problem"]
    target_user = config["target_user"]
    pain_points = list(config["pain_points"])  # AI: Make copy to allow mutations
    risks = list(config["risks"])  # AI: Make copy to allow mutations
    
    # AI: Add assumptions from base template
    assumptions = [
        "The founder has at least a few customer conversations or notes.",
        "The first version should be reviewed by a human before customer-facing use.",
        "The MVP should avoid complex integrations until the core workflow is validated.",
    ]
    
    # AI: Domain-specific risk handling - check for privacy/regulated content
    if contains_any(lower, PRIVACY_KEYWORDS):
        risks.append("Privacy or regulated-domain handling may be required before production use.")
    
    # AI: Warn if notes are short and may lack sufficient customer evidence
    if len(text) < RECOMMENDED_NOTES_LENGTH:
        assumptions.append("The notes are short; request more customer evidence before major build decisions.")
    
    return RequirementExtraction(
        problem=problem,
        target_user=target_user,
        pain_points=pain_points,
        risks=risks,
        assumptions=assumptions,
    )
