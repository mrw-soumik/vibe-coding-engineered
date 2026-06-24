from __future__ import annotations
import logging
from typing import List
from pydantic import BaseModel
from app.models import (
    RequirementExtraction,
    MVPPlan,
    ArchitecturePlan,
    JiraTicket,
    EvaluationMetric,
    EvaluationReport,
)
from app.llm.client import llm_enabled, generate_structured
from app.constants import (
    DOMAIN_CONFIGS,
    DEFAULT_DOMAIN_CONFIG,
    CONTENT_QUALITY_METRICS,
    SYSTEM_RELIABILITY_METRICS,
    EVALUATION_RECOMMENDATION,
)

logger = logging.getLogger(__name__)


class _LLMMetric(BaseModel):
    """One LLM-produced evaluation metric (overall score is computed in code)."""
    name: str
    score: float
    notes: str


class _LLMEvaluation(BaseModel):
    """Schema for the LLM evaluation response, excluding the derived overall score."""
    content_quality: List[_LLMMetric]
    domain_fit: List[_LLMMetric]
    system_reliability: List[_LLMMetric]
    recommendation: str


_EVALUATION_SYSTEM = (
    "You are a critical product reviewer. Score the generated MVP package across "
    "three layers, each metric 1-5 (1=poor, 5=excellent), and justify each score "
    "in one sentence grounded in the artifacts shown. Be discerning: do not give "
    "5s by default. The three layers are:\n"
    "1. content_quality - is the output useful, complete, and accurate?\n"
    "2. domain_fit - does it fit this business domain and handle its specific "
    "risks (e.g. safety, privacy, regulation)?\n"
    "3. system_reliability - is the scope coherent, testable, and free of "
    "overbuild? Provide 3-6 metrics per layer."
)


def _metric(name: str, score: float, notes: str) -> EvaluationMetric:
    """Create an evaluation metric."""
    return EvaluationMetric(name=name, score=score, notes=notes)


def _overall(*groups: List[EvaluationMetric]) -> float:
    """Average all metric scores across the given groups, rounded to 2 dp."""
    scores = [m.score for group in groups for m in group]
    return round(sum(scores) / len(scores), 2) if scores else 0.0


def _evaluate_with_llm(
    req: RequirementExtraction,
    plan: MVPPlan,
    arch: ArchitecturePlan,
    tickets: List[JiraTicket],
    domain: str,
) -> EvaluationReport:
    """Score the produced artifacts with a live Claude call."""
    prompt = (
        f"Business domain: {domain}\n\n"
        f"Problem: {req.problem}\n"
        f"Target user: {req.target_user}\n"
        f"Pain points: {req.pain_points}\n"
        f"Risks: {req.risks}\n\n"
        f"Recommended MVP: {plan.recommended_mvp}\n"
        f"In scope: {plan.in_scope}\n"
        f"Out of scope: {plan.out_of_scope}\n"
        f"Success criteria: {plan.success_criteria}\n\n"
        f"Architecture pattern: {arch.pattern}\n"
        f"Jira tickets: {[t.title for t in tickets]}\n\n"
        "Score content_quality, domain_fit, and system_reliability, and give an "
        "overall recommendation."
    )
    result = generate_structured(_EVALUATION_SYSTEM, prompt, _LLMEvaluation)

    content_quality = [_metric(m.name, m.score, m.notes) for m in result.content_quality]
    domain_fit = [_metric(m.name, m.score, m.notes) for m in result.domain_fit]
    system_reliability = [_metric(m.name, m.score, m.notes) for m in result.system_reliability]

    return EvaluationReport(
        content_quality=content_quality,
        domain_fit=domain_fit,
        system_reliability=system_reliability,
        overall_score=_overall(content_quality, domain_fit, system_reliability),
        recommendation=result.recommendation,
    )


def evaluate_workflow(
    req: RequirementExtraction,
    plan: MVPPlan,
    arch: ArchitecturePlan,
    tickets: List[JiraTicket],
    domain: str = "restaurant",
) -> EvaluationReport:
    """Evaluate workflow output across three dimensions.
    
    Generates scores and recommendations for:
    - Content Quality: Is output useful and complete?
    - Domain Fit: Does output make sense for the selected business?
    - System Reliability: Does workflow behave consistently and safely?
    
    Overall score is the average of all metric scores across all three layers.
    
    Args:
        req: Extracted requirements from founder notes.
        plan: MVP plan with scope and success criteria.
        arch: System architecture plan.
        tickets: Generated Jira tickets.
        domain: Business domain for domain-specific evaluation (default: "restaurant").
        
    Returns:
        EvaluationReport with metrics, overall score, and recommendation.
    """
    if llm_enabled():
        try:
            return _evaluate_with_llm(req, plan, arch, tickets, domain)
        except Exception as e:  # fall back to deterministic scoring on any failure
            logger.warning("LLM evaluation failed, using template scores: %s", e)

    # Content quality metrics (same for all domains)
    content_quality = [
        _metric(name, score, notes)
        for name, score, notes in CONTENT_QUALITY_METRICS
    ]
    
    # Domain-specific fit metrics
    domain_lower = domain.lower()
    config = DOMAIN_CONFIGS.get(domain_lower, DEFAULT_DOMAIN_CONFIG)
    domain_fit_tuples = config.get("domain_fit_metrics", [])
    
    domain_fit = [
        _metric(name, score, notes)
        for name, score, notes in domain_fit_tuples
    ]
    
    # System reliability metrics (same for all domains)
    system_reliability = [
        _metric(name, score, notes)
        for name, score, notes in SYSTEM_RELIABILITY_METRICS
    ]
    
    # Calculate overall score as average of all metrics
    overall = _overall(content_quality, domain_fit, system_reliability)

    recommendation = EVALUATION_RECOMMENDATION
    
    return EvaluationReport(
        content_quality=content_quality,
        domain_fit=domain_fit,
        system_reliability=system_reliability,
        overall_score=overall,
        recommendation=recommendation,
    )
