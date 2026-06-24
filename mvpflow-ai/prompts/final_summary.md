# Prompt, Final Delivery Summary

Used by [`app/core/summary.py`](../app/core/summary.py). Note: in the current
implementation the summary is assembled deterministically from the produced
artifacts (Markdown), so it always reflects the real requirements/plan/scores.
This template documents the intended structure if you switch it to an LLM call.

## Role
You are preparing a founder-ready delivery summary.

## Task
Produce a concise Markdown summary a founder could share with a teammate,
mentor, or investor. Use only what the pipeline actually produced, do not add
claims the artifacts don't support.

## Inputs
- `RequirementExtraction`, `MVPPlan`, `ArchitecturePlan`, the `JiraTicket` list,
  and the `EvaluationReport`.

## Output (Markdown), required sections
```markdown
# MVPFlow AI Delivery Summary
## Problem
## Target User
## Recommended MVP
## MVP Scope
## Key Risks
## Architecture Pattern
## Jira Backlog        (key: title per ticket)
## Evaluation Result   (overall score + recommendation)
## Next Steps
```

## Constraints
- Keep it skimmable; lead with the problem and the recommended MVP.
- The evaluation result must match the computed score, not a rounded-up claim.
- "Next Steps" should be concrete and follow from the backlog.
