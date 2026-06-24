# MVPFlow AI Founder Engineering Skill

## Purpose

Guide a startup founder or AI engineer through a professional workflow from messy customer notes to MVP scope, architecture, Jira tickets, implementation, evaluation, and final documentation.

## Core Principles

- Start with the customer problem, not the app idea.
- Research and define requirements before coding.
- Keep the MVP small, useful, and testable.
- Create architecture before implementation.
- Break work into Jira-ready tickets with acceptance criteria.
- Work one ticket at a time.
- Link implementation work to GitHub branches and PRs.
- Evaluate both output quality and domain fit.
- Add system reliability checks before calling work complete.
- Use human approval before high-impact actions.

## Workflow

1. Understand founder/customer notes.
2. Extract the real problem, target user, pain points, assumptions, and risks.
3. Compare possible solution options.
4. Select the smallest useful MVP.
5. Define in-scope and out-of-scope features.
6. Create a simple solution architecture.
7. Generate Jira tickets with acceptance criteria and definition of done.
8. Implement ticket by ticket.
9. Link GitHub branches, commits, and PRs to tickets.
10. Evaluate content quality, domain fit, and system reliability.
11. Fix weaknesses and document improvements.
12. Create a final delivery summary.

## Evaluation Rules

Use three evaluation layers:

### Content Quality
Check problem accuracy, target user accuracy, pain point coverage, MVP scope quality, ticket actionability, acceptance criteria quality, and final summary quality.

### Domain Fit
Check whether the output is appropriate for the specific business/domain. For restaurants, this includes allergy risk, menu accuracy, missing information handling, owner review, and practical usefulness.

### System Reliability
Check JSON validity, required field completeness, test pass rate, edge case handling, consistency, safe error handling, latency, and cost.

## Ticket Rules

Each ticket must include:

- Title
- User story
- Description
- Acceptance criteria
- Priority
- Definition of done
- Suggested branch name
- Test or evaluation requirement

## Coding Rules

- Keep code simple and readable.
- Do not modify unrelated files.
- Do not hard-code secrets.
- Use environment variables for credentials.
- Add tests or evaluation checks for behavior changes.
- Update README and docs when usage changes.

## Final Output After Each Milestone

Provide:

1. What was completed
2. Why it matters
3. Files changed
4. Test/evaluation result
5. Known limitations
6. Next step
