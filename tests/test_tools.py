"""Tests for the mock research function tools in agency.tools."""

import asyncio
import json

from agents.tool_context import ToolContext

from agency.tools import get_niche_benchmarks, list_candidate_niches


def _invoke(tool, **kwargs):
    args = json.dumps(kwargs)
    ctx = ToolContext(context=None, tool_name=tool.name, tool_call_id="call_fake", tool_arguments=args)
    return asyncio.run(tool.on_invoke_tool(ctx, args))


def test_list_candidate_niches_known_industry():
    niches = _invoke(list_candidate_niches, industry="home services")
    assert [n["niche"] for n in niches] == ["Roofing", "HVAC", "Foundation repair"]


def test_list_candidate_niches_unknown_industry_falls_back_to_generic():
    niches = _invoke(list_candidate_niches, industry="underwater basket weaving")
    assert niches == [
        {"niche": "Local home services", "rationale": "Broadly high-intent, easy to find via Google Ads"},
        {"niche": "Local professional services", "rationale": "High value per client, lower ad competition than e-commerce"},
    ]


def test_get_niche_benchmarks_known_niche_is_case_insensitive():
    lower = _invoke(get_niche_benchmarks, niche="roofing")
    upper = _invoke(get_niche_benchmarks, niche="ROOFING")
    assert lower == upper
    assert lower["avg_job_value"] == "$8k-$25k"


def test_get_niche_benchmarks_unknown_niche_falls_back_to_generic():
    benchmark = _invoke(get_niche_benchmarks, niche="alpaca farming")
    assert benchmark["demand_pattern"] == "unknown"
    assert benchmark["pain_points"] == []
