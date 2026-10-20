# Project Plan

Running log of planning steps for this project. Each entry is a step as it's planned/decided,
in chronological order. Significant architectural decisions get their own ADR in
[docs/decisions](decisions/) and are linked from here.

## Steps

1. **Scope v1** — one agent pair (Offer Creation Bot + Offer Summarizer), CLI interface, mocked
   tools. See [ADR-003](decisions/ADR-003-v1-scope.md).
2. **Pick agent framework** — OpenAI Agents SDK. See [ADR-001](decisions/ADR-001-openai-agents-sdk.md).
3. **Design the Offer stage flow** — conversational Offer Creation Bot hands off to a structured
   Offer Summarizer agent instead of one agent doing both. See
   [ADR-002](decisions/ADR-002-handoff-for-structured-output.md).

## Not yet planned in detail

- Real tools (web search, CRM, email) to replace mocks
- Additional stage agents (Lead Gen, Outbound, Qualify, Sales)
- Input guardrails and persisted sessions across CLI runs
