from __future__ import annotations
import logging
from typing import List
from pydantic import BaseModel
from app.models import MVPPlan, ArchitecturePlan
from app.llm.client import llm_enabled, generate_structured
from app.constants import (
    ARCHITECTURE_COMPONENTS,
    ARCHITECTURE_DATA_FLOW,
    ARCHITECTURE_NEXT_LAYERS,
)

logger = logging.getLogger(__name__)


class _ArchComponent(BaseModel):
    """Typed component for the LLM schema (ArchitecturePlan uses dicts publicly)."""
    name: str
    purpose: str


class _ArchProposal(BaseModel):
    """LLM-facing schema; converted to ArchitecturePlan. Avoids free-form dicts,
    which structured outputs rejects (additionalProperties must be false)."""
    pattern: str
    components: List[_ArchComponent]
    data_flow: List[str]
    next_production_layers: List[str]

_ARCH_SYSTEM = (
    "You are a software architect designing a SIMPLE, human-in-the-loop MVP "
    "architecture for the given scope. Keep it minimal but production-shaped: "
    "name the pattern, list the core components (each with a one-line purpose), "
    "describe the data flow as ordered steps, and list the next production "
    "layers to add later (auth, storage, monitoring, real integrations). Do not "
    "over-engineer the MVP."
)


def _architecture_with_llm(plan: MVPPlan) -> ArchitecturePlan:
    """Design the architecture from the actual MVP scope via a live Claude call."""
    prompt = (
        f"Recommended MVP: {plan.recommended_mvp}\n"
        f"In scope:\n- " + "\n- ".join(plan.in_scope) + "\n"
        f"Out of scope:\n- " + "\n- ".join(plan.out_of_scope) + "\n\n"
        "Return pattern, components (name + purpose), data_flow, and next_production_layers."
    )
    proposal = generate_structured(_ARCH_SYSTEM, prompt, _ArchProposal)
    return ArchitecturePlan(
        pattern=proposal.pattern,
        components=[{"name": c.name, "purpose": c.purpose} for c in proposal.components],
        data_flow=proposal.data_flow,
        next_production_layers=proposal.next_production_layers,
    )


def create_architecture(plan: MVPPlan) -> ArchitecturePlan:
    """Create system architecture plan from MVP scope.

    When the Claude integration is enabled this designs an architecture tailored
    to the actual scope; otherwise it falls back to the deterministic template.

    Args:
        plan: MVP plan defining scope and boundaries.

    Returns:
        ArchitecturePlan with components, data flow, and next production layers.
    """
    if llm_enabled():
        try:
            return _architecture_with_llm(plan)
        except Exception as e:  # fall back to deterministic template on any failure
            logger.warning("LLM architecture design failed, using template: %s", e)

    return ArchitecturePlan(
        pattern="Human-in-the-loop AI workflow MVP",
        components=ARCHITECTURE_COMPONENTS,
        data_flow=ARCHITECTURE_DATA_FLOW,
        next_production_layers=ARCHITECTURE_NEXT_LAYERS,
    )
