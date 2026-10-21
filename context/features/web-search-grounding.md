# Feature: web-search-grounding (Offer stage follow-up)

## Status
Not started

## Objective

Replace the Offer stage's fabricated mock data (`src/agency/tools.py`'s `list_candidate_niches` /
`get_niche_benchmarks`) with the Agents SDK's built-in `WebSearchTool`, so niche recommendations
and benchmarks are grounded in real, current web data instead of a hardcoded dict of three niches.
This closes the gap flagged in the Update note of
[ADR-003](../../docs/decisions/ADR-003-v1-scope.md).

Success: running the CLI with a real `OPENAI_API_KEY` and asking about any industry (not just the
three hardcoded ones) returns a niche recommendation grounded in actual web search results, with
the model citing what it found rather than looking up a fixed dict.

## Background / key SDK fact

`agents.WebSearchTool` is a **hosted tool** — the OpenAI Responses API executes the search
server-side; it is not a local Python function the SDK calls back into (unlike `@function_tool`).
Consequences for this repo:
- It only works with OpenAI models via the Responses API, and needs a real `OPENAI_API_KEY` — it
  cannot run against the existing `FakeModel` the way `@function_tool`s do, because `FakeModel`
  never talks to OpenAI's backend where the search actually executes.
- There is no Python function body to unit-test. `tools.py`'s current unit tests (calling the
  tool's `on_invoke_tool` directly) do not apply to `WebSearchTool`.
- The agent's instructions must change from "call `list_candidate_niches`/`get_niche_benchmarks`
  tool, read the structured dict back" to "search the web for X, synthesize findings yourself" —
  this is a prompting change, not just a tool swap.

## Scope

- Add `WebSearchTool` (from `agents`) to `offer_agent`'s `tools` list.
- Rewrite `offer_agent`'s instructions to direct it to use web search for candidate niches and
  benchmarks (avg job value, demand pattern, competition, pain points) instead of calling the old
  mock tools, while keeping the same conversational flow (clarify -> research -> recommend ->
  confirm -> handoff).
- Remove `list_candidate_niches` and `get_niche_benchmarks` from `offer_agent`'s tool list once
  `WebSearchTool` covers their purpose. Decide in Phase 1 whether `src/agency/tools.py` is deleted
  outright or kept temporarily behind a feature flag for offline/no-API-key demos (see Open
  question below) — default plan is to delete it, since real grounding is the whole point of this
  module.
- Update existing `FakeModel`-based agent behavior tests (`tests/agents/test_offer_agent.py`) so
  they no longer script the removed mock tool calls; add a test asserting `offer_agent.tools`
  includes a `WebSearchTool` instance.
- Document in README that the Offer stage now requires a real `OPENAI_API_KEY` to get real search
  results (no more API-key-free mock mode for this stage) — call out the tradeoff against the
  "no API key needed" CLI experience from before.
- Out of scope: Lead Gen's own web-search needs (tracked separately once that module starts,
  though it will reuse whatever pattern this module establishes), rate limiting / cost controls on
  search usage, caching search results.

## Open question (resolve before/at start of Phase 1)

Keep `src/agency/tools.py`'s mock functions around (unused by `offer_agent` but still tested) as a
reference/fallback, or delete them entirely now that `WebSearchTool` replaces their purpose?
Default: delete, per "Never do: ... mocked data... must be replaced with real data sources" intent
in ADR-003. Flag to the user if there's a reason to keep a no-API-key demo path.

## Task list

### Phase 1: Agent wiring
- [ ] Task 1: Resolve the open question above (delete vs. keep `tools.py`).
- [ ] Task 2: Update `src/agency/agents/offer_agent.py` — add `WebSearchTool()` to `tools`, remove
      `list_candidate_niches`/`get_niche_benchmarks`, rewrite `INSTRUCTIONS` to describe the new
      web-search-driven research flow (what to search for, how many sources/candidates to
      consider, still grounding the recommendation's math in what it finds).
- [ ] Task 3: If Task 1 decided to delete `tools.py`, remove the file and its dedicated unit tests
      (`tests/test_tools.py`); if kept, leave as-is but note in the module docstring that it is
      unused by any agent.

### Phase 2: Tests
- [ ] Task 4: Update `tests/agents/test_offer_agent.py` — drop any `FakeModel` scripting of the
      removed mock tool calls; add a test asserting `offer_agent.tools` contains a `WebSearchTool`
      instance (construction/wiring check, not a live search).
- [ ] Task 5: Confirm no test in the default suite makes a real network/OpenAI call (`WebSearchTool`
      must stay untriggered under `FakeModel`-driven tests).

### Phase 3: Docs
- [ ] Task 6: Update README to state the Offer stage needs a real `OPENAI_API_KEY` for web search
      (no more mock/offline mode for this stage), and briefly describe the manual smoke-test
      (`python -m agency.cli` with a real key, try an industry outside the old hardcoded three).
- [ ] Task 7: Update [context/project-overview.md](../project-overview.md)'s "What it does today"
      section (currently says research tools are mocked) and
      [docs/decisions/ADR-003](../../docs/decisions/ADR-003-v1-scope.md)'s Update note to record
      that this follow-up is done.

## Checkpoint: Complete

- [ ] `ruff check .` passes with zero errors
- [ ] `python3 -m pytest` passes with zero real API/network calls
- [ ] `offer_agent` uses `WebSearchTool` instead of the mocked niche/benchmark tools
- [ ] Manual smoke test with a real `OPENAI_API_KEY` against an industry not in the old hardcoded
      list produces a grounded recommendation
- [ ] README and ADR-003 updated to reflect real web-search grounding
- [ ] `context/current-feature.md` updated: this entry moved to "Completed features"
