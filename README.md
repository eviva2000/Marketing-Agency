# Agentic Marketing Agency (Learning Project)

[![CI](https://github.com/eviva2000/Marketing-Agency/actions/workflows/ci.yml/badge.svg)](https://github.com/eviva2000/Marketing-Agency/actions/workflows/ci.yml)

A small Offer Creation Bot built on the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/),
used as a hands-on introduction to tool calling, structured outputs, and multi-agent handoffs.

## What it does

1. **Offer Creation Bot** (conversational) interviews you about your target industry, uses the
   Agents SDK's `WebSearchTool` to research real candidate niches and benchmarks, and gives an
   opinionated recommendation grounded in what it finds.
2. Once you confirm a niche, it **hands off** to the **Offer Summarizer** agent, which reads the
   conversation and returns a structured `OfferPackage` (offer summary + ready-to-use pitch copy).

`WebSearchTool` is a hosted tool that requires a real `OPENAI_API_KEY` (OpenAI Responses API) —
there is no API-key-free mock mode for the Offer stage anymore.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # then add your real OPENAI_API_KEY
```

## Development

```bash
pip install -e ".[dev]"
python -m pytest     # run tests (no OPENAI_API_KEY needed — agent tests use a fake Model)
ruff check .          # lint
```

`WebSearchTool` is a hosted tool executed by OpenAI's backend, so it never runs under the fake
`Model` used in tests — the automated suite only checks that `offer_agent` is wired with it, not
actual search behavior. To see real search results, run the CLI by hand with a real
`OPENAI_API_KEY` (see Run below).

## Run

```bash
source .venv/bin/activate
python -m agency.cli
```

Try: "I run a marketing agency focused on home services" → confirm the recommended niche → watch
it hand off and print the structured `OfferPackage` JSON.

## Tracing

Every CLI run is tagged with a `workflow_name` ("Offer Stage") and a `group_id` (the CLI session
id), so all turns of one conversation link into a single traced group.

- **Default:** traces export to the [OpenAI dashboard](https://platform.openai.com/traces)
  (requires `OPENAI_API_KEY`).
- **Local/offline:** set `AGENCY_TRACE_CONSOLE=1` to print traces/spans to stdout instead — no API
  key or network access needed.

```bash
AGENCY_TRACE_CONSOLE=1 python -m agency.cli
```

## Project layout

- `src/agency/schemas.py` — Pydantic models for the structured output (`OfferPackage`)
- `src/agency/agents/offer_agent.py` — conversational agent with `WebSearchTool` + handoff
- `src/agency/agents/offer_summarizer_agent.py` — structured-output agent, handoff target
- `src/agency/observability.py` — tracing setup (console export toggle, `RunConfig` tagging)
- `src/agency/cli.py` — interactive chat loop, prints tool calls/handoffs for visibility
- `context/` — planning/context docs: project overview, coding standards, how an agent should
  operate in this repo, and the current/completed feature log (start at
  [context/project-overview.md](context/project-overview.md))

## Architecture decisions

Significant design choices and their alternatives are recorded in [docs/decisions](docs/decisions):

- [ADR-001](docs/decisions/ADR-001-openai-agents-sdk.md) — why the OpenAI Agents SDK over LangChain/CrewAI/raw API
- [ADR-002](docs/decisions/ADR-002-handoff-for-structured-output.md) — why a handoff produces the structured output, not the main agent
- [ADR-003](docs/decisions/ADR-003-v1-scope.md) — why v1 is one agent pair, CLI-only, with mocked tools (now superseded for the Offer stage's tools — see the ADR's Update note)

## Next steps (not built yet)

- Additional stage agents (Lead Gen, Outbound, Qualify, Sales)
- Input guardrails and persisted sessions across separate CLI runs
