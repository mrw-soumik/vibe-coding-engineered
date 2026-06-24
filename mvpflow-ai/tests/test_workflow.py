"""Tests for MVPFlow AI workflow.

Tests cover:
- Happy path: valid notes generate all required sections
- Edge cases: short notes, domain-specific behavior
- Error handling: empty/invalid input
- API models: validation and serialization
"""
import pytest
from app.core.workflow import run_workflow
from app.core.requirements_extractor import extract_requirements
from app.models import FounderNotesRequest


@pytest.fixture
def restaurant_notes() -> str:
    """Fixture: Sample restaurant founder notes."""
    return open("examples/restaurant_founder_notes.txt", encoding="utf-8").read()


@pytest.fixture
def short_notes() -> str:
    """Fixture: Short notes for edge case testing."""
    return "We have an idea for a restaurant assistant."


def test_workflow_generates_required_sections(restaurant_notes: str):
    """Test that workflow generates all required output sections."""
    result = run_workflow(restaurant_notes, "restaurant")
    
    # All major sections must be present
    assert result.requirements.problem
    assert result.mvp_plan.recommended_mvp
    assert result.architecture.components
    assert len(result.jira_tickets) >= 5
    assert result.evaluation.overall_score >= 4
    assert "MVPFlow AI Delivery Summary" in result.final_summary


def test_restaurant_domain_flags_allergy_risk(restaurant_notes: str):
    """Test that restaurant domain specifically flags allergy/menu risks."""
    result = run_workflow(restaurant_notes, "restaurant")
    
    # Allergy risk should be mentioned in requirements
    combined_risks = " ".join(result.requirements.risks).lower()
    assert "allergy" in combined_risks
    
    # Domain fit evaluation should include allergy handling
    assert any(
        "Allergy" in m.name or "allergy" in m.notes.lower()
        for m in result.evaluation.domain_fit
    )


def test_jira_tickets_are_actionable(restaurant_notes: str):
    """Test that Jira tickets have all required fields for implementation."""
    result = run_workflow(restaurant_notes, "restaurant")
    
    for ticket in result.jira_tickets:
        # Key must follow pattern MVP-XXX
        assert ticket.key.startswith("MVP-")
        
        # User story must be in standard format
        assert ticket.user_story.startswith("As a founder")
        
        # Must have acceptance criteria
        assert len(ticket.acceptance_criteria) >= 3
        
        # Suggested branch must be valid GitHub branch format
        assert ticket.suggested_branch.startswith("feature/")
        
        # Must have definition of done
        assert len(ticket.definition_of_done) >= 3


def test_evaluation_has_three_layers(restaurant_notes: str):
    """Test that evaluation covers all three quality dimensions."""
    result = run_workflow(restaurant_notes)
    
    # Three evaluation layers
    assert result.evaluation.content_quality
    assert result.evaluation.domain_fit
    assert result.evaluation.system_reliability
    
    # Each layer has meaningful metrics
    assert len(result.evaluation.content_quality) >= 3
    assert len(result.evaluation.domain_fit) >= 3
    assert len(result.evaluation.system_reliability) >= 3


def test_short_notes_add_assumption(short_notes: str):
    """Test that short notes trigger warning assumptions."""
    result = run_workflow(short_notes)
    
    assumptions = " ".join(result.requirements.assumptions).lower()
    
    # Should warn about short notes
    assert "short" in assumptions or "more customer evidence" in assumptions


def test_api_models_serializable(restaurant_notes: str):
    """Test that all models serialize to JSON correctly."""
    result = run_workflow(restaurant_notes)
    
    # Should be able to dump to dict (needed for JSON serialization)
    dumped = result.model_dump()
    assert "requirements" in dumped
    assert "evaluation" in dumped
    assert isinstance(dumped["jira_tickets"], list)
    
    # Nested models should also serialize
    assert "content_quality" in dumped["evaluation"]


def test_invalid_input_raises_error():
    """Test that invalid input raises appropriate error."""
    with pytest.raises(ValueError):
        extract_requirements("")  # Empty notes should fail


def test_privacy_keywords_trigger_risk_flag():
    """Test that privacy-related keywords trigger special handling."""
    notes = "We need to store patient health data."
    result = run_workflow(notes)
    
    # Should have added privacy risk
    combined_risks = " ".join(result.requirements.risks).lower()
    assert "privacy" in combined_risks or "regulated" in combined_risks


def test_founder_notes_request_validation():
    """Test FounderNotesRequest model validation."""
    # Valid request should work
    valid = FounderNotesRequest(notes="Good enough test notes here", domain="restaurant")
    assert valid.notes
    
    # Too short should fail
    with pytest.raises(ValueError):
        FounderNotesRequest(notes="too short")


def test_domain_adaptability():
    """Test that workflow adapts to different domains."""
    notes = "General business notes for a SaaS product."
    
    # Should work for custom domain
    result = run_workflow(notes, domain="saas")
    assert result.mvp_plan.recommended_mvp
    
    # Restaurant domain should be different
    result_restaurant = run_workflow(notes, domain="restaurant")
    assert "restaurant" in result_restaurant.mvp_plan.recommended_mvp.lower()


def test_architecture_includes_next_steps(restaurant_notes: str):
    """Test that architecture includes production roadmap."""
    result = run_workflow(restaurant_notes)
    
    arch = result.architecture
    
    # Should include components
    assert len(arch.components) > 0
    
    # Should include data flow
    assert len(arch.data_flow) > 0
    
    # Should include next production layers
    assert len(arch.next_production_layers) > 0
    
    # Should mention Claude/Codex or MCP
    next_layers_text = " ".join(arch.next_production_layers).lower()
    assert "claude" in next_layers_text or "mcp" in next_layers_text


def test_summary_is_founder_ready(restaurant_notes: str):
    """Test that final summary is in founder-friendly format."""
    result = run_workflow(restaurant_notes)
    summary = result.final_summary
    
    # Must be Markdown
    assert "# MVPFlow AI Delivery Summary" in summary
    
    # Must include all key sections
    assert "## Problem" in summary
    assert "## Target User" in summary
    assert "## MVP Scope" in summary
    assert "## Evaluation Result" in summary
    assert "## Next Steps" in summary


def test_overall_score_calculation(restaurant_notes: str):
    """Test that overall score is correctly calculated."""
    result = run_workflow(restaurant_notes)
    
    evaluation = result.evaluation
    
    # Calculate expected overall score
    all_metrics = (
        evaluation.content_quality
        + evaluation.domain_fit
        + evaluation.system_reliability
    )
    all_scores = [m.score for m in all_metrics]
    expected_score = round(sum(all_scores) / len(all_scores), 2)
    
    # Should match calculated score
    assert evaluation.overall_score == expected_score
