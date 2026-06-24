#!/usr/bin/env python3
"""Evaluation harness, grade pipeline output against a golden rubric.

Runs the workflow on each case in ``golden_cases.json`` and checks the output
against declarative rubric assertions. Runs in deterministic mode by default
(no key, no cost), so it's reproducible; set a provider key + ``USE_LLM=true``
to grade *live* generated output with the same rubric (the on-message use:
catch quality regressions before shipping).

Usage:
    python eval/run_eval.py            # deterministic
    USE_LLM=true python eval/run_eval.py   # grade live LLM output

Exits non-zero if any case fails, so it can gate a release if you choose.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Make the project root importable when run as a standalone script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.workflow import run_workflow  # noqa: E402

CASES = Path(__file__).with_name("golden_cases.json")


def _check(result, name: str, expected) -> tuple[bool, str]:
    """Return (passed, detail) for one rubric assertion."""
    r = result
    if name == "min_tickets":
        n = len(r.jira_tickets)
        return n >= expected, f"{n} tickets (need ≥{expected})"
    if name == "all_tickets_min_acceptance":
        ok = all(len(t.acceptance_criteria) >= expected for t in r.jira_tickets)
        return ok, f"every ticket has ≥{expected} acceptance criteria"
    if name == "tickets_have_story_points":
        ok = all(t.story_points is not None for t in r.jira_tickets)
        return ok, "all tickets have story points"
    if name == "risks_include":
        joined = " ".join(r.requirements.risks).lower()
        return expected.lower() in joined, f"risks include '{expected}'"
    if name == "recommended_mvp_nonempty":
        return bool(r.mvp_plan.recommended_mvp.strip()), "recommended MVP present"
    if name == "summary_includes":
        return expected in r.final_summary, f"summary includes '{expected}'"
    return False, f"unknown check '{name}'"


def main() -> int:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    total_failed = 0
    print(f"Running eval over {len(cases)} golden case(s)\n" + "=" * 60)
    for case in cases:
        result = run_workflow(case["notes"], case["domain"])
        print(f"\n• {case['name']}  (domain: {case['domain']})")
        case_failed = 0
        for check_name, expected in case["checks"].items():
            passed, detail = _check(result, check_name, expected)
            print(f"    {'PASS' if passed else 'FAIL'}  {detail}")
            if not passed:
                case_failed += 1
        total_failed += case_failed
    print("\n" + "=" * 60)
    print("ALL CHECKS PASSED" if total_failed == 0 else f"{total_failed} CHECK(S) FAILED")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
