# Agentic Marketing Agency (Learning Project)

[![CI](https://github.com/eviva2000/Marketing-Agency/actions/workflows/ci.yml/badge.svg)](https://github.com/eviva2000/Marketing-Agency/actions/workflows/ci.yml)

A small Offer Creation Bot built on the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/),
used as a hands-on introduction to tool calling, structured outputs, and multi-agent handoffs.

## What it does

1. **Offer Creation Bot** (conversational) interviews you about your target industry, uses mock
   research tools to compare candidate niches, and gives an opinionated recommendation.
2. Once you confirm a niche, it **hands off** to the **Offer Summarizer** agent, which reads the
   conversation and returns a structured `OfferPackage` (offer summary + ready-to-use pitch copy).

All research data in `src/agency/tools.py` is mocked/hardcoded — no real web search or APIs yet.

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

## Run

```bash
source .venv/bin/activate
python -m agency.cli
```

Try: "I run a marketing agency focused on home services" → confirm the recommended niche → watch
it hand off and print the structured `OfferPackage` JSON.

## Project layout

- `src/agency/schemas.py` — Pydantic models for the structured output (`OfferPackage`)
- `src/agency/tools.py` — mock `@function_tool` functions (niche lists, benchmarks)
- `src/agency/agents/offer_agent.py` — conversational agent with tools + handoff
- `src/agency/agents/offer_summarizer_agent.py` — structured-output agent, handoff target
- `src/agency/cli.py` — interactive chat loop, prints tool calls/handoffs for visibility

## Architecture decisions

Significant design choices and their alternatives are recorded in [docs/decisions](docs/decisions):

- [ADR-001](docs/decisions/ADR-001-openai-agents-sdk.md) — why the OpenAI Agents SDK over LangChain/CrewAI/raw API
- [ADR-002](docs/decisions/ADR-002-handoff-for-structured-output.md) — why a handoff produces the structured output, not the main agent
- [ADR-003](docs/decisions/ADR-003-v1-scope.md) — why v1 is one agent pair, CLI-only, with mocked tools

## Next steps (not built yet)

- Real tools (web search, CRM, email) instead of mocks
- Additional stage agents (Lead Gen, Outbound, Qualify, Sales)
- Input guardrails and persisted sessions across separate CLI runs
- Inspect SDK tracing to visualize tool calls/handoffs
