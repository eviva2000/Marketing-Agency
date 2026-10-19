# ADR-001: Use the OpenAI Agents SDK (Python) as the agentic framework

## Status
Accepted

## Date
2026-10-19

## Context
This project exists primarily to learn agentic AI concepts hands-on, through a real marketing-agency
use case. The user requested the OpenAI SDK specifically but was open to framework recommendations.
Key requirements for whatever framework is chosen:
- First-class, idiomatic support for tool/function calling
- First-class support for structured (schema-validated) outputs
- First-class support for multi-agent handoffs/orchestration
- Built-in tracing/observability to inspect what the agent actually did
- Low enough abstraction overhead that the underlying agentic concepts stay visible while learning,
  rather than being hidden behind a heavy framework-specific DSL

## Decision
Use the official `openai-agents` Python SDK (`Agent`, `Runner`, `function_tool`, `output_type`,
`handoffs`, `SQLiteSession`) as the framework for all agents in this project.

## Alternatives Considered

### LangChain / LangGraph
- Pros: Mature ecosystem, multi-provider support, large library of integrations
- Cons: Graph-based orchestration and heavier abstractions add indirection; more concepts to learn
  before reaching the agentic primitives themselves
- Rejected: Too much framework surface area for a first hands-on pass at agentic concepts

### CrewAI
- Pros: Opinionated multi-agent "crew" abstraction, quick to get a multi-agent demo running
- Cons: Less direct control over handoff and structured-output primitives compared to what the
  OpenAI SDK exposes natively; opinionated role/crew structure obscures the mechanics being learned
- Rejected: Abstraction hides the exact mechanics (tool calls, handoffs, structured outputs) this
  project is meant to teach

### Raw OpenAI API (hand-rolled function-calling loop)
- Pros: Maximum transparency, zero framework dependency
- Cons: Requires hand-rolling session/history management, JSON-schema output parsing and retries,
  and agent-to-agent control-flow transfer — significant plumbing unrelated to the concepts being
  learned
- Rejected: Too much incidental complexity before any agentic concept can be exercised

## Consequences
- The project is coupled to OpenAI's SDK conventions and model support; switching providers later
  (e.g. to Anthropic or a local model) would require more rework than a multi-provider framework
  like LangChain would need. Acceptable trade-off for a learning project.
- Tool calling, structured outputs, and handoffs are all available as direct SDK primitives
  (`@function_tool`, `output_type`, `handoffs=[...]`), which keeps the code close to the concepts.
- Built-in SDK tracing is available for free to inspect agent behavior (see README "Next steps").
