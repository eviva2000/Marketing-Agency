# Feature: observability (module 2 of 6)

## Status
Completed

## Objective

Make the Agents SDK's built-in tracing visible and testable for the Offer stage, so every later
module (`lead-gen`, `outbound`, `web-ui`) inherits the same observability for free instead of
bolting it on later.

Success: a developer can run the CLI and inspect a full trace (agent turns, tool calls, the
Offer -> Offer Summarizer handoff) either in the OpenAI dashboard (default, needs
`OPENAI_API_KEY`) or printed to stdout with no API key at all (local/offline mode, important for a
reviewer cloning the repo without credentials). Tracing behavior is covered by tests with zero
real API/network calls.

## Scope

- Tag every CLI run with a descriptive `workflow_name` and a `group_id` (the existing CLI
  `session_id`) via `agents.RunConfig`, so all turns of one conversation link into one traced
  group.
- Add a local/offline tracing mode: an env var switches the SDK's trace processor to
  `ConsoleSpanExporter` (via `agents.tracing.processors.BatchTraceProcessor`), so traces print to
  stdout instead of requiring network access or an API key.
- Keep the SDK's default backend export (OpenAI dashboard) as the default when the env var is
  unset — no behavior change for anyone already relying on it.
- Out of scope: custom span types, a custom trace UI/exporter, metrics/alerting (not part of this
  SDK-tracing-focused module).

## Task list

### Phase 1: Tracing setup
- [x] Task 1: `src/agency/observability.py` — `configure_tracing()` (switches to
      `ConsoleSpanExporter` when `AGENCY_TRACE_CONSOLE` is set) and `run_config(workflow_name,
      group_id)` (builds a `RunConfig` tagging a run for tracing)
- [x] Task 2: Wire `configure_tracing()` + `run_config(...)` into `src/agency/cli.py`'s
      `Runner.run_sync` calls

### Phase 2: Tests
- [x] Task 3: Unit test `configure_tracing()` env-var toggle (no real tracing processor hit)
- [x] Task 4: Agent-behavior test asserting a run produces the expected trace/span shape
      (workflow name, agent + handoff spans) using a custom in-memory `TracingProcessor` and the
      existing `FakeModel` — zero real API/network calls

### Phase 3: Docs
- [x] Task 5: README "Tracing" section documenting both modes and how to view a trace

## Checkpoint: Complete

- [x] `ruff check .` passes with zero errors
- [x] `python3 -m pytest` passes, including new observability tests
- [x] README documents `AGENCY_TRACE_CONSOLE=1` and the OpenAI dashboard trace view
- [x] `context/current-feature.md` updated: this entry moved to "Completed features"
