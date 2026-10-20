# Implementation Plan: testing-ci (module 1 of 6)

See [specs/SPEC-testing-ci.md](../specs/SPEC-testing-ci.md) for the full spec this plan implements.
Part of [specs/CAPABILITY-MAP.md](../specs/CAPABILITY-MAP.md).

## Overview

Add `pytest`/`ruff` as dev dependencies, a hand-written fake `Model` so agent tests run with zero
real OpenAI API calls, tests covering the existing Offer stage, and a GitHub Actions workflow that
runs lint + tests on every push/PR.

## Architecture Decisions

- Verified `agents.models.interface.Model` has a small interface (`get_response`,
  `stream_response`, `get_retry_advice`, `close`) — confirms a hand-written fake model is feasible
  for scripting deterministic agent responses in tests, per the spec.
- Linting (`ruff`) is bundled into this module rather than split out, since it shares the same dev
  dependency group and CI workflow file — splitting it would mean touching the same files twice.

## Task List

### Phase 1: Foundation
- [ ] Task 1: Add dev dependencies and pytest scaffold
- [ ] Task 2: Fake `Model` fixture for deterministic agent tests

### Checkpoint: Foundation
- [ ] `pip install -e ".[dev]"` succeeds
- [ ] `pytest` runs (even trivially) with `OPENAI_API_KEY` unset and no network calls

### Phase 2: Core Tests
- [ ] Task 3: Unit tests for `schemas.py` and `tools.py`
- [ ] Task 4: Agent behavior tests using the fake `Model` (offer_agent, offer_summarizer_agent)

### Checkpoint: Core Tests
- [ ] Full `pytest` suite passes locally with `OPENAI_API_KEY` unset
- [ ] Tests cover: schema validation, tool outputs (known + fallback cases), tool wiring on
      `offer_agent`, the handoff to `offer_summarizer_agent`, and `OfferPackage` structured output

### Phase 3: Lint + CI
- [ ] Task 5: Add `ruff` config and fix existing lint issues
- [ ] Task 6: GitHub Actions CI workflow
- [ ] Task 7: Update README with dev commands + CI badge

### Checkpoint: Complete
- [ ] `ruff check .` passes with zero errors
- [ ] `.github/workflows/ci.yml` runs lint + tests on push/PR to `main`
- [ ] README documents `pip install -e ".[dev]"`, `pytest`, `ruff check .`
- [ ] Ready for review

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Fake `Model` doesn't correctly simulate tool-call / handoff / structured-output response shapes, making tests pass without actually exercising real logic | High — false confidence | Task 2's acceptance criteria require the fake model to drive a real `Runner.run_sync` call and produce real `ToolCallItem`/`HandoffOutputItem`/structured `final_output`, not a hand-rolled fake `Runner` |
| `ruff` surfaces many pre-existing lint issues in `src/agency/` | Low — just cleanup work | Task 5 explicitly includes fixing issues found, scoped as part of this module, not deferred |
| GitHub Actions workflow untested until first real push/PR | Low | Task 6's verification includes local YAML validation; full confirmation happens on first PR once implemented |

## Open Questions

None.
