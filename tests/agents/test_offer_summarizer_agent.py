"""Behavior tests for offer_summarizer_agent: structured OfferPackage output."""

import dataclasses
import json

from agents import Runner
from agents.items import HandoffOutputItem

from agency.agents.lead_gen_agent import lead_gen_agent
from agency.agents.offer_summarizer_agent import offer_summarizer_agent
from agency.schemas import OfferPackage
from tests.conftest import handoff_tool_name, text_message, tool_call


def _offer_package_json() -> str:
    return json.dumps(
        {
            "niche": "Roofing",
            "offer_summary": {
                "who": "Roofing companies doing $1M+/year",
                "what": "Done-for-you lead generation",
                "promise": "10 qualified leads/month",
                "model": "Pay-per-qualified-lead",
                "delivery": "Landing page + ad campaigns",
                "guarantee": "First 10 leads free if we miss the target",
            },
            "final_pitch": {
                "who_we_help": "Roofing companies tired of shared leads",
                "pain_points": ["Shared leads", "Seasonal demand", "No in-house marketing"],
                "promise": "10 exclusive leads/month, guaranteed",
                "proof_math": "One $15k job pays for a year of this service",
            },
        }
    )


def test_offer_summarizer_returns_structured_offer_package(fake_model):
    agent = dataclasses.replace(
        offer_summarizer_agent,
        model=fake_model([[text_message(_offer_package_json())]]),
    )

    result = Runner.run_sync(agent, "The user confirmed the Roofing niche.")

    assert isinstance(result.final_output, OfferPackage)
    assert result.final_output.niche == "Roofing"
    assert result.final_output.offer_summary.model == "Pay-per-qualified-lead"
    assert len(result.final_output.final_pitch.pain_points) == 3


def test_offer_summarizer_hands_off_to_lead_gen_once_asked(fake_model):
    target = dataclasses.replace(
        lead_gen_agent,
        model=fake_model([[text_message("Sure, let's find some leads.")]]),
    )
    agent = dataclasses.replace(
        offer_summarizer_agent,
        handoffs=[target],
        model=fake_model([[tool_call(handoff_tool_name(target), "{}", call_id="call_1")]]),
    )

    result = Runner.run_sync(agent, "Great, now find me some leads for this offer")

    handoff_items = [item for item in result.new_items if isinstance(item, HandoffOutputItem)]
    assert len(handoff_items) == 1
    assert handoff_items[0].target_agent.name == "Lead Gen Bot"
    assert handoff_items[0].source_agent.name == "Offer Summarizer"
