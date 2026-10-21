# Project Overview

## What this is

A small agentic marketing agency built on the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/),
started as a hands-on introduction to tool calling, structured outputs, and multi-agent handoffs,
now being leveled up into a resume-ready showcase of agentic-systems engineering (see
[full-pipeline-showcase intent](../docs/intent/full-pipeline-showcase.md) for the full rationale).

## What it does today

1. **Offer Creation Bot** (conversational) interviews the user about their target industry, uses
   research tools to compare candidate niches, and gives an opinionated recommendation.
2. Once the user confirms a niche, it **hands off** to the **Offer Summarizer** agent, which reads
   the conversation and returns a structured `OfferPackage` (offer summary + ready-to-use pitch
   copy).
3. Everything runs through a CLI chat loop (`python -m agency.cli`); no web UI yet.

Research data in `src/agency/tools.py` is currently mocked — see the Update note in
[ADR-003](../docs/decisions/ADR-003-v1-scope.md) for the plan to replace it with real
`WebSearchTool` grounding for the Offer stage.

## Where things live

- `src/agency/schemas.py` — Pydantic models for the structured output (`OfferPackage`)
- `src/agency/tools.py` — `@function_tool` functions (niche lists, benchmarks)
- `src/agency/agents/offer_agent.py` — conversational agent with tools + handoff
- `src/agency/agents/offer_summarizer_agent.py` — structured-output agent, handoff target
- `src/agency/cli.py` — interactive chat loop, prints tool calls/handoffs for visibility
- `tests/` — unit + agent-behavior tests (fake `Model`, zero real API calls)
- `docs/decisions/` — ADRs: the *why* behind significant, hard-to-reverse choices
- `docs/intent/` — confirmed product intent docs (captured via structured interviews)
- `context/` (this folder) — planning/context docs: this overview, coding standards, how an
  agent should operate in this repo, and the current/completed feature log

## Roadmap (capability map)

Five target stages: Offer, Lead Gen, Outbound, Qualify, Sales — each with its own bots/sub-agents.
Built incrementally, one module at a time, to keep each hands-on learning step isolated.

| Module id | Responsibility | Depends on | Status |
|---|---|---|---|
| testing-ci | Test framework + CI pipeline (applies to the existing Offer stage too) | — | Completed |
| observability | SDK tracing/observability setup | — | Completed |
| lead-gen | Lead Gen agent: finds/qualifies candidate leads via web search, hands off from Offer | testing-ci, observability | Not started |
| outbound | Outbound agent: generates dry-run emails/call scripts/sequences (never dispatched), hands off from Lead Gen | lead-gen | Not started |
| web-ui | Local web chat UI running the full Offer→Lead Gen→Outbound session (replaces/wraps the CLI) | lead-gen, outbound | Not started |
| qualify-sales-roadmap | Docs-only: architecture/roadmap for Qualify and Sales stages (not implemented) | lead-gen, outbound | Not started |

Build order: testing-ci, observability → lead-gen → outbound → web-ui → qualify-sales-roadmap

See [context/current-feature.md](current-feature.md) for what's actively being worked on and a
history of completed features, and [context/features/](features/) for the per-module spec/plan for
each one.

## Architecture decisions

Significant design choices and their alternatives are recorded in [docs/decisions](../docs/decisions):

- [ADR-001](../docs/decisions/ADR-001-openai-agents-sdk.md) — why the OpenAI Agents SDK over LangChain/CrewAI/raw API
- [ADR-002](../docs/decisions/ADR-002-handoff-for-structured-output.md) — why a handoff produces the structured output, not the main agent
- [ADR-003](../docs/decisions/ADR-003-v1-scope.md) — why v1 is one agent pair, CLI-only, with mocked tools (partially superseded, see Update note)

## Constraints (from intent)

- Local-only, no deployment/hosting needed; no auth or multi-tenancy
- Outbound generates realistic content but never actually dispatches anything
- Real-world grounding comes from web search, not paid data vendors
- Out of scope: hosting/deployment, real email/message sending, user accounts, building out
  Qualify/Sales beyond architecture, real CRM/calendar/ads integrations
