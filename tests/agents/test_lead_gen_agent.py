"""Behavior tests for lead_gen_agent: web search tool usage followed by a handoff."""

import dataclasses

from agents import Runner, WebSearchTool
from agents.items import HandoffOutputItem

from agency.agents.lead_gen_agent import lead_gen_agent
from agency.agents.lead_list_summarizer_agent import lead_list_summarizer_agent
from tests.conftest import handoff_tool_name, text_message, tool_call


def test_lead_gen_agent_has_web_search_tool():
    assert any(isinstance(tool, WebSearchTool) for tool in lead_gen_agent.tools)


def test_lead_gen_agent_hands_off_once_confirmed(fake_model):
    summarizer = dataclasses.replace(
        lead_list_summarizer_agent,
        model=fake_model([[text_message('{"niche": "Roofing", "leads": []}')]]),
    )
    agent = dataclasses.replace(
        lead_gen_agent,
        handoffs=[summarizer],
        model=fake_model([[tool_call(handoff_tool_name(summarizer), "{}", call_id="call_1")]]),
    )

    result = Runner.run_sync(agent, "That list looks good, let's go with those leads")

    handoff_items = [item for item in result.new_items if isinstance(item, HandoffOutputItem)]
    assert len(handoff_items) == 1
    assert handoff_items[0].target_agent.name == "Lead List Summarizer"
    assert handoff_items[0].source_agent.name == "Lead Gen Bot"
