"""AI code-draft for MVPFlow AI automation.

Given a Jira ticket, asks Claude for a small, focused candidate implementation
as a set of full-file changes (not diffs, which are fragile to apply). The
orchestrator writes these to a feature branch and opens a **draft** PR for human
review. This never auto-merges and is strictly a proposal.

Requires the Claude integration to be enabled (``ANTHROPIC_API_KEY`` +
``USE_LLM=true``); otherwise :func:`draft_available` is False and the
orchestrator scaffolds a proposal note instead.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from pydantic import BaseModel

from app.llm.client import llm_enabled, generate_structured
from app.models import JiraTicket

logger = logging.getLogger(__name__)

# Hard cap so an AI draft can never wander across the repo unattended.
_MAX_FILES = 6


class FileChange(BaseModel):
    """One proposed file change (full new content, not a diff)."""
    path: str          # repo-relative path, e.g. "mvpflow-ai/app/core/foo.py"
    action: str        # "create" or "modify"
    content: str       # complete intended file contents
    rationale: str


class ImplementationProposal(BaseModel):
    """Claude's candidate implementation for a ticket."""
    summary: str
    files: List[FileChange]
    notes: str


_SYSTEM = (
    "You are a senior engineer drafting a SMALL, focused candidate change for one "
    "ticket in the MVPFlow AI repo (a Python/FastAPI project under the "
    "'mvpflow-ai/' directory). Output full file contents for each file you "
    "create or modify (never diffs). Keep the change minimal and reviewable: "
    f"at most {_MAX_FILES} files, no unrelated refactors, no secrets. This is a "
    "DRAFT for human review, not a final merge. Prefer adding a small module or "
    "test over sweeping edits. Use repo-relative paths beginning with "
    "'mvpflow-ai/'."
)


def draft_available() -> bool:
    """True when an AI draft can be generated."""
    return llm_enabled()


def safe_repo_path(repo_root: Path, rel_path: str) -> Path:
    """Resolve ``rel_path`` under ``repo_root``, rejecting traversal/escape."""
    candidate = (repo_root / rel_path).resolve()
    root = repo_root.resolve()
    if root not in candidate.parents and candidate != root:
        raise ValueError(f"Unsafe path outside repo: {rel_path}")
    return candidate


def generate_proposal(ticket: JiraTicket) -> ImplementationProposal:
    """Ask Claude for a candidate implementation of the ticket."""
    prompt = (
        f"Ticket {ticket.key}: {ticket.title}\n\n"
        f"User story: {ticket.user_story}\n"
        f"Description: {ticket.description}\n"
        f"Acceptance criteria:\n- " + "\n- ".join(ticket.acceptance_criteria) + "\n\n"
        "Draft a minimal, reviewable implementation. Return summary, files "
        "(each with path, action, full content, rationale), and notes."
    )
    proposal = generate_structured(_SYSTEM, prompt, ImplementationProposal)
    if len(proposal.files) > _MAX_FILES:
        logger.warning("Proposal had %d files; truncating to %d", len(proposal.files), _MAX_FILES)
        proposal.files = proposal.files[:_MAX_FILES]
    return proposal
