# Current Feature: None (next: Lead Gen)

## Active Spec

None in progress. Next up per the build order in
[context/project-overview.md](project-overview.md): **lead-gen** (Lead Gen agent) — no spec
written yet.

## Goals

- (none yet — filled in once the lead-gen spec is written)

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

