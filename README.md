# Agentic Marketing Agency (Learning Project)

[![CI](https://github.com/eviva2000/Marketing-Agency/actions/workflows/ci.yml/badge.svg)](https://github.com/eviva2000/Marketing-Agency/actions/workflows/ci.yml)

A small agentic marketing agency built on the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/),
used as a hands-on introduction to tool calling, structured outputs, and multi-agent handoffs.

## What it does

1. **Offer Creation Bot** (conversational) interviews you about your target industry, uses the
   Agents SDK's `WebSearchTool` to research real candidate niches and benchmarks, and gives an
   opinionated recommendation grounded in what it finds.
2. Once you confirm a niche, it **hands off** to the **Offer Summarizer** agent, which reads the
   conversation and returns a structured `OfferPackage` (offer summary + ready-to-use pitch copy).
3. If you then ask it to find leads, the **same Offer Summarizer** hands off to the **Lead Gen
   Bot**, which uses `WebSearchTool` to find real, named candidate prospects matching the offer's
   target customer.
4. Once you confirm the list, it **hands off** to the **Lead List Summarizer**, which returns a
   structured `LeadList` (one entry per confirmed prospect, with contact info and an outreach
   angle).
5. Ask for outreach drafts and the **Outbound Bot** prepares a personalized email and call opener
   per confirmed lead. After review and approval, the **Outbound Summarizer** returns a structured
   `OutboundPackage`. The drafts are never sent.

`WebSearchTool` is a hosted tool that requires a real `OPENAI_API_KEY` (OpenAI Responses API) —
there is no API-key-free mock mode for the Offer or Lead Gen stages.

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

To use the local browser interface instead:

```bash
source .venv/bin/activate
python -m agency.web
```

Then open <http://127.0.0.1:8765>. The web interface keeps sessions in memory and requires the
same `OPENAI_API_KEY` as the CLI. It binds to loopback; messages and web searches use OpenAI
services, and outreach drafts are never sent.

Try: "I run a marketing agency focused on home services" → confirm the recommended niche → ask
for leads → confirm the list → ask for outreach drafts → review and approve the drafts.

## Tracing

Every CLI run is tagged with a `workflow_name` ("Agency Pipeline") and a `group_id` (the CLI session
id), so all turns of one conversation link into a single traced group.

- **Default:** traces export to the [OpenAI dashboard](https://platform.openai.com/traces)
  (requires `OPENAI_API_KEY`).
- **Local/offline:** set `AGENCY_TRACE_CONSOLE=1` to print traces/spans to stdout instead — no API
  key or network access needed.

```bash
AGENCY_TRACE_CONSOLE=1 python -m agency.cli
```

## Project layout

- `src/agency/schemas.py` — Pydantic models for `OfferPackage`, `LeadList`, and `OutboundPackage`
- `src/agency/agents/offer_agent.py` — conversational agent with `WebSearchTool` + handoff
- `src/agency/agents/offer_summarizer_agent.py` — structured-output agent, hands off to Lead Gen
- `src/agency/agents/lead_gen_agent.py` — conversational agent with `WebSearchTool` + handoff
- `src/agency/agents/lead_list_summarizer_agent.py` — structured-output agent, handoff target
- `src/agency/agents/outbound_agent.py` — conversational outreach drafting and review
- `src/agency/agents/outbound_summarizer_agent.py` — structured approved drafts
- `src/agency/observability.py` — tracing setup (console export toggle, `RunConfig` tagging)
- `src/agency/cli.py` — interactive chat loop, prints tool calls/handoffs for visibility
- `src/agency/web.py` and `src/agency/web_ui/` — local HTTP server and browser chat interface
- `context/` — planning/context docs: project overview, coding standards, how an agent should
  operate in this repo, and the current/completed feature log (start at
  [context/project-overview.md](context/project-overview.md))

## Architecture decisions

Significant design choices and their alternatives are recorded in [docs/decisions](docs/decisions):

- [ADR-001](docs/decisions/ADR-001-openai-agents-sdk.md) — why the OpenAI Agents SDK over LangChain/CrewAI/raw API
- [ADR-002](docs/decisions/ADR-002-handoff-for-structured-output.md) — why a handoff produces the structured output, not the main agent
- [ADR-003](docs/decisions/ADR-003-v1-scope.md) — why v1 is one agent pair, CLI-only, with mocked tools (now superseded for the Offer stage's tools — see the ADR's Update note)

## Next steps (not built yet)

- Qualify and Sales architecture roadmap
- Input guardrails and persisted sessions across separate CLI runs
