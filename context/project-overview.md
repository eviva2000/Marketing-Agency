# Project Overview

## What this is

A small agentic marketing agency built on the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/),
started as a hands-on introduction to tool calling, structured outputs, and multi-agent handoffs,
now being leveled up into a resume-ready showcase of agentic-systems engineering (see
[full-pipeline-showcase intent](../docs/intent/full-pipeline-showcase.md) for the full rationale).

## What it does today

1. **Offer Creation Bot** (conversational) interviews the user about their target industry, uses
   `WebSearchTool` to research real candidate niches and benchmarks, and gives an opinionated
   recommendation grounded in what it finds.
2. Once the user confirms a niche, it **hands off** to the **Offer Summarizer** agent, which reads
   the conversation and returns a structured `OfferPackage` (offer summary + ready-to-use pitch
   copy).
3. If the user then asks to find leads, the same Offer Summarizer **hands off** to the **Lead Gen
   Bot**, which uses `WebSearchTool` to find real, named candidate prospects matching the offer's
   target customer; once confirmed, it hands off to the **Lead List Summarizer**, which returns a
   structured `LeadList`.
4. The pipeline runs through a CLI chat loop (`python -m agency.cli`) and a local browser UI
   (`python -m agency.web`). The user can ask the **Lead List Summarizer** to hand off to the
   **Outbound Bot**, which drafts an email and call opener for each confirmed lead. After review,
   the **Outbound Summarizer** returns a structured `OutboundPackage`; no outreach is sent.

`WebSearchTool` is a hosted tool (OpenAI Responses API) — the Offer and Lead Gen stages require a
real `OPENAI_API_KEY` for any run, per the Update note in
[ADR-003](../docs/decisions/ADR-003-v1-scope.md).

## Where things live

- `src/agency/schemas.py` — Pydantic models for `OfferPackage`, `LeadList`, `OutboundPackage`
- `src/agency/agents/offer_agent.py` — conversational agent with `WebSearchTool` + handoff
- `src/agency/agents/offer_summarizer_agent.py` — structured-output agent, hands off to Lead Gen
- `src/agency/agents/lead_gen_agent.py` — conversational agent with `WebSearchTool` + handoff
- `src/agency/agents/lead_list_summarizer_agent.py` — structured-output agent, handoff target
- `src/agency/agents/outbound_agent.py` — conversational outreach drafting and review
- `src/agency/agents/outbound_summarizer_agent.py` — structured approved outreach
- `src/agency/cli.py` — interactive chat loop, prints tool calls/handoffs for visibility
- `src/agency/web.py` and `src/agency/web_ui/` — local HTTP server and browser chat interface
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
| lead-gen | Lead Gen agent: finds/qualifies candidate leads via web search, hands off from Offer | testing-ci, observability | Completed |
| outbound | Outbound agent: generates reviewed email/call drafts (never dispatched), hands off from Lead Gen | lead-gen | Completed |
| web-ui | Local web chat UI running the full Offer→Lead Gen→Outbound session (wraps the CLI pipeline) | lead-gen, outbound | Implemented; browser smoke check pending |
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
- [ADR-004](../docs/decisions/ADR-004-local-web-demo.md) — why the local browser demo uses the Python standard library

## Constraints (from intent)

- Local-only, no deployment/hosting needed; no auth or multi-tenancy
- Outbound generates realistic content but never actually dispatches anything
- Real-world grounding comes from web search, not paid data vendors
- Out of scope: hosting/deployment, real email/message sending, user accounts, building out
  Qualify/Sales beyond architecture, real CRM/calendar/ads integrations
