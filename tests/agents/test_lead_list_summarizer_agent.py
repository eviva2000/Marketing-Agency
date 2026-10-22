"""Behavior tests for lead_list_summarizer_agent: structured LeadList output."""

import dataclasses
import json

from agents import Runner

from agency.agents.lead_list_summarizer_agent import lead_list_summarizer_agent
from agency.schemas import LeadList
from tests.conftest import text_message


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
