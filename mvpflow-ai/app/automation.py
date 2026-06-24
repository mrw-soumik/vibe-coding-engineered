"""End-to-end Jira -> Branch -> (AI draft) -> Draft PR -> Jira update automation.

Implements slide 11 of the workshop ("Connect Jira to GitHub execution") as a
deterministic, human-gated pipeline. For each generated ticket it:

  1. finds the live Jira issue (by its [MVP-xxx] summary marker),
  2. optionally asks Claude for a candidate implementation (draft only),
  3. creates a feature branch named with the issue key + commits the changes,
  4. pushes and opens a **draft** PR pre-filled from the ticket,
  5. transitions the Jira issue to "In Progress" and comments the PR link.

It NEVER merges, a human reviews and merges the draft PR. Dry-run by default;
pass --live to actually create branches/PRs and update Jira.

Usage:
    python -m app.automation                      # dry-run plan for all tickets
    python -m app.automation --limit 1 --live     # do one ticket for real
    python -m app.automation --live --no-ai-draft # plumbing only, no AI code
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from app.integrations import github, jira
from app.llm import codegen
from app.core.workflow import run_workflow

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("automation")

PROPOSALS_DIR = "mvpflow-ai/automation/proposals"


def _write_ai_draft(ticket, issue_key) -> list[Path]:
    """Generate an AI draft and write its files; return the written paths."""
    proposal = codegen.generate_proposal(ticket)
    written: list[Path] = []
    for fc in proposal.files:
        try:
            target = codegen.safe_repo_path(github.REPO_ROOT, fc.path)
        except ValueError as e:
            logger.warning("Skipping unsafe path from AI draft: %s (%s)", fc.path, e)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(fc.content, encoding="utf-8")
        written.append(target)
    # Always include a human-readable proposal note for the reviewer.
    note = github.REPO_ROOT / PROPOSALS_DIR / f"{issue_key or ticket.key}.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    body = [f"# AI draft for {issue_key or ticket.key}: {ticket.title}", "",
            proposal.summary, "", "## Files", *[f"- `{f.path}` ({f.action}), {f.rationale}" for f in proposal.files],
            "", "## Notes", proposal.notes]
    note.write_text("\n".join(body), encoding="utf-8")
    written.append(note)
    return written


def _scaffold_note(ticket, issue_key) -> list[Path]:
    """Write a placeholder proposal note (when AI draft is off/unavailable)."""
    note = github.REPO_ROOT / PROPOSALS_DIR / f"{issue_key or ticket.key}.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {issue_key or ticket.key}: {ticket.title}", "", ticket.user_story, "",
             "## Acceptance criteria", *[f"- [ ] {c}" for c in ticket.acceptance_criteria],
             "", "_Implement on this branch, then mark the draft PR ready for review._"]
    note.write_text("\n".join(lines), encoding="utf-8")
    return [note]


def run(domain: str, input_path: str, live: bool, ai_draft: bool, limit: int, base: str) -> int:
    notes = Path(input_path).read_text(encoding="utf-8")
    result = run_workflow(notes, domain)
    tickets = result.jira_tickets[: limit if limit > 0 else None]

    ai_on = ai_draft and codegen.draft_available()
    if ai_draft and not ai_on:
        print("! AI draft requested but Claude is not enabled (set ANTHROPIC_API_KEY + USE_LLM=true). "
              "Falling back to scaffold notes.\n")
    if live and not github.gh_available():
        print("Error: --live needs the gh CLI authenticated. Run `gh auth login` first.", file=sys.stderr)
        return 2
    if live and not jira.jira_enabled():
        print("! Jira not configured, branches/PRs will be created but issues won't be updated.\n")

    mode = "LIVE" if live else "DRY RUN (no branches/PRs/Jira changes)"
    print(f"{'='*64}\nWorkflow automation: {mode} | AI draft: {'on' if ai_on else 'off'} | {len(tickets)} ticket(s)\n{'='*64}")

    created = 0
    for ticket in tickets:
        issue = jira.find_issue_for_ticket(ticket) if jira.jira_enabled() else None
        issue_key = issue["key"] if issue else None
        branch = github.branch_name(ticket, issue_key)
        title = f"{issue_key or ticket.key}: {ticket.title}"

        if not live:
            print(f"\n• {ticket.key}  (Jira: {issue_key or 'not found'})")
            print(f"    branch:        {branch}")
            print(f"    draft PR:      {title}")
            print(f"    AI draft:      {'generate candidate change' if ai_on else 'scaffold note only'}")
            print(f"    Jira update:   {'transition '+issue_key+' -> In Progress + comment PR link' if issue_key else 'skip (no issue)'}")
            continue

        try:
            files = _write_ai_draft(ticket, issue_key) if ai_on else _scaffold_note(ticket, issue_key)
            github.create_branch_with_changes(branch, files, f"{issue_key or ticket.key}: scaffold {ticket.title}", base=base)
            pr_url = github.open_draft_pr(branch, title, github.pr_body(ticket, issue_key, issue["url"] if issue else None), base=base)
            print(f"  ✓ {ticket.key} -> branch {branch} | draft PR {pr_url}")
            if issue_key:
                jira.transition_issue(issue_key, "In Progress")
                jira.add_comment(issue_key, f"Draft PR opened by MVPFlow automation: {pr_url}")
            created += 1
        except Exception as e:
            print(f"  ✗ {ticket.key} failed: {e}", file=sys.stderr)
        finally:
            try:
                github._run(["git", "checkout", base])
            except Exception:
                pass

    if live:
        print(f"\nOpened {created}/{len(tickets)} draft PR(s). Review and merge them yourself.")
    return 0


def main() -> None:
    p = argparse.ArgumentParser(description="Automate Jira -> branch -> draft PR -> Jira update.")
    p.add_argument("--input", default="examples/restaurant_founder_notes.txt")
    p.add_argument("--domain", default="restaurant")
    p.add_argument("--live", action="store_true", help="Actually create branches/PRs and update Jira (default: dry run).")
    p.add_argument("--no-ai-draft", dest="ai_draft", action="store_false", help="Skip Claude code drafting (plumbing only).")
    p.add_argument("--limit", type=int, default=1, help="How many tickets to process (default 1; 0 = all).")
    p.add_argument("--base", default="main", help="Base branch (default: main).")
    p.set_defaults(ai_draft=True)
    args = p.parse_args()
    sys.exit(run(args.domain, args.input, args.live, args.ai_draft, args.limit, args.base))


if __name__ == "__main__":
    main()
