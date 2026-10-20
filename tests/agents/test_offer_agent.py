"""Behavior tests for offer_agent: tool usage followed by a handoff."""

import dataclasses
import json

from agents import Runner
from agents.items import HandoffOutputItem

from agency.agents.offer_agent import offer_agent
from agency.agents.offer_summarizer_agent import offer_summarizer_agent
from tests.conftest import handoff_tool_name, text_message, tool_call


def _minimal_offer_package_json() -> str:
    return json.dumps(
        {
            "niche": "Roofing",
            "offer_summary": {
                "who": "Roofing companies",
                "what": "Lead generation",
                "promise": "10 leads/month",
                "model": "Pay-per-lead",
                "delivery": "Ads + landing page",
                "guarantee": "Money back if no leads",
            },
            "final_pitch": {
                "who_we_help": "Roofing companies",
                "pain_points": ["Shared leads", "Seasonal demand"],
                "promise": "Exclusive leads, guaranteed",
                "proof_math": "One job pays for a year",
            },
        }
    )


def test_offer_agent_uses_tools_then_hands_off(fake_model):
    summarizer = dataclasses.replace(
        offer_summarizer_agent,
        model=fake_model([[text_message(_minimal_offer_package_json())]]),
    )
    agent = dataclasses.replace(
        offer_agent,
        handoffs=[summarizer],
        model=fake_model(
            [
                [tool_call("list_candidate_niches", '{"industry": "home services"}', call_id="call_1")],
                [tool_call("get_niche_benchmarks", '{"niche": "Roofing"}', call_id="call_2")],
                [tool_call(handoff_tool_name(summarizer), "{}", call_id="call_3")],
            ]
        ),
    )

    result = Runner.run_sync(agent, "I run a home services agency, recommend a niche")

    handoff_items = [item for item in result.new_items if isinstance(item, HandoffOutputItem)]
    assert len(handoff_items) == 1
    assert handoff_items[0].target_agent.name == "Offer Summarizer"
    assert handoff_items[0].source_agent.name == "Offer Creation Bot"
