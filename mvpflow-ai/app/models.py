from __future__ import annotations
from typing import List, Dict, Any, Optional
from html import escape
from pydantic import BaseModel, Field, field_validator
from app.constants import MIN_NOTES_LENGTH, MAX_NOTES_LENGTH

class FounderNotesRequest(BaseModel):
    """Request model for the workflow API endpoint.
    
    Accepts raw founder notes and an optional domain for domain-specific evaluation.
    Validates and sanitizes input to prevent injection attacks.
    """
    notes: str = Field(..., min_length=MIN_NOTES_LENGTH, max_length=MAX_NOTES_LENGTH, 
                       description="Messy founder notes or customer feedback (10-50000 chars)")
    domain: str = Field(default="restaurant", description="Business domain used for domain-fit evaluation")
    
    @field_validator('notes')
    @classmethod
    def sanitize_notes(cls, v: str) -> str:
        """Sanitize input to remove suspicious patterns."""
        if not isinstance(v, str):
            raise ValueError("Notes must be a string")
        # Remove script tags and javascript patterns
        if any(pattern in v.lower() for pattern in ['<script', 'javascript:', 'onerror=', 'onclick=']):
            raise ValueError("Invalid content detected in notes")
        return escape(v.strip())

class RequirementExtraction(BaseModel):
    """Requirements extracted from founder notes.
    
    Identifies the core problem, target user, pain points, risks, and assumptions
    that guide MVP scope definition.
    """
    problem: str
    target_user: str
    pain_points: List[str]
    risks: List[str]
    assumptions: List[str]

class MVPPlan(BaseModel):
    """Minimum Viable Product scope and strategy.
    
    Defines what is included in the first version, what is deferred,
    and success criteria for determining if the MVP succeeds.
    """
    recommended_mvp: str
    in_scope: List[str]
    out_of_scope: List[str]
    success_criteria: List[str]

class ArchitecturePlan(BaseModel):
    """System architecture and implementation strategy.
    
    Describes components, data flow, and recommended production layers
    for transitioning from prototype to production.
    """
    pattern: str
    components: List[Dict[str, str]]
    data_flow: List[str]
    next_production_layers: List[str]

class JiraTicket(BaseModel):
    """Actionable work item for implementation.
    
    Represents a single feature or task that can be implemented as a GitHub branch
    and pull request. Includes acceptance criteria and definition of done.
    """
    key: str
    title: str
    user_story: str
    description: str
    acceptance_criteria: List[str]
    priority: str
    definition_of_done: List[str]
    suggested_branch: str
    story_points: Optional[float] = None

class ResearchFindings(BaseModel):
    """Domain/market research grounding the planning (optionally web-sourced)."""
    summary: str
    key_insights: List[str]
    alternatives: List[str]        # existing tools / how the problem is solved today
    domain_risks: List[str]        # safety, regulatory, or domain-specific risks
    best_practices: List[str]      # industry best practices relevant to the build
    sources: List[str] = []        # URLs when web search was used

class SolutionOption(BaseModel):
    """One candidate solution at a given level of ambition."""
    name: str
    description: str
    effort: str                    # e.g. "Small", "Medium", "Large"
    pros: List[str]
    cons: List[str]

class SolutionComparison(BaseModel):
    """Three solution options with a recommended (smallest useful) choice."""
    options: List[SolutionOption]
    recommended: str               # name of the recommended option
    rationale: str

class TicketList(BaseModel):
    """Wrapper so the LLM can return a list of tickets as structured output."""
    tickets: List[JiraTicket]

class EvaluationMetric(BaseModel):
    """Single evaluation metric with score and rationale.
    
    Part of a three-layer evaluation: content quality, domain fit, system reliability.
    """
    name: str
    score: float
    max_score: float = 5.0
    notes: str

class EvaluationReport(BaseModel):
    """Comprehensive workflow evaluation across three dimensions.
    
    Evaluates the generated output and workflow behavior in:
    - Content Quality: Is output useful and complete?
    - Domain Fit: Does output fit the selected business domain?
    - System Reliability: Does workflow behave consistently and safely?
    
    Overall score is the average of all metric scores.
    """
    content_quality: List[EvaluationMetric]
    domain_fit: List[EvaluationMetric]
    system_reliability: List[EvaluationMetric]
    overall_score: float
    recommendation: str

class WorkflowResponse(BaseModel):
    """Complete workflow output: requirements through final summary.
    
    Contains all artifacts produced by the workflow: extracted requirements,
    MVP plan, architecture, Jira tickets, evaluation metrics, and founder-ready summary.
    """
    requirements: RequirementExtraction
    research: Optional[ResearchFindings] = None
    solution_options: Optional[SolutionComparison] = None
    mvp_plan: MVPPlan
    architecture: ArchitecturePlan
    jira_tickets: List[JiraTicket]
    evaluation: EvaluationReport
    final_summary: str
