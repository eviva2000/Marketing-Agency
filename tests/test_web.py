"""Tests for the local browser server's conversation handling."""

import json
from threading import Thread
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from agents import Agent
from agents.items import HandoffOutputItem, ToolCallItem, ToolCallOutputItem
from openai.types.responses import ResponseFunctionToolCall

from agency.schemas import OutboundDraft, OutboundPackage
from agency.web import ConversationManager, SessionNotFoundError, create_server


def test_conversation_reuses_session_and_last_agent_then_resets():
    first_agent = Agent(name="Offer Creation Bot", instructions="test")
    next_agent = Agent(name="Offer Summarizer", instructions="test")
    calls = []

    def run_turn(agent, message, session, group_id):
        calls.append((agent, message, session, group_id))
        next_result_agent = next_agent if len(calls) == 1 else agent
        return SimpleNamespace(last_agent=next_result_agent, final_output=f"reply {len(calls)}", new_items=[])

    manager = ConversationManager(run_turn=run_turn, starting_agent=first_agent)
    session_id = manager.start()

    first = manager.submit(session_id, "start")
    second = manager.submit(session_id, "continue")

    assert first["reply"] == "reply 1"
    assert second["reply"] == "reply 2"
    assert calls[0][0] is first_agent
    assert calls[1][0] is next_agent
    assert calls[0][2] is calls[1][2]
    assert calls[0][3] == calls[1][3]
    assert calls[0][3] != session_id

    manager.reset(session_id)
    with pytest.raises(SessionNotFoundError):
        manager.submit(session_id, "after reset")


def test_conversation_returns_structured_output_as_json_data():
    structured = OutboundPackage(
        niche="Roofing",
        drafts=[
            OutboundDraft(
                lead_name="North Roofing",
                email_subject="A quick idea",
                email_body="Hello",
                call_opener="Hi",
                personalization_rationale="Confirmed lead details",
            )
        ],
    )
    manager = ConversationManager(
        run_turn=lambda *_: SimpleNamespace(last_agent=Agent(name="Outbound", instructions="test"), final_output=structured, new_items=[]),
        starting_agent=Agent(name="Offer", instructions="test"),
    )

    response = manager.submit(manager.start(), "approve")

    assert response["structured"]["niche"] == "Roofing"
    assert response["structured"]["drafts"][0]["lead_name"] == "North Roofing"


def test_activity_hides_tool_arguments_and_results():
    offer_agent = Agent(name="Offer Creation Bot", instructions="test")
    target_agent = Agent(name="Lead Gen Bot", instructions="test")
    tool_call = ToolCallItem(
        agent=offer_agent,
        raw_item=ResponseFunctionToolCall(
            id="fc_1", call_id="call_1", type="function_call", name="web_search",
            arguments='{"query":"API_KEY=private"}',
        ),
    )
    tool_result = ToolCallOutputItem(agent=offer_agent, raw_item={}, output="private search output")
    handoff = HandoffOutputItem(
        agent=offer_agent, raw_item={}, source_agent=offer_agent, target_agent=target_agent
    )
    manager = ConversationManager(
        run_turn=lambda *_: SimpleNamespace(
            last_agent=target_agent, final_output="Found leads", new_items=[tool_call, tool_result, handoff]
        ),
        starting_agent=offer_agent,
    )

    response = manager.submit(manager.start(), "find leads")
    serialized = str(response["activity"])

    assert "API_KEY" not in serialized
    assert "private search output" not in serialized
    assert any(item["type"] == "handoff" for item in response["activity"])


def test_failed_turn_does_not_advance_active_agent():
    first_agent = Agent(name="Offer Creation Bot", instructions="test")
    next_agent = Agent(name="Offer Summarizer", instructions="test")
    attempted_agents = []

    def run_turn(agent, *_):
        attempted_agents.append(agent)
        if len(attempted_agents) == 1:
            raise RuntimeError("model unavailable")
        return SimpleNamespace(last_agent=next_agent, final_output="Try again worked", new_items=[])

    manager = ConversationManager(run_turn=run_turn, starting_agent=first_agent)
    session_id = manager.start()

    with pytest.raises(RuntimeError):
        manager.submit(session_id, "start")
    response = manager.submit(session_id, "retry")

    assert attempted_agents == [first_agent, first_agent]
    assert response["reply"] == "Try again worked"


def test_conversations_are_isolated():
    sessions = []

    def run_turn(agent, _, session, __):
        sessions.append(session)
        return SimpleNamespace(last_agent=agent, final_output="ok", new_items=[])

    manager = ConversationManager(
        run_turn=run_turn,
        starting_agent=Agent(name="Offer", instructions="test"),
    )
    first_session = manager.start()
    second_session = manager.start()
    manager.submit(first_session, "first")
    manager.submit(second_session, "second")

    assert first_session != second_session
    assert sessions[0] is not sessions[1]
    manager.reset(first_session)
    assert manager.submit(second_session, "still active")["reply"] == "ok"


def test_local_server_serves_ui_and_enforces_session_api():
    server = create_server(port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"

    def request(path, method="GET", payload=None):
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Origin": base_url}
        if body is not None:
            headers["Content-Type"] = "application/json"
        return urlopen(Request(base_url + path, data=body, headers=headers, method=method))

    try:
        page = request("/")
        assert page.status == 200
        assert "Content-Security-Policy" in page.headers
        assert b"Agency Builder" in page.read()
        assert b"https://" not in request("/app.js").read()

        created = json.loads(request("/api/sessions", "POST", {}).read())
        assert len(created["session_id"]) >= 40

        cross_origin = Request(
            base_url + "/api/sessions",
            data=b"{}",
            headers={"Content-Type": "application/json", "Origin": "http://outside.example"},
            method="POST",
        )
        with pytest.raises(HTTPError) as forbidden:
            urlopen(cross_origin)
        assert forbidden.value.code == 403

        with pytest.raises(HTTPError) as missing_session:
            request("/api/chat", "POST", {"session_id": "unknown", "message": "hello"})
        assert missing_session.value.code == 404

        deleted = json.loads(request(f"/api/sessions/{created['session_id']}", "DELETE").read())
        assert deleted == {"ok": True}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
