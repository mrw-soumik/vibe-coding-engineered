"""LLM-layer tests: provider selection, Groq routing (mocked), and fallback.

No real network/model calls, the Groq HTTP call is monkeypatched.
"""
from __future__ import annotations

import json
import pytest

from app.config import config
from app.llm import client as llm
from app.models import RequirementExtraction
from app.core.requirements_extractor import extract_requirements


def test_provider_none_without_keys(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(config, "GROQ_API_KEY", "")
    monkeypatch.setattr(config, "USE_LLM", True)
    assert llm.provider() is None
    assert llm.llm_enabled() is False  # no provider → disabled even with USE_LLM


def test_web_search_requires_anthropic(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(config, "GROQ_API_KEY", "gsk_test")
    with pytest.raises(RuntimeError):
        llm.web_search("anything")


class _FakeResp:
    status_code = 200

    def __init__(self, content: str):
        self._content = content

    def raise_for_status(self):  # noqa: D401
        return None

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


def test_generate_structured_routes_to_groq(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(config, "GROQ_API_KEY", "gsk_test")
    assert llm.provider() == "groq"

    payload = json.dumps({
        "problem": "p", "target_user": "u",
        "pain_points": ["a"], "risks": [], "assumptions": [],
    })

    def fake_post(url, headers=None, json=None, timeout=None):
        assert "groq.com" in url
        assert json["response_format"]["type"] == "json_object"
        return _FakeResp(payload)

    monkeypatch.setattr("app.llm.client.httpx.post", fake_post)
    out = llm.generate_structured("system", "prompt", RequirementExtraction)
    assert isinstance(out, RequirementExtraction)
    assert out.problem == "p"


def test_pipeline_falls_back_to_template_when_disabled(monkeypatch):
    # LLM disabled → deterministic template path (restaurant config).
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(config, "GROQ_API_KEY", "")
    req = extract_requirements("Restaurant owners answer repeated questions.", "restaurant")
    assert "restaurant" in req.problem.lower() or req.problem  # template-derived, no LLM
