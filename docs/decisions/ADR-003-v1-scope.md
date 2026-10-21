# ADR-003: Scope v1 to one agent pair, CLI interface, and mocked tools

## Status
Accepted; partially superseded 2026-10-20 (see Update below) — the mocked-tools part of this
decision no longer reflects the Offer stage's planned tooling.

## Date
2026-10-19

## Context
The target product (per the reference design) spans five stages: Offer, Lead Gen, Outbound,
Qualify, and Sales — each with its own bots/sub-agents. Building all of it at once, with real
integrations and a web UI, would be a large surface area for a first hands-on pass at agentic AI,
and would make it harder to isolate what was learned at each step.

## Decision
Scope the first build to:
- One agent pair: Offer Creation Bot + Offer Summarizer (see ADR-002) — the Offer stage only
- A CLI chat loop as the interface (no web server or frontend)
- Hardcoded mock tools (`list_candidate_niches`, `get_niche_benchmarks`) instead of real web
  search, CRM, or email APIs

## Alternatives Considered

### Scaffold all 5 stage-agents immediately
- Pros: Gives a fuller picture of the end product sooner
- Cons: Spreads learning thin across many agents before any single agentic concept (tools,
  structured output, handoffs) is well understood; higher risk of rework once early design
  decisions (e.g. ADR-002's handoff pattern) change
- Rejected: Too broad for a first iteration focused on learning

### Web UI (e.g. FastAPI backend + frontend) instead of CLI
- Pros: Closer to how the final product would actually be used
- Cons: Adds HTTP/server/frontend plumbing that is orthogonal to learning agent primitives
- Rejected: Unnecessary overhead for the current learning goal; can be added once the agent logic
  is solid

### Real integrations (live web search, CRM, email) from day one
- Pros: More realistic behavior and output
- Cons: Couples correctness of agent logic to external API availability, cost, and rate limits
  while still learning the SDK basics; harder to get deterministic, repeatable test conversations
- Rejected at the time: Mocked data gives fast, free, deterministic iteration while learning the
  SDK. (Revisited for the Offer stage specifically — see Update below.)

## Consequences
- Lead Gen, Outbound, Qualify, and Sales stage-agents are not built yet — explicitly deferred to
  future iterations once the Offer stage pattern is validated.
- No web UI, no persisted memory across separate CLI runs, and no input guardrails yet — also
  deferred (see README "Next steps").
- Mock tool data in `src/agency/tools.py` is fabricated for learning purposes and must be replaced
  with real data sources before any real-world/production use.

## Update (2026-10-20)
Per [docs/intent/full-pipeline-showcase.md](../intent/full-pipeline-showcase.md), this project's
goal shifted from a pure learning repo to a resume-ready showcase, and real-world grounding via web
search (`WebSearchTool`) was decided for the Offer stage specifically, superseding the "mocked
tools" part of this ADR's decision for that stage. `src/agency/tools.py` still uses the mocked
`list_candidate_niches`/`get_niche_benchmarks` functions as of this writing — switching them to
`WebSearchTool` is tracked as follow-up implementation work, not yet done.

The rest of this ADR's scope still holds as the current state: one agent pair, CLI interface, and
Lead Gen/Outbound/Qualify/Sales not yet built (now tracked concretely in
[context/project-overview.md](../../context/project-overview.md) rather than being open-ended).
