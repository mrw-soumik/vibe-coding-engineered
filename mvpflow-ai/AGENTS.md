# AGENTS.md

## Project Goal

This repository demonstrates an AI-assisted MVP execution workflow for startup founders. The goal is not to overbuild a production platform; the goal is to show a clean, repeatable engineering process from customer notes to evaluation and final summary.

## Instructions for Coding Agents

- Follow the current ticket or task only.
- Keep changes small and reviewable.
- Do not implement unrelated features.
- Prefer deterministic, testable behavior in the workshop version.
- Do not commit secrets, credentials, tokens, or private data.
- Add or update tests when changing behavior.
- Update documentation when changing setup, usage, architecture, or evaluation.
- Keep founder-facing language simple and clear.

## Review Checklist

When reviewing a PR, check:

- Does the change match the ticket?
- Are tests added or updated?
- Does `pytest -q` pass?
- Are docs updated if needed?
- Are there any hard-coded secrets?
- Is the output useful for founders?
- Is the domain-specific risk handling preserved?
- Are acceptance criteria satisfied?

## PR Template Expectations

Every PR should include:

- Jira/ticket reference
- Summary of changes
- Files changed
- Test command and result
- Evaluation result
- Known limitations
- Next steps
