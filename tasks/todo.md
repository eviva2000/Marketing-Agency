# Todo: testing-ci (module 1 of 6)

See `tasks/plan.md` and `specs/SPEC-testing-ci.md` for full context.

## Phase 1: Foundation

### Task 1: Add dev dependencies and pytest scaffold

**Description:** Add a `[project.optional-dependencies].dev` group (`pytest`, `pytest-cov`,
`ruff`) to `pyproject.toml` and create the `tests/` directory with one trivial sanity test to
prove the scaffold works.

**Acceptance criteria:**
- [ ] `pip install -e ".[dev]"` installs `pytest`, `pytest-cov`, `ruff`
- [ ] `tests/test_sanity.py` exists with one trivial passing assertion
- [ ] `pytest` discovers and runs it successfully

**Verification:**
- [ ] `pytest` exits 0
- [ ] Manual check: `pip list` shows the three dev packages installed

**Dependencies:** None

**Files likely touched:**
- `pyproject.toml`
- `tests/test_sanity.py`

**Estimated scope:** Small: 1-2 files

---

### Task 2: Fake `Model` fixture for deterministic agent tests

**Description:** Implement a `FakeModel` class (in `tests/conftest.py`) that satisfies the SDK's
`agents.models.interface.Model` protocol, scriptable with a queue of canned `ModelResponse` values
(messages, tool calls, structured output) so agent tests exercise real `Agent`/`Runner` logic
without calling the real OpenAI API.

**Acceptance criteria:**
- [ ] `FakeModel` implements `get_response` (and `stream_response`/`close`/`get_retry_advice` as
      required by the protocol) returning pre-scripted `ModelResponse` objects in sequence
- [ ] A pytest fixture exposes `FakeModel` so tests can pass `model=fake_model` to an `Agent` or
      via `RunConfig`
- [ ] A smoke test constructs a trivial `Agent(model=FakeModel([...]))`, runs it via
      `Runner.run_sync`, and asserts the scripted final output is returned

**Verification:**
- [ ] `pytest tests/test_fake_model.py` (or equivalent) passes
- [ ] Confirmed zero network calls made (e.g. no `OPENAI_API_KEY` set in the test environment)

**Dependencies:** Task 1

**Files likely touched:**
- `tests/conftest.py`

**Estimated scope:** Medium: 1 file, but requires understanding the `Model` protocol's return
types (`ModelResponse`, tool-call items) correctly

---

## Phase 2: Core Tests

### Task 3: Unit tests for `schemas.py` and `tools.py`

**Description:** Add unit tests for the Pydantic models in `schemas.py` (valid construction,
missing-field validation errors) and the function tools in `tools.py` (`list_candidate_niches`,
`get_niche_benchmarks`), covering both known-key and fallback/generic paths. No agent/LLM involved.

**Acceptance criteria:**
- [ ] `test_schemas.py` covers: valid `OfferPackage` construction, and a `ValidationError` when a
      required field is missing
- [ ] `test_tools.py` covers: `list_candidate_niches("home services")` returns the expected
      curated list, an unknown industry returns the generic fallback list, `get_niche_benchmarks`
      behaves the same way for known vs. unknown niches (case-insensitive lookup included)

**Verification:**
- [ ] `pytest tests/test_schemas.py tests/test_tools.py` passes

**Dependencies:** Task 1

**Files likely touched:**
- `tests/test_schemas.py`
- `tests/test_tools.py`

**Estimated scope:** Small: 2 files

---

### Task 4: Agent behavior tests using the fake `Model`

**Description:** Using `FakeModel` from Task 2, test that `offer_agent` calls its tools and hands
off to `offer_summarizer_agent` correctly, and that `offer_summarizer_agent` returns a well-formed
`OfferPackage` as `final_output`.

**Acceptance criteria:**
- [ ] A test scripts `FakeModel` to call `list_candidate_niches`/`get_niche_benchmarks` then
      trigger a handoff; asserts a `HandoffOutputItem` with `target_agent.name ==
      "Offer Summarizer"` appears in `result.new_items`
- [ ] A test scripts `FakeModel` to return structured output matching `OfferPackage`; asserts
      `result.final_output` is an `OfferPackage` instance with the expected fields

**Verification:**
- [ ] `pytest tests/agents/` passes
- [ ] Full suite (`pytest`) passes with `OPENAI_API_KEY` unset

**Dependencies:** Task 2

**Files likely touched:**
- `tests/agents/test_offer_agent.py`
- `tests/agents/test_offer_summarizer_agent.py`

**Estimated scope:** Medium: 2 files

---

## Checkpoint: Core Tests
- [ ] Full `pytest` suite passes locally with `OPENAI_API_KEY` unset
- [ ] Tests cover schema validation, tool outputs, tool wiring, handoff, and structured output

---

## Phase 3: Lint + CI

### Task 5: Add `ruff` config and fix existing lint issues

**Description:** Add a `[tool.ruff]` section to `pyproject.toml` (target Python 3.10, reasonable
line length) and fix any lint issues `ruff check .` surfaces in `src/agency/` and `tests/`.

**Acceptance criteria:**
- [ ] `[tool.ruff]` config exists in `pyproject.toml`
- [ ] `ruff check .` passes with zero errors

**Verification:**
- [ ] `ruff check .` exits 0
- [ ] `pytest` still passes after any lint-driven code changes

**Dependencies:** Task 1

**Files likely touched:**
- `pyproject.toml`
- possibly minor fixes across `src/agency/*.py`

**Estimated scope:** Small: 1-3 files

---

### Task 6: GitHub Actions CI workflow

**Description:** Add `.github/workflows/ci.yml` that installs dev dependencies and runs
`ruff check .` and `pytest` on push and pull request to `main`.

**Acceptance criteria:**
- [ ] Workflow triggers on `push` and `pull_request` to `main`
- [ ] Workflow steps: checkout, set up Python, `pip install -e ".[dev]"`, `ruff check .`, `pytest`
- [ ] No secrets required (no `OPENAI_API_KEY` reference anywhere in the workflow)

**Verification:**
- [ ] YAML is valid (e.g. `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`)
- [ ] Manual check: steps mirror the exact local commands from Tasks 1/5 so local and CI behavior match

**Dependencies:** Task 1, Task 5, Task 4

**Files likely touched:**
- `.github/workflows/ci.yml`

**Estimated scope:** Small: 1 file

---

### Task 7: Update README with dev commands and CI badge

**Description:** Add a "Development" section to README.md documenting
`pip install -e ".[dev]"`, `pytest`, `ruff check .`, and add a CI status badge referencing the new
workflow.

**Acceptance criteria:**
- [ ] README has a "Development" section with the three commands
- [ ] CI badge markdown is present near the top of README.md

**Verification:**
- [ ] Manual check: badge markdown syntax is correct (will render once pushed)

**Dependencies:** Task 6

**Files likely touched:**
- `README.md`

**Estimated scope:** Small: 1 file

## Checkpoint: Complete
- [ ] All 7 tasks checked off
- [ ] `ruff check .` and `pytest` both pass locally
- [ ] `.github/workflows/ci.yml` valid and mirrors local commands
- [ ] Ready for review
