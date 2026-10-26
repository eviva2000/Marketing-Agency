# ADR-004: Use a standard-library server for the local browser demo

## Status
Accepted

## Date
2026-10-26

## Context

The Web UI is a local interview/demo surface around an existing Python Agents SDK pipeline. The
repository has no web framework or frontend toolchain, and the project intent rules out hosting,
accounts, and multi-user operation. The UI needs to keep agent handoffs and SDK session state on the
Python side, while exposing structured outputs and safe activity to the browser.

## Decision

Use Python's standard-library `http.server` for a loopback-only server and static HTML, CSS, and
JavaScript for the browser client. Keep each conversation in an in-memory `SQLiteSession` and an
in-memory registry that also tracks its active agent. Generate an opaque browser session token and
a separate trace grouping ID. Serve only fixed, packaged assets; accept same-origin JSON requests;
and return concise user-facing errors without internal exception details.

## Alternatives considered

### Add a Python web framework and a frontend build toolchain

- Pros: Provides routing, request validation, and richer frontend conventions out of the box.
- Cons: Adds runtime and development dependencies for a single-user, local-only demo surface and
  requires introducing a second application stack alongside the existing CLI.
- Rejected: The current server surface is small enough for the standard library, and avoiding a
  new stack keeps installation and local use simple.

### Put agent/session logic in the browser

- Pros: Could reduce the server to static file hosting.
- Cons: Would expose API credentials and duplicate or weaken the existing Python handoff/session
  behavior.
- Rejected: Agent execution and credentials remain server-side.

## Consequences

- No web-framework, JavaScript-framework, or browser-test dependencies are required.
- The server is intended for a local demo, not deployment or multi-user service.
- Conversation state is lost when a session is reset or the process exits.
- Browser-level regression checks may need a separately available browser runtime; default Python
  tests cover the HTTP contract and agent-session management without live API calls.
