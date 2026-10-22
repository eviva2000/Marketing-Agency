# Feature: lead-gen

## Status
Completed

## Objective

Add a Lead Gen stage that takes the confirmed `OfferPackage` from the Offer stage and finds real,
named candidate businesses/prospects matching the offer's target customer, using web search for
grounding (same approach as the Offer stage, per
[web-search-grounding](web-search-grounding.md)). Output a structured list of qualified leads
(name, how to find/contact them, why they fit, a suggested outreach angle) that the later Outbound
stage will consume.

Success: running the CLI through Offer → confirm niche → Offer Summarizer produces an
`OfferPackage`, then the Lead Gen stage takes over, searches the web for real prospects matching
that offer's target customer, and returns a structured list of qualified leads grounded in what it
found (not fabricated names/companies).

## Background / key design question

The Offer stage ends when `offer_summarizer_agent` (which has `output_type=OfferPackage`) returns
its structured output — it has no `handoffs` of its own, so the SDK can't auto-chain into Lead Gen
on the same turn via a handoff tool call. Two options:

1. **CLI-level chaining (default plan):** when `cli.py` sees `final_output` is an `OfferPackage`,
   switch `current_agent` to a new `lead_gen_agent` and seed its next turn with the package
   (e.g. serialize it into the user-visible prompt/context), rather than an SDK handoff tool call.
2. **SDK handoff:** give `offer_summarizer_agent` a `handoffs=[lead_gen_agent]` list. Risk (per
   existing SDK-pattern notes in `coding-standards.md`): an agent with both `output_type` and
   `handoffs` is an untested combination here — needs a `FakeModel`-driven spike in Phase 1 to
   confirm the SDK actually supports "produce structured output, then still offer a handoff tool"
   before committing to this path.

Resolve in Phase 1 with a quick spike against `FakeModel`; default to option 1 if option 2 proves
awkward or unsupported.

**Resolved (Phase 1 spike):** Option 2 works. Spiked an `Agent(output_type=Foo, handoffs=[target])`
against `FakeModel` scripted to return a handoff tool call — the SDK happily hands off instead of
enforcing the output schema on that turn (`result.last_agent` became the handoff target, no
schema-validation error). So `offer_summarizer_agent` gets `handoffs=[lead_gen_agent]` added
alongside its existing `output_type=OfferPackage`: first turn after niche confirmation it produces
the structured `OfferPackage`; on a later turn, once the user asks to find leads, the same agent
instance calls the handoff tool instead of re-emitting the schema. This needs no special-casing in
`cli.py` beyond what already exists (the loop already does `current_agent = result.last_agent`
every turn) — pretty-printing `LeadList` is the only CLI change required.

## Scope

- New `src/agency/agents/lead_gen_agent.py` — conversational agent, `WebSearchTool()`-equipped,
  takes the confirmed niche + offer summary (from `OfferPackage`) and searches for real candidate
  businesses/prospects matching the target customer described in `OfferSummary.who`. Presents
  findings conversationally, lets the user ask for more/fewer or refine criteria, then hands off
  to a summarizer once the user confirms the list.
- New `src/agency/agents/lead_list_summarizer_agent.py` — structured-output agent (mirrors
  `offer_summarizer_agent`), reads the conversation and produces a `LeadList`.
- New schemas in `src/agency/schemas.py`: `Lead` (name, source/how-found, contact angle, fit
  reasoning, suggested outreach angle) and `LeadList` (niche, `list[Lead]`).
- Wire the Offer → Lead Gen transition per whichever option is chosen above.
- Update `src/agency/cli.py` only as needed for the chosen transition approach (e.g. handling a
  new structured output type in `_print_final_output`).
- Agent behavior tests using `FakeModel` (zero real API calls), following the existing pattern in
  `tests/agents/test_offer_agent.py` / `test_offer_summarizer_agent.py`.
- Out of scope: actually contacting/emailing leads (that's Outbound), real CRM integration,
  deduplication/persistence of leads across runs, lead scoring beyond a qualitative fit reason.

## Task list

### Phase 1: Design spike
- [x] Task 1: Spike the `output_type` + `handoffs` combination on `offer_summarizer_agent` against
      `FakeModel` to resolve the open design question above. Record the outcome here.
- [x] Task 2: Add `Lead` / `LeadList` schemas to `src/agency/schemas.py` with unit tests
      (`tests/test_schemas.py`).

### Phase 2: Agents
- [x] Task 3: Add `src/agency/agents/lead_gen_agent.py` (`WebSearchTool`, instructions to search
      for real prospects matching the offer's target customer, confirm list with user, handoff to
      summarizer).
- [x] Task 4: Add `src/agency/agents/lead_list_summarizer_agent.py` (`output_type=LeadList`,
      mirrors `offer_summarizer_agent`'s structure).
- [x] Task 5: Wire the Offer → Lead Gen transition per the Phase 1 decision.

### Phase 3: Tests + CLI
- [x] Task 6: Agent behavior tests for `lead_gen_agent` / `lead_list_summarizer_agent` using
      `FakeModel`, mirroring `tests/agents/test_offer_agent.py` /
      `test_offer_summarizer_agent.py`.
- [x] Task 7: Update `cli.py` if needed (e.g. `_print_final_output` handling `LeadList`) and verify
      `python3 -m pytest` / `ruff check .` pass.

### Phase 4: Docs
- [x] Task 8: Update README with the new Lead Gen stage and its `OPENAI_API_KEY` requirement
      (same as Offer).
- [x] Task 9: Update `context/project-overview.md`'s "What it does today" section and the roadmap
      table status for `lead-gen`.

## Checkpoint: Complete

- [x] `ruff check .` passes with zero errors
- [x] `python3 -m pytest` passes with zero real API/network calls
- [x] Lead Gen stage produces a structured `LeadList` grounded in real web search results
- [x] Manual smoke test with a real `OPENAI_API_KEY`: run the CLI through Offer → confirm a niche →
      Lead Gen returns real, named candidate prospects for that niche
- [x] README and `context/project-overview.md` updated
- [x] `context/current-feature.md` updated: this entry moved to "Completed features"
