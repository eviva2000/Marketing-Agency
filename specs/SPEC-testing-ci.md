# Spec: testing-ci

Part of [CAPABILITY-MAP.md](CAPABILITY-MAP.md). Build order position: 1 (foundation, no
dependencies). Applies retroactively to the existing Offer stage as well as future modules.

## Objective

Give the repo automated tests and a CI pipeline so it reads as a professional, verifiable
codebase to a technical interviewer — not just working code, but code with proof it works. Covers
the existing Offer Creation Bot + Offer Summarizer today, and is the foundation every later module
(`lead-gen`, `outbound`, `web-ui`) builds its own tests on top of.

Success here means: a reviewer can clone the repo, run one command, and see tests + lint pass; and
a GitHub Actions badge/workflow shows the same thing happens on every push without them lifting a
finger.

## Tech Stack

- **Test framework:** `pytest` (new dev dependency; nothing currently installed)
- **Linter:** `ruff` (new dev dependency; lint + format check)
- **CI platform:** GitHub Actions (`.github/workflows/ci.yml`)
- **Deterministic agent testing:** a hand-written fake `Model` implementation (the SDK's `Model`
  protocol accepts `str | Model` on both `Agent(model=...)` and `RunConfig(model=...)`), so tests
  never call the real OpenAI API — no API key needed in CI, no network flakiness, no cost.

## Commands

```
Install dev deps: pip install -e ".[dev]"
Test:              pytest
Test (coverage):   pytest --cov=agency --cov-report=term-missing
Lint:              ruff check .
Format check:      ruff format --check .
```

## Project Structure

```
tests/
  conftest.py          → shared fixtures (e.g. the fake Model, a fake Session)
  test_schemas.py       → OfferPackage/OfferSummary/FinalPitch validation tests
  test_tools.py          → unit tests for function tools (and, later, lead-gen/outbound tools)
  agents/
    test_offer_agent.py            → offer_agent behavior against the fake model
    test_offer_summarizer_agent.py → offer_summarizer_agent structured-output behavior
.github/
  workflows/
    ci.yml             → runs lint + tests on every push/PR
```

## Code Style

Match the existing repo conventions already visible in `src/agency/`: module-level docstring
one-liner, type hints on function signatures, no inline comments restating obvious code. Test
files follow `pytest` convention — plain `def test_...():` functions (no test classes), one
behavior asserted per test:

```python
def test_offer_package_requires_all_fields():
    with pytest.raises(ValidationError):
        OfferPackage(niche="Roofing")  # missing offer_summary/final_pitch
```

## Testing Strategy

- **Unit tests** for `schemas.py` (Pydantic validation) and `tools.py` (function tool outputs) —
  no agent/LLM involved, fastest and most deterministic layer.
- **Agent behavior tests** using the fake `Model` to script canned LLM responses (tool calls,
  handoffs, final structured output) and assert the `Agent`/`Runner` wiring behaves correctly —
  e.g. `offer_agent` has the right tools and hands off to `offer_summarizer_agent`;
  `offer_summarizer_agent` is constructed with `output_type=OfferPackage`.
- **No live-API tests.** Real OpenAI calls are explicitly out of scope for CI (cost, flakiness,
  needing a secret). A short manual "smoke test" section in the README covers real end-to-end runs.
- **Coverage:** no hard percentage gate for this learning/portfolio project — the goal is
  meaningful tests over a coverage number. CI fails only on actual test/lint failures, not on a
  coverage threshold.

## Boundaries

- **Always do:** run `ruff check .` and `pytest` before considering a module's implementation
  phase done; add/update tests in the same task that adds/changes behavior.
- **Ask first:** adding new dev dependencies beyond `pytest`/`ruff`/`pytest-cov`; changing the CI
  trigger conditions (e.g. adding scheduled runs, deploy steps).
- **Never do:** commit a real `OPENAI_API_KEY` or `.env` to the repo or to CI config; add tests
  that call the real OpenAI API in the default `pytest`/CI run.

## Success Criteria

- `pip install -e ".[dev]"` installs `pytest`, `ruff`, `pytest-cov` via a new `[project.optional-dependencies].dev` group in `pyproject.toml`
- `pytest` passes locally with zero real API calls made (verified by running with `OPENAI_API_KEY` unset)
- `ruff check .` passes with zero errors
- `.github/workflows/ci.yml` exists and runs lint + tests on push and PR to `main`
- Existing `schemas.py`, `tools.py`, `offer_agent.py`, `offer_summarizer_agent.py` all have test coverage

## Open Questions

- None — confirmed via assumptions check in this conversation.
