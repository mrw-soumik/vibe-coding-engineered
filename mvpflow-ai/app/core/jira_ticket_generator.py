from __future__ import annotations
import logging
from typing import List, Optional
from app.models import JiraTicket, MVPPlan, RequirementExtraction, TicketList
from app.llm.client import llm_enabled, generate_structured
from app.constants import JIRA_TICKETS, JIRA_STORY_POINTS

logger = logging.getLogger(__name__)

_TICKETS_SYSTEM = (
    "You are a delivery lead converting an MVP scope into a buildable backlog. "
    "Produce 5-7 Jira tickets that, together, deliver the in-scope MVP. Each "
    "ticket must have: key (MVP-001, MVP-002, ...), title, user_story in the form "
    "'As a <user>, I want <capability> so that <benefit>', description, at least 3 "
    "acceptance_criteria, priority (High/Medium/Low), at least 3 definition_of_done "
    "items, a suggested_branch like 'feature/mvp-001-...', and story_points on a "
    "Fibonacci scale (1,2,3,5,8). Order tickets so foundational work comes first. "
    "Tickets must be specific to THIS scope, not generic boilerplate."
)


def _tickets_with_llm(plan: MVPPlan, req: Optional[RequirementExtraction]) -> List[JiraTicket]:
    """Generate tickets tailored to the actual scope via a live Claude call."""
    problem = f"Problem: {req.problem}\nTarget user: {req.target_user}\n\n" if req else ""
    prompt = (
        f"{problem}"
        f"Recommended MVP: {plan.recommended_mvp}\n"
        f"In scope:\n- " + "\n- ".join(plan.in_scope) + "\n"
        f"Success criteria:\n- " + "\n- ".join(plan.success_criteria) + "\n\n"
        "Return a backlog of 5-7 tickets implementing this scope."
    )
    result = generate_structured(_TICKETS_SYSTEM, prompt, TicketList)
    if not result.tickets:
        raise RuntimeError("LLM returned no tickets")
    return result.tickets


def generate_jira_tickets(
    plan: MVPPlan, req: Optional[RequirementExtraction] = None
) -> List[JiraTicket]:
    """Generate Jira-style tickets from the MVP plan.

    When the Claude integration is enabled, tickets are generated from the actual
    scope (so they fit any problem/domain); otherwise it falls back to the
    deterministic template backlog.

    Args:
        plan: MVP plan defining scope and success criteria.
        req: Optional requirements, used to ground LLM-generated tickets.

    Returns:
        List of JiraTicket objects with all necessary fields for implementation.
    """
    if llm_enabled():
        try:
            return _tickets_with_llm(plan, req)
        except Exception as e:  # fall back to deterministic template on any failure
            logger.warning("LLM ticket generation failed, using template: %s", e)

    out = []
    
    # AI: Definition of done is consistent across all tickets
    definition_of_done = [
        "Code or documentation completed",
        "Relevant tests or evaluation checks pass",
        "Output reviewed for founder usefulness",
        "Summary added to Jira/PR notes",
    ]
    
    # Generate tickets from template
    for ticket_template in JIRA_TICKETS:
        key = ticket_template["key"]
        title = ticket_template["title"]
        description = ticket_template["description"]
        acceptance_criteria = ticket_template["acceptance_criteria"]
        priority = ticket_template["priority"]
        
        # Generate user story
        user_story = f"As a founder, I want to {title.lower()} so that I can move from messy feedback to structured MVP execution."
        
        # Generate suggested branch name from ticket key and title
        slug = title.lower().replace(" ", "-").replace("/", "-")
        suggested_branch = f"feature/{key.lower()}-{slug[:40]}"
        
        ticket = JiraTicket(
            key=key,
            title=title,
            user_story=user_story,
            description=description,
            acceptance_criteria=acceptance_criteria,
            priority=priority,
            definition_of_done=definition_of_done,
            suggested_branch=suggested_branch,
            story_points=JIRA_STORY_POINTS.get(key),
        )
        out.append(ticket)
    
    return out
