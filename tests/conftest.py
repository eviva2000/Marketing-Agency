"""Shared pytest fixtures, including a fake Model so agent tests never call a real LLM."""

import pytest
from agents import Agent
from agents.handoffs import Handoff
from agents.models.interface import Model, ModelResponse
from agents.usage import Usage
from openai.types.responses import (
    ResponseFunctionToolCall,
    ResponseOutputMessage,
    ResponseOutputText,
)
from openai.types.responses.response_output_item import ResponseOutputItem


def text_message(text: str) -> ResponseOutputItem:
    """Build a scripted assistant text-message output item."""
    return ResponseOutputMessage(
        id="msg_fake",
        type="message",
        role="assistant",
        status="completed",
        content=[ResponseOutputText(type="output_text", text=text, annotations=[])],
    )


def tool_call(name: str, arguments: str = "{}", call_id: str = "call_fake") -> ResponseOutputItem:
    """Build a scripted function/handoff tool-call output item."""
    return ResponseFunctionToolCall(
        type="function_call",
        id="fc_fake",
        call_id=call_id,
        name=name,
        arguments=arguments,
    )


def handoff_tool_name(agent: Agent) -> str:
    """Return the default tool name the SDK generates for handing off to `agent`."""
    return Handoff.default_tool_name(agent)


class FakeModel(Model):
    """A `Model` that replays a pre-scripted queue of responses instead of calling an LLM."""

    def __init__(self, responses: list[list[ResponseOutputItem]]):
        self._responses = list(responses)

    async def get_response(
        self,
        system_instructions,
        input,
        model_settings,
        tools,
        output_schema,
        handoffs,
        tracing,
        *,
        previous_response_id,
        conversation_id,
        prompt,
    ) -> ModelResponse:
        if not self._responses:
            raise AssertionError("FakeModel has no more scripted responses")
        output = self._responses.pop(0)
        return ModelResponse(output=output, usage=Usage(), response_id=None)

    async def stream_response(self, *args, **kwargs):
        raise NotImplementedError("FakeModel does not support streaming")

    def get_retry_advice(self, *args, **kwargs):
        return None

    async def close(self) -> None:
        pass


@pytest.fixture
def fake_model():
    return FakeModel
