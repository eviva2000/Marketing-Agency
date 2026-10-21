"""Tracing setup: OpenAI dashboard export by default, console export for API-key-free local runs."""

import os

from agents import RunConfig
from agents.tracing import set_trace_processors
from agents.tracing.processors import BatchTraceProcessor, ConsoleSpanExporter

CONSOLE_TRACING_ENV_VAR = "AGENCY_TRACE_CONSOLE"


def configure_tracing() -> None:
    """Print traces to stdout instead of the OpenAI backend when `AGENCY_TRACE_CONSOLE` is set."""
    if os.environ.get(CONSOLE_TRACING_ENV_VAR):
        set_trace_processors([BatchTraceProcessor(ConsoleSpanExporter())])


def run_config(workflow_name: str, group_id: str) -> RunConfig:
    """Tag a run so its spans are named and grouped for tracing."""
    return RunConfig(workflow_name=workflow_name, group_id=group_id)
