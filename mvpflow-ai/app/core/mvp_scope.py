from __future__ import annotations
import logging
from app.models import RequirementExtraction, MVPPlan
from app.llm.client import llm_enabled, generate_structured
from app.constants import DOMAIN_CONFIGS, DEFAULT_DOMAIN_CONFIG

logger = logging.getLogger(__name__)

_MVP_SYSTEM = (
    "You are a pragmatic startup product lead. Given the extracted requirements, "
    "define the smallest genuinely useful MVP. Favor a human-in-the-loop, "
    "review-before-publish design over full automation. Be explicit about what is "
    "deliberately out of scope so the team avoids overbuilding, and write success "
    "criteria that are observable and testable."
)


def _mvp_with_llm(req: RequirementExtraction, domain: str) -> MVPPlan:
    """Create an MVP plan using a live Claude call grounded in the requirements."""
    prompt = (
        f"Business domain: {domain}\n\n"
        f"Problem: {req.problem}\n"
        f"Target user: {req.target_user}\n"
        f"Pain points:\n- " + "\n- ".join(req.pain_points) + "\n"
        f"Risks:\n- " + "\n- ".join(req.risks) + "\n\n"
        "Return recommended_mvp, in_scope, out_of_scope, and success_criteria."
    )
    return generate_structured(_MVP_SYSTEM, prompt, MVPPlan)


def create_mvp_plan(req: RequirementExtraction, domain: str = "restaurant") -> MVPPlan:
    """Create MVP scope and strategy from requirements.

    Defines what is included in the first version (in-scope), what is deferred
    (out-of-scope), and success criteria for determining if the MVP succeeds.

    When LLM integration is enabled this derives the scope from the actual
    requirements via a live Claude call; otherwise it uses domain templates.

    Args:
        req: Extracted requirements from founder notes.
        domain: Business domain for domain-specific MVP planning (default: "restaurant").

    Returns:
        MVPPlan with recommended MVP, in-scope features, out-of-scope features,
        and success criteria.
    """
    if llm_enabled():
        try:
            return _mvp_with_llm(req, domain)
        except Exception as e:  # fall back to deterministic templates on any failure
            logger.warning("LLM MVP planning failed, using template: %s", e)

    # Get domain-specific config or use default
    domain_lower = domain.lower()
    cfg = DOMAIN_CONFIGS.get(domain_lower, DEFAULT_DOMAIN_CONFIG)

    # Extract MVP configuration
    mvp_config = cfg["mvp"]

    return MVPPlan(
        recommended_mvp=mvp_config["recommended"],
        in_scope=mvp_config["in_scope"],
        out_of_scope=mvp_config["out_of_scope"],
        success_criteria=mvp_config["success_criteria"],
    )
