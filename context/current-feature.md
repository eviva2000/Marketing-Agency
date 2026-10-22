# Current Feature: outbound

## Active Spec

[Outbound](features/outbound.md) — implemented in the CLI and verified with a focused live run.
The full Offer → Lead Gen → Outbound smoke check remains before marking the module complete.

## Notes

- Each entry below moves here from "Active" once its checkpoint passes (tests + lint green,
  success criteria met) — see [context/ai-interaction.md](ai-interaction.md) for the full workflow.

## History

- [Offer Stage](../docs/decisions/ADR-001-openai-agents-sdk.md) — Offer Creation Bot + Offer
  Summarizer agent pair, CLI chat loop, mocked research tools. Predates the per-module spec/plan
  convention below — see also [ADR-002](../docs/decisions/ADR-002-handoff-for-structured-output.md)
  and [ADR-003](../docs/decisions/ADR-003-v1-scope.md) (Completed).
- [Testing & CI](features/testing-ci.md) — `pytest` + `ruff` + GitHub Actions CI added, covering
  the Offer stage with zero real API calls (Completed).
- [Observability](features/observability.md) — SDK tracing wired into the CLI (`RunConfig`
  workflow name/group id) with a console-export fallback for API-key-free local runs, covered by
  tests using an in-memory `TracingProcessor` (Completed).
- [Web Search Grounding](features/web-search-grounding.md) — replaced the Offer stage's mocked
  `list_candidate_niches`/`get_niche_benchmarks` tools with the Agents SDK's `WebSearchTool`;
  Offer stage now requires a real `OPENAI_API_KEY` for any run (Completed).
- [Lead Gen](features/lead-gen.md) — `lead_gen_agent` (`WebSearchTool`, conversational) and
  `lead_list_summarizer_agent` (`output_type=LeadList`), chained from `offer_summarizer_agent` via
  a handoff that coexists with its `output_type=OfferPackage`; manually smoke-tested end to end
  with a real `OPENAI_API_KEY` (Completed).

