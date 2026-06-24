from __future__ import annotations
import logging
from app.models import WorkflowResponse
from app.core.requirements_extractor import extract_requirements
from app.core.research import conduct_research
from app.core.solutions import compare_solutions
from app.core.mvp_scope import create_mvp_plan
from app.core.architecture import create_architecture
from app.core.jira_ticket_generator import generate_jira_tickets
from app.core.evaluation import evaluate_workflow
from app.core.summary import create_final_summary

logger = logging.getLogger(__name__)


def run_workflow(notes: str, domain: str = "restaurant") -> WorkflowResponse:
    """Execute the complete MVPFlow AI workflow.
    
    Transforms founder/customer notes into a structured MVP execution package:
    requirements extraction → MVP scope → architecture → Jira tickets → 
    evaluation → final summary.
    
    Each step is logged for debugging and auditing purposes.
    
    Args:
        notes: Raw founder or customer notes.
        domain: Business domain for domain-specific evaluation (default: "restaurant").
        
    Returns:
        WorkflowResponse with requirements, MVP plan, architecture, tickets, 
        evaluation, and final summary.
        
    Raises:
        ValueError: If notes fail validation or processing fails at any step.
    """
    logger.info(f"Starting workflow for domain: {domain}")
    logger.debug(f"Input notes length: {len(notes)} characters")
    
    try:
        # Extract requirements
        logger.debug("Step 1: Extracting requirements...")
        req = extract_requirements(notes, domain)
        logger.info(f"Requirements extracted. Problem: {req.problem[:50]}...")

        # Research the domain (LLM-only; None in deterministic mode)
        logger.debug("Step 2: Researching domain...")
        research = conduct_research(notes, domain)
        if research:
            logger.info(f"Research complete: {len(research.key_insights)} insights, {len(research.sources)} sources")

        # Compare solution options and recommend the smallest useful MVP (LLM-only)
        logger.debug("Step 3: Comparing solution options...")
        solutions = compare_solutions(req, research, domain)
        if solutions:
            logger.info(f"Solution options compared. Recommended: {solutions.recommended}")

        # Create MVP plan
        logger.debug("Step 4: Creating MVP plan...")
        plan = create_mvp_plan(req, domain)
        logger.info(f"MVP plan created: {plan.recommended_mvp[:50]}...")

        # Create architecture
        logger.debug("Step 5: Creating architecture...")
        arch = create_architecture(plan)
        logger.info(f"Architecture defined: {arch.pattern}")

        # Generate Jira tickets (grounded in requirements when LLM is on)
        logger.debug("Step 6: Generating Jira tickets...")
        tickets = generate_jira_tickets(plan, req)
        logger.info(f"Generated {len(tickets)} Jira tickets")

        # Evaluate workflow
        logger.debug("Step 7: Evaluating workflow...")
        evaluation = evaluate_workflow(req, plan, arch, tickets, domain)
        logger.info(f"Evaluation complete. Overall score: {evaluation.overall_score}/5")

        # Create final summary
        logger.debug("Step 8: Creating final summary...")
        summary = create_final_summary(req, plan, arch, tickets, evaluation)
        logger.info("Final summary created")

        logger.info("Workflow completed successfully")

        return WorkflowResponse(
            requirements=req,
            research=research,
            solution_options=solutions,
            mvp_plan=plan,
            architecture=arch,
            jira_tickets=tickets,
            evaluation=evaluation,
            final_summary=summary,
        )
    
    except ValueError as e:
        logger.error(f"Validation error in workflow: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in workflow: {str(e)}", exc_info=True)
        raise RuntimeError(f"Workflow execution failed: {str(e)}") from e
