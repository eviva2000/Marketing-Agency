# Coding Standards

## Stack

- Python >= 3.10, `openai-agents` SDK, `pydantic` v2, `python-dotenv`
- Test framework: `pytest` (+ `pytest-cov`)
- Linter/formatter: `ruff` (target `py310`, line length 110)

## Commands

```
Install dev deps:  pip install -e ".[dev]"
Test:               python3 -m pytest
Test (coverage):    python3 -m pytest --cov=agency --cov-report=term-missing
Lint:               ruff check .
Format check:       ruff format --check .
```

**Gotcha:** bare `pytest` on `PATH` can resolve to a different (non-venv) install and fail with
`ImportError` on `agents`. Always invoke it as `python3 -m pytest` after activating `.venv`. `ruff`
does not have this problem.

## Style

- Module-level docstring one-liner at the top of each file, type hints on function signatures, no
  inline comments restating obvious code.
- Tests follow plain `pytest` convention — `def test_...():` functions, no test classes, one
  behavior asserted per test.

```python
def test_offer_package_requires_all_fields():
    with pytest.raises(ValidationError):
        OfferPackage(niche="Roofing")  # missing offer_summary/final_pitch
```

## Testing strategy

- **Unit tests** for `schemas.py` (Pydantic validation) and `tools.py` (function tool outputs) —
  no agent/LLM involved, fastest and most deterministic layer.
- **Agent behavior tests** use a hand-written `FakeModel` (`tests/conftest.py`) implementing
  `agents.models.interface.Model.get_response` to script canned responses (tool calls, handoffs,
  structured output) and drive a real `Agent`/`Runner`, so tests exercise real SDK wiring with zero
  real API calls.
- **No live-API tests.** Real OpenAI calls are out of scope for the default `pytest`/CI run (cost,
  flakiness, needing a secret). Manual smoke-testing against the real API is a separate, deliberate
  step, not part of the automated suite.
- No hard coverage percentage gate — meaningful tests over a coverage number. CI fails only on
  actual test/lint failures.

## OpenAI Agents SDK patterns

- `Agent`/`RunConfig` accept `model: str | Model` — this is what makes `FakeModel` possible.
- Handoff tool name: `agents.handoffs.Handoff.default_tool_name(agent)`.
- To unit-test a `@function_tool`-wrapped function directly, construct
  `agents.tool_context.ToolContext(context=None, tool_name=tool.name, tool_call_id="x",
  tool_arguments=json_args)` and `await tool.on_invoke_tool(ctx, json_args)`.
- Agents are mutable dataclasses; use `dataclasses.replace(agent, model=..., handoffs=[...])` in
  tests instead of mutating module-level singleton agents.
- `output_type`-structured agents require the scripted final message text to be valid JSON matching
  the schema, or the SDK raises `ModelBehaviorError: Invalid JSON when parsing model output` — this
  can surface on a *later* handed-off agent's turn, not just the immediate one.

## Boundaries

- **Always do:** run `ruff check .` and `python3 -m pytest` before considering a change done; add/
  update tests in the same change that adds/changes behavior.
- **Ask first:** adding new dev dependencies beyond `pytest`/`ruff`/`pytest-cov`; changing CI
  trigger conditions (e.g. scheduled runs, deploy steps).
- **Never do:** commit a real `OPENAI_API_KEY` or `.env`; add tests that call the real OpenAI API
  in the default `pytest`/CI run.
