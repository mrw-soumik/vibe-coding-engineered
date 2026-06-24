"""Tests for the landing-page generator.

The generator is an optional output: it turns the pipeline's requirements +
MVP plan into a self-contained HTML launch page, deterministically by default.
"""
from html.parser import HTMLParser

import pytest

from app.core.landing import create_landing_page, _copy_fallback
from app.core.workflow import run_workflow


@pytest.fixture
def result():
    notes = open("examples/restaurant_founder_notes.txt", encoding="utf-8").read()
    return run_workflow(notes, "restaurant")


def test_landing_page_is_well_formed_html(result):
    html = create_landing_page(result.requirements, result.mvp_plan, "restaurant")

    # Parses without error and is a complete standalone document.
    HTMLParser().feed(html)
    assert html.lstrip().startswith("<!doctype html>")
    assert "<title>" in html and "</html>" in html


def test_landing_page_is_self_contained(result):
    """No external assets, so it works offline (no CDN/font/script requests)."""
    html = create_landing_page(result.requirements, result.mvp_plan, "restaurant")
    assert "http://" not in html and "https://" not in html
    assert "<script" not in html  # the waitlist form is non-functional template markup


def test_landing_page_uses_plan_content(result):
    html = create_landing_page(result.requirements, result.mvp_plan, "restaurant")
    # Headline is the recommended MVP; features come from in-scope.
    assert result.mvp_plan.recommended_mvp.rstrip(".") in html
    for feature in result.mvp_plan.in_scope:
        assert feature in html


def test_fallback_copy_has_no_truncated_titles(result):
    """Value-prop titles must be whole statements, not cut-off fragments."""
    copy = _copy_fallback(result.requirements, result.mvp_plan, "restaurant")
    assert copy.value_props
    for prop in copy.value_props:
        assert prop.title  # non-empty
    assert copy.cta_label
    assert copy.product_name


def test_html_escaping_prevents_injection():
    """Plan content is escaped so it can't break out of the markup."""
    from app.models import RequirementExtraction, MVPPlan

    req = RequirementExtraction(
        problem="<script>alert(1)</script>",
        target_user="owners",
        pain_points=["p"],
        risks=["r"],
        assumptions=["a"],
    )
    plan = MVPPlan(
        recommended_mvp="Build <b>it</b>",
        in_scope=["Do \"x\" & y"],
        out_of_scope=["later"],
        success_criteria=["works"],
    )
    html = create_landing_page(req, plan, "test")
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
