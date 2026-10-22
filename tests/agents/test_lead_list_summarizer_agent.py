"""Behavior tests for lead_list_summarizer_agent: structured LeadList output."""

import dataclasses
import json

from agents import Runner
from agents.items import HandoffOutputItem

from agency.agents.lead_list_summarizer_agent import lead_list_summarizer_agent
from agency.agents.outbound_agent import outbound_agent
from agency.schemas import LeadList
from tests.conftest import handoff_tool_name, text_message, tool_call


def _lead_list_json() -> str:
    return json.dumps(
        {
            "niche": "Roofing",
            "leads": [
                {
                    "name": "Acme Roofing Co.",
                    "how_found": "Google search for 'roofing companies in Austin, TX'",
                    "contact_info": "https://acmeroofing.example/contact",
                    "fit_reasoning": "Does $1M+/year and relies on shared leads today",
                    "outreach_angle": "Offer a free trial batch of exclusive leads",
                },
                {
                    "name": "Summit Roofing LLC",
                    "how_found": "Local business directory listing",
                    "contact_info": "(512) 555-0100",
                    "fit_reasoning": "Growing team, no in-house marketing",
                    "outreach_angle": "Pitch pay-per-lead pricing",
                },
            ],
        }
    )


def test_lead_list_summarizer_returns_structured_lead_list(fake_model):
    agent = dataclasses.replace(
        lead_list_summarizer_agent,
        model=fake_model([[text_message(_lead_list_json())]]),
    )

    result = Runner.run_sync(agent, "The user confirmed this list of leads.")

    assert isinstance(result.final_output, LeadList)
    assert result.final_output.niche == "Roofing"
    assert len(result.final_output.leads) == 2
    assert result.final_output.leads[0].name == "Acme Roofing Co."


def test_lead_list_summarizer_hands_off_to_outbound_when_asked(fake_model):
    target = dataclasses.replace(outbound_agent, model=fake_model([[text_message("Here are the drafts.")]]))
    agent = dataclasses.replace(
        lead_list_summarizer_agent,
        handoffs=[target],
        model=fake_model([[tool_call(handoff_tool_name(target), "{}")]]),
    )

    result = Runner.run_sync(agent, "Prepare outreach for these leads")

    handoffs = [item for item in result.new_items if isinstance(item, HandoffOutputItem)]
    assert len(handoffs) == 1
    assert handoffs[0].target_agent.name == "Outbound Bot"
