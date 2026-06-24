"""Solution-options step for MVPFlow AI.

Implements the PPT's founder-template step: propose three solution options
(small MVP, more advanced workflow, full product vision), weigh them, and
recommend the **smallest useful** one to carry into MVP scoping.

Only runs when the Claude integration is enabled.
"""
from __future__ import annotations

import logging
from typing import Optional

from app.llm.client import llm_enabled, generate_structured
from app.models import RequirementExtraction, ResearchFindings, SolutionComparison

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are a pragmatic product strategist. Given the requirements (and any "
    "research), propose exactly THREE solution options at increasing ambition: "
    "(1) a small, human-in-the-loop MVP, (2) a more advanced workflow, (3) the "
    "full product vision. For each give effort (Small/Medium/Large), pros, and "
    "cons. Then recommend the SMALLEST option that is genuinely useful and safe, "
    "and explain why. Favor shipping something real and reviewable over scope."
)


def compare_solutions(
    req: RequirementExtraction,
    research: Optional[ResearchFindings],
    domain: str,
) -> Optional[SolutionComparison]:
    """Generate and rank three solution options. Returns None if LLM disabled."""
    if not llm_enabled():
        return None

    research_block = ""
    if research:
        research_block = (
            "Research insights:\n- " + "\n- ".join(research.key_insights)
            + "\nExisting alternatives:\n- " + "\n- ".join(research.alternatives)
        )

    prompt = (
        f"Domain: {domain}\n"
        f"Problem: {req.problem}\n"
        f"Target user: {req.target_user}\n"
        f"Pain points:\n- " + "\n- ".join(req.pain_points) + "\n\n"
        f"{research_block}\n\n"
        "Return options (exactly 3), recommended (the option name), and rationale."
    )
    try:
        return generate_structured(_SYSTEM, prompt, SolutionComparison)
    except Exception as e:
        logger.warning("Solution-options step failed, continuing without it: %s", e)
        return None
