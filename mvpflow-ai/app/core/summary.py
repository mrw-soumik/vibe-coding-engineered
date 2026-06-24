from __future__ import annotations
from typing import List
from app.models import (
    RequirementExtraction,
    MVPPlan,
    ArchitecturePlan,
    JiraTicket,
    EvaluationReport,
)


def create_final_summary(
    req: RequirementExtraction,
    plan: MVPPlan,
    arch: ArchitecturePlan,
    tickets: List[JiraTicket],
    evaluation: EvaluationReport,
) -> str:
    """Create founder-ready delivery summary.
    
    Generates a concise Markdown summary that can be shared with team members,
    mentors, or investors. Includes problem, MVP scope, risks, architecture,
    execution backlog, evaluation results, and next steps.
    
    Args:
        req: Extracted requirements from founder notes.
        plan: MVP plan with scope and success criteria.
        arch: System architecture plan.
        tickets: Generated Jira tickets for execution.
        evaluation: Evaluation report with scores and recommendation.
        
    Returns:
        Markdown-formatted summary ready for sharing or inclusion in docs.
    """
    ticket_lines = "\n".join([f"- {t.key}: {t.title}" for t in tickets])
    scope_lines = "\n".join([f"- {item}" for item in plan.in_scope])
    risk_lines = "\n".join([f"- {risk}" for risk in req.risks])
    
    return f"""# MVPFlow AI Delivery Summary

## Problem
{req.problem}

## Target User
{req.target_user}

## Recommended MVP
{plan.recommended_mvp}

## MVP Scope
{scope_lines}

## Key Risks
{risk_lines}

## Architecture Pattern
{arch.pattern}

## Jira Backlog
{ticket_lines}

## Evaluation Result
Overall score: {evaluation.overall_score}/5

Recommendation: {evaluation.recommendation}

## Next Steps
1. Review generated tickets with the founder/team.
2. Select the first implementation ticket.
3. Build through a GitHub branch and PR.
4. Run tests and domain-specific evaluation.
5. Update the final summary after each milestone.
""".strip()
