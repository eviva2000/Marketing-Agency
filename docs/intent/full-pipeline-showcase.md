# Intent: Full-pipeline resume showcase

Confirmed via `interview-me`, 2026-10-20.

- **Outcome:** Turn this from a pure learning repo into a resume-ready showcase of agentic-systems
  skills — a repo built like a real product, plus a local UI demoable live in interviews.
- **User:** The project author — demoed to recruiters/technical interviewers evaluating agentic
  engineering ability, primarily via repo read-through, secondarily via a live local demo.
- **Why now:** Adding this to the resume / wants something concrete to show off in interviews.
- **Success:** Offer → Lead Gen → Outbound work fully end-to-end as one continuous
  handoff-chained session (same `Runner`/session model as today, just richer), demoable through a
  local web chat UI; Qualify and Sales exist only as documented/architected roadmap (not built);
  the repo has automated tests, a CI pipeline, and observability/tracing — the things a technical
  reviewer would specifically probe for.
- **Constraint:** Local-only, no deployment/hosting needed; no auth or multi-tenancy; Outbound
  generates realistic content but never actually dispatches anything; real-world grounding comes
  from web search (already decided for Offer via `WebSearchTool`), not paid data vendors.
- **Out of scope:** Hosting/deployment, real email/message sending, user accounts, building out
  Qualify or Sales (architecture only), real CRM/calendar/ads integrations.
