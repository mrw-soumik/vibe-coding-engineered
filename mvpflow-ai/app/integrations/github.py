"""GitHub branch + pull-request automation for MVPFlow AI.

Implements the "Branch / Pull Request" leg of the workflow: for a generated
ticket, create a feature branch, commit any AI-drafted changes, push it, and
open a **draft** PR whose body is built from the ticket (acceptance criteria as
a checklist, definition of done, and the Jira issue link).

Design notes / safety:

* Uses the authenticated ``gh`` CLI rather than handling a token in code. If
  ``gh`` isn't installed or authenticated, operations are skipped with a clear
  message instead of failing hard.
* PRs are always opened as **drafts**, this code never merges anything. A human
  reviews and merges. (See the README "Automation" section.)
* Branches and PRs are named with the Jira issue key (e.g. ``WOR-3``) so the
  official GitHub-for-Jira app auto-links them and Smart Commits can transition
  the issue.
"""
from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from app.models import JiraTicket

logger = logging.getLogger(__name__)

# Repo root is the parent of the mvpflow-ai package dir (the Workshop folder).
REPO_ROOT = Path(__file__).resolve().parents[3]


def _run(cmd: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run a command, capturing output (raises on non-zero)."""
    return subprocess.run(
        cmd, cwd=str(cwd or REPO_ROOT),
        check=True, capture_output=True, text=True,
    )


def gh_available() -> bool:
    """True if the gh CLI is installed and authenticated."""
    if not shutil.which("gh"):
        return False
    try:
        subprocess.run(["gh", "auth", "status"], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError:
        return False


def branch_name(ticket: JiraTicket, issue_key: Optional[str] = None) -> str:
    """Branch name keyed by the live Jira issue (falls back to the ticket key)."""
    key = (issue_key or ticket.key).lower()
    slug = ticket.title.lower().replace(" ", "-").replace("/", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")[:40].strip("-")
    return f"feature/{key}-{slug}"


def pr_body(ticket: JiraTicket, issue_key: Optional[str] = None, issue_url: Optional[str] = None) -> str:
    """Markdown PR description built from the ticket."""
    key = issue_key or ticket.key
    lines = [f"## {ticket.title}", "", f"**Jira:** {issue_url or key}", "", ticket.user_story, "", ticket.description, "", "### Acceptance criteria"]
    lines += [f"- [ ] {c}" for c in ticket.acceptance_criteria]
    lines += ["", "### Definition of done"]
    lines += [f"- [ ] {d}" for d in ticket.definition_of_done]
    if ticket.story_points is not None:
        lines += ["", f"_Story points: {ticket.story_points}_"]
    lines += ["", "---", "_Draft opened by MVPFlow AI automation. Review before merging._"]
    return "\n".join(lines)


def create_branch_with_changes(
    branch: str,
    changed_files: List[Path],
    commit_message: str,
    base: str = "main",
) -> None:
    """Create ``branch`` off ``base``, stage ``changed_files``, commit, and push.

    ``changed_files`` are absolute paths already written to the working tree.
    """
    _run(["git", "checkout", base])
    _run(["git", "checkout", "-b", branch])
    if changed_files:
        _run(["git", "add", *[str(p) for p in changed_files]])
        _run(["git", "commit", "-m", commit_message])
    else:
        # Empty commit so the branch differs from base and a PR can open.
        _run(["git", "commit", "--allow-empty", "-m", commit_message])
    _run(["git", "push", "-u", "origin", branch])


def open_draft_pr(branch: str, title: str, body: str, base: str = "main") -> str:
    """Open a draft PR via gh and return its URL."""
    result = _run([
        "gh", "pr", "create", "--draft",
        "--base", base, "--head", branch,
        "--title", title, "--body", body,
    ])
    return result.stdout.strip()
