"""Smoke test proving FakeModel drives a real Agent/Runner without a real LLM call."""

from agents import Agent, Runner

from tests.conftest import text_message


def test_fake_model_drives_runner(fake_model):
    agent = Agent(
        name="Echo Agent",
        instructions="irrelevant — model is faked",
        model=fake_model([[text_message("hello from fake model")]]),
    )

    result = Runner.run_sync(agent, "hi")

    assert result.final_output == "hello from fake model"
