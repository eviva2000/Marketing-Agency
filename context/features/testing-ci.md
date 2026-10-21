# Feature: testing-ci (module 1 of 6)

## Status
Completed

## Objective

Give the repo automated tests and a CI pipeline so it reads as a professional, verifiable
codebase — proof it works, not just working code. Covers the existing Offer Creation Bot + Offer
Summarizer, and is the foundation every later module (`lead-gen`, `outbound`, `web-ui`) builds its
own tests on top of.

Success: a reviewer can clone the repo, run one command, and see tests + lint pass; a GitHub
Actions badge/workflow shows the same thing happens on every push.

See [context/coding-standards.md](../coding-standards.md) for the stack, commands, and testing
strategy this module established (still the repo-wide convention today).

## Project structure delivered

```
tests/
  conftest.py          → shared fixtures (the fake Model)
  test_schemas.py       → OfferPackage/OfferSummary/FinalPitch validation tests
  test_tools.py          → unit tests for function tools
  agents/
    test_offer_agent.py            → offer_agent behavior against the fake model
    test_offer_summarizer_agent.py → offer_summarizer_agent structured-output behavior
.github/
  workflows/
    ci.yml             → runs lint + tests on every push/PR
```

## Task list (all completed)

### Phase 1: Foundation
- [x] Task 1: Add dev dependencies and pytest scaffold
- [x] Task 2: Fake `Model` fixture for deterministic agent tests

### Phase 2: Core Tests
- [x] Task 3: Unit tests for `schemas.py` and `tools.py`
- [x] Task 4: Agent behavior tests using the fake `Model` (offer_agent, offer_summarizer_agent)

### Phase 3: Lint + CI
- [x] Task 5: Add `ruff` config and fix existing lint issues
- [x] Task 6: GitHub Actions CI workflow
- [x] Task 7: Update README with dev commands + CI badge

## Architecture decisions made during this module

- Verified `agents.models.interface.Model` has a small interface (`get_response`,
  `stream_response`, `get_retry_advice`, `close`) — confirmed a hand-written fake model was
  feasible for scripting deterministic agent responses in tests.
- Linting (`ruff`) was bundled into this module rather than split out, since it shares the same dev
  dependency group and CI workflow file.

## Checkpoint: Complete

- [x] `ruff check .` passes with zero errors
- [x] `.github/workflows/ci.yml` runs lint + tests on push/PR to `main`
- [x] README documents `pip install -e ".[dev]"`, `pytest`, `ruff check .`
- [x] Existing `schemas.py`, `tools.py`, `offer_agent.py`, `offer_summarizer_agent.py` all have test
      coverage
