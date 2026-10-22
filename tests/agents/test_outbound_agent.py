"""Behavior tests for Outbound drafting and structured handoff."""

import dataclasses
import json

from agents import Runner
from agents.items import HandoffOutputItem

from agency.agents.outbound_agent import outbound_agent
from agency.agents.outbound_summarizer_agent import outbound_summarizer_agent
from agency.schemas import OutboundPackage
from tests.conftest import handoff_tool_name, text_message, tool_call


def _package_json() -> str:
    return json.dumps({
        "niche": "Roofing",
        "drafts": [{
            "lead_name": "Acme Roofing Co.",
            "email_subject": "Qualified roofing leads for Acme",
            "email_body": "I noticed Acme serves Austin. Could we discuss exclusive leads?",
            "call_opener": "Hi, I have an idea for Acme's Austin lead pipeline.",
            "personalization_rationale": "References Acme's confirmed service area.",
        }],
    })


def test_outbound_summarizer_returns_structured_package(fake_model):
    agent = dataclasses.replace(
        outbound_summarizer_agent,
        model=fake_model([[text_message(_package_json())]]),
    )

    result = Runner.run_sync(agent, "I approve these drafts")

    assert isinstance(result.final_output, OutboundPackage)
    assert result.final_output.drafts[0].lead_name == "Acme Roofing Co."


def test_outbound_agent_hands_off_after_approval(fake_model):
    target = dataclasses.replace(
        outbound_summarizer_agent,
        model=fake_model([[text_message(_package_json())]]),
    )
    agent = dataclasses.replace(
        outbound_agent,
        handoffs=[target],
        model=fake_model([[tool_call(handoff_tool_name(target), "{}")]]),
    )

    result = Runner.run_sync(agent, "I approve these drafts")

    handoffs = [item for item in result.new_items if isinstance(item, HandoffOutputItem)]
    assert len(handoffs) == 1
    assert handoffs[0].target_agent.name == "Outbound Summarizer"
    assert isinstance(result.final_output, OutboundPackage)
