# Current Feature: web-search-grounding

## Active Spec

[web-search-grounding](features/web-search-grounding.md) — replace the Offer stage's mocked
`list_candidate_niches`/`get_niche_benchmarks` tools with the Agents SDK's `WebSearchTool`, per the
Update note in [ADR-003](../docs/decisions/ADR-003-v1-scope.md). **lead-gen** remains next up after
this per the build order in [context/project-overview.md](project-overview.md).

## Goals

- `offer_agent` uses `WebSearchTool` for real web-grounded niche research instead of a hardcoded
  mock dataset.
- No real API/network calls added to the default `pytest`/CI suite.

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

