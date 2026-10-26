# Feature: web-ui

## Status
Implemented; browser smoke check pending

## Objective

Add a local web chat interface for the existing Offer → Lead Gen → Outbound agency pipeline.
The project author should be able to demo one continuous session in a browser, see the agent's
responses and handoffs, confirm or refine each stage, and review the final structured outputs.
The UI wraps the existing Agents SDK flow; it does not add new marketing capabilities.

Success means a user can complete the Offer → Lead Gen → Outbound workflow in one browser
conversation, including reviewing and approving outreach drafts, while the server preserves the
current agent/session context between turns. The application runs locally only, and never sends
outreach.

## Assumptions to validate

- The browser UI is a local development/demo interface, not a hosted product.
- Offer, Lead Gen, Outbound behavior, agent instructions, schemas, and handoffs remain owned by
  the existing Python Agents SDK implementation.
- A single local user and one active conversation are sufficient for the initial release; there
  is no authentication, multi-tenancy, or account management.
- The server must keep `OPENAI_API_KEY` private and must not expose it to browser code or responses.
- Agent trace visibility should include tool calls and handoffs, matching the CLI's demo value,
  while hiding secrets and raw credential-bearing configuration.
- The initial UI supports text input and readable text/structured outputs. File uploads, voice,
  rich editing, and exporting are not required.

## Scope

- Build a browser chat interface that sends user turns to a local application server and displays
  assistant messages in conversation order.
- Reuse the existing Offer → Lead Gen → Outbound agents and SDK handoff chain rather than
  reimplementing agent behavior in the browser.
- Maintain a single conversation across turns, including the current agent and session state, so
  users can continue after each structured `OfferPackage`, `LeadList`, and `OutboundPackage`.
- Render structured outputs clearly, with readable lead and outreach-draft details.
- Show useful progress and handoff/tool activity so the demo makes the agent workflow visible.
- Provide pending, error, and retry states for a failed server/model request without discarding
  the conversation already displayed.
- Provide a clear way to start a fresh conversation and explain that doing so resets the local
  session.
- Run the app locally with documented setup and development commands.
- Keep the CLI available; this feature wraps/replaces it for the live browser demo but does not
  remove it.

Out of scope: deployment or hosting, authentication, multiple users or simultaneous sessions,
conversation history management across restarts, database-backed product persistence, real CRM or
email integrations, sending or scheduling outreach, Qualify/Sales agents, file uploads, and
mobile-native apps.

## Resolved design decisions

- Use the Python standard library HTTP server and static HTML/CSS/JavaScript; see
  [ADR-004](../../docs/decisions/ADR-004-local-web-demo.md). No framework dependencies are added.
- Return each assistant turn after completion. The browser shows a pending state while the server
  runs the existing synchronous pipeline.
- Give each conversation a random opaque ID, an in-memory `SQLiteSession`, and its own active-agent
  reference. Reset closes and removes that session; process exit clears all sessions.
- Display generic research activity and fixed agent handoff names. Never display tool arguments,
  tool results, hidden instructions, or raw exceptions.
- Keep browser automation out of the dependency set. Add a browser test runner only when a browser
  runtime is available and the project approves the additional dependency/tooling.

## Task list

### Phase 1: Resolve implementation boundary

- [x] Task 1: Inspect the existing agent/CLI session behavior and choose the local web framework,
      request/response contract, and session-id strategy. The implementation uses the Python
      standard library and in-memory SDK sessions; see [ADR-004](../../docs/decisions/ADR-004-local-web-demo.md).
- [x] Task 2: Define UI states and the safe event/output contract, including structured results,
      handoffs, tool activity, errors, reset behavior, and session isolation.

### Phase 2: Local server integration

- [x] Task 3: Add a local server entry point that invokes the existing pipeline with one in-memory
      SDK session per browser conversation.
- [x] Task 4: Add request validation, safe error handling, and tests for turn handling, session
      continuation/reset, and output serialization using fake turn runners and no real API calls.
- [x] Task 5: Expose only the events and output data required by the UI; keep secrets and internal
      instructions server-side.

### Phase 3: Browser interface

- [x] Task 6: Build an accessible, responsive chat view with message history, composer, pending
      state, retryable errors, and fresh-conversation action.
- [x] Task 7: Render `OfferPackage`, `LeadList`, and `OutboundPackage` as readable structured
      content, and make handoffs/tool activity visible without showing sensitive internals.
- [ ] Task 8: Add browser-level coverage for a representative conversation, structured output,
      reset, and failure handling using fake model responses. No browser runtime is currently
      available in the development environment; the HTTP contract and session manager are covered
      by Python tests.

### Phase 4: Documentation and checkpoint

- [x] Task 9: Document installation, local run, required `OPENAI_API_KEY`, and browser usage; update
      README and `context/project-overview.md`.
- [ ] Task 10: Run lint, unit/agent tests, and browser checks; manually smoke-test Offer → Lead Gen
      → Outbound in the browser with a real API key and verify no outreach is sent. Python tests,
      lint, and local HTTP checks pass; the browser and live model checks remain pending.
- [ ] Task 11: Mark this feature complete and move its entry to completed history in
      `context/current-feature.md` after the checkpoint passes.

## Checkpoint

- [ ] A local browser session can complete Offer → Lead Gen → Outbound while preserving context
      across turns and SDK handoffs.
- [ ] The UI displays all three structured output types and makes tool/handoff activity legible.
- [ ] A new conversation resets its session without altering another session's data.
- [ ] Loading and recoverable error states work without losing displayed conversation history.
- [ ] The browser never receives the API key, hidden instructions, or raw internal exception data.
- [ ] Tests cover server behavior and the primary browser workflow without real API calls.
- [x] The local HTTP server serves the UI and enforces same-origin JSON session requests.
- [x] Python tests cover session continuation, active-agent handoffs, structured output, isolation,
      reset, safe activity output, and generic failure handling.
- [ ] Manual live smoke check completes the workflow and confirms no sending mechanism exists.
- [x] README, project overview, and current-feature log reflect the implemented UI.

## Commands

Run the local server with `python -m agency.web` after installing the package and setting
`OPENAI_API_KEY` in `.env`. Run checks with `python3 -m pytest` and `ruff check .`. The app has no
frontend build step or browser-test dependency.

## Boundaries

- **Always:** Reuse the existing agent pipeline; keep the API key server-side; validate incoming
  requests; preserve the local-only constraint; keep outreach draft-only; cover behavior with fake
  model tests that make no real API calls.
- **Ask first:** Hosting/deployment, authentication or multiple users, persistent history across
  restarts, real integrations or delivery, and changes to the Offer/Lead Gen/Outbound behavior.
- **Never:** Send or schedule outreach; expose secrets or hidden instructions to the browser; add
  real API calls to the default test suite.
