# MVPFlow AI Delivery Summary

## Problem
Restaurant owners spend too much time answering repeated customer questions across scattered channels.

## Target User
Small restaurant owners and managers who handle customer questions manually.

## Recommended MVP
A human-reviewed AI FAQ assistant for restaurant owners.

## MVP Scope
- Paste or upload restaurant information.
- Generate editable FAQ answers from the restaurant information.
- Answer sample customer questions in a test console.
- Flag risky allergy, dietary, or missing-information questions for owner review.
- Create evaluation test cases for common and risky questions.

## Key Risks
- Allergy or dietary answers may be risky if menu information is incomplete.
- Outdated menu, delivery, or reservation information could mislead customers.
- Fully automated replies should not be enabled before owner review.

## Architecture Pattern
Human-in-the-loop AI workflow MVP

## Jira Backlog
- MVP-001: Define restaurant FAQ MVP scope
- MVP-002: Build founder notes input workflow
- MVP-003: Generate MVP analysis output
- MVP-004: Generate Jira-style execution tickets
- MVP-005: Add evaluation metrics
- MVP-006: Create final founder summary

## Evaluation Result
Overall score: 4.66/5

Recommendation: Workshop-ready. Use as a deterministic reference system, then add live Claude/Codex, Jira, GitHub, and MCP integrations as the advanced layer.

## Next Steps
1. Review generated tickets with the founder/team.
2. Select the first implementation ticket.
3. Build through a GitHub branch and PR.
4. Run tests and domain-specific evaluation.
5. Update the final summary after each milestone.