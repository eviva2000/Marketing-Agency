# Capability Map: Full-Pipeline Showcase

Approved 2026-10-20. Source intent: [docs/intent/full-pipeline-showcase.md](../docs/intent/full-pipeline-showcase.md).

| Module id | Responsibility | Depends on |
|---|---|---|
| testing-ci | Test framework + CI pipeline (applies to existing Offer stage too) | — |
| observability | SDK tracing/observability setup | — |
| lead-gen | Lead Gen agent: finds/qualifies candidate leads via web search, hands off from Offer | testing-ci, observability |
| outbound | Outbound agent: generates dry-run emails/call scripts/sequences (never dispatched), hands off from Lead Gen | lead-gen |
| web-ui | Local web chat UI running the full Offer→Lead Gen→Outbound session (replaces/wraps the CLI) | lead-gen, outbound |
| qualify-sales-roadmap | Docs-only: architecture/roadmap for Qualify and Sales stages (not implemented) | lead-gen, outbound |

Build order: testing-ci, observability → lead-gen → outbound → web-ui → qualify-sales-roadmap

Each module gets its own spec at `specs/SPEC-<module-id>.md`, produced via Specify → Plan → Tasks
→ Implement, in build order.
