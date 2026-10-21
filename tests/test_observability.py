"""Unit tests for agency.observability: console-export toggle and RunConfig tagging."""

import dataclasses
import json

from agents import Runner
from agents.tracing import TracingProcessor, set_trace_processors
from agents.tracing.processors import BatchTraceProcessor, ConsoleSpanExporter, default_processor

from agency.agents.offer_agent import offer_agent
from agency.agents.offer_summarizer_agent import offer_summarizer_agent
from agency.observability import CONSOLE_TRACING_ENV_VAR, configure_tracing, run_config
from tests.conftest import handoff_tool_name, text_message, tool_call

_OFFER_PACKAGE_JSON = json.dumps(
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


def test_configure_tracing_switches_to_console_when_env_var_set(monkeypatch):
    monkeypatch.setenv(CONSOLE_TRACING_ENV_VAR, "1")
    captured = {}
    monkeypatch.setattr(
        "agency.observability.set_trace_processors",
        lambda processors: captured.setdefault("processors", processors),
    )

    configure_tracing()

    (processor,) = captured["processors"]
    assert isinstance(processor, BatchTraceProcessor)
    assert isinstance(processor._exporter, ConsoleSpanExporter)


def test_configure_tracing_leaves_default_when_env_var_unset(monkeypatch):
    monkeypatch.delenv(CONSOLE_TRACING_ENV_VAR, raising=False)
    monkeypatch.setattr(
        "agency.observability.set_trace_processors",
        lambda processors: (_ for _ in ()).throw(AssertionError("should not switch processors")),
    )

    configure_tracing()


def test_run_config_tags_workflow_name_and_group_id():
    config = run_config("Offer Stage", "offer-bot-cli")

    assert config.workflow_name == "Offer Stage"
    assert config.group_id == "offer-bot-cli"


class _RecordingProcessor(TracingProcessor):
    """In-memory processor that records traces/spans instead of exporting anywhere."""

    def __init__(self):
        self.traces = []
        self.span_types = []

    def on_trace_start(self, trace):
        self.traces.append(trace)

    def on_trace_end(self, trace):
        pass

    def on_span_start(self, span):
        pass

    def on_span_end(self, span):
        self.span_types.append(span.span_data.type)

    def shutdown(self):
        pass

    def force_flush(self):
        pass


def test_offer_agent_run_is_traced_with_workflow_name_and_handoff_span(fake_model):
    recorder = _RecordingProcessor()
    set_trace_processors([recorder])
    try:
        summarizer = dataclasses.replace(
            offer_summarizer_agent,
            model=fake_model([[text_message(_OFFER_PACKAGE_JSON)]]),
        )
        agent = dataclasses.replace(
            offer_agent,
            handoffs=[summarizer],
            model=fake_model([[tool_call(handoff_tool_name(summarizer), "{}")]]),
        )

        Runner.run_sync(
            agent,
            "recommend a niche",
            run_config=run_config("Offer Stage", "test-group"),
        )
    finally:
        set_trace_processors([default_processor()])

    assert len(recorder.traces) == 1
    assert recorder.traces[0].name == "Offer Stage"
    assert recorder.traces[0].group_id == "test-group"
    assert "agent" in recorder.span_types
    assert "handoff" in recorder.span_types
