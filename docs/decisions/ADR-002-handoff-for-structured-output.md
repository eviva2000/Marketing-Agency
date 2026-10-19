# ADR-002: Use a handoff to an Offer Summarizer agent for structured output

## Status
Accepted

## Date
2026-10-19

## Context
The initial plan treated two learning goals as separate build steps: a multi-agent **handoff**
(originally scoped as a "Niche Researcher" agent) and a **structured output** schema
(`OfferSummary`/`PitchOutput`) produced by the main conversational agent. Building them
independently would mean two mostly-unrelated features bolted onto the same bot.

Also, setting `output_type` directly on the conversational "Offer Creation Bot" agent would force
every turn of the interview (including clarifying questions and niche comparisons) into the
structured schema shape, breaking the natural back-and-forth conversation shown in the reference
product design.

## Decision
Model the flow as two agents connected by a single handoff:
- **Offer Creation Bot** — conversational, uses mock research tools, no `output_type`. Interviews
  the user and recommends a niche.
- **Offer Summarizer** — the handoff target, triggered once the user confirms a niche. Has
  `output_type=OfferPackage` and reads the conversation history to produce the final structured
  deliverable (nesting `OfferSummary` + `FinalPitch` in one `OfferPackage` model).

The handoff point doubles as the transition from freeform conversation to structured output,
exercising both concepts through one coherent, realistic interaction instead of two disconnected
features.

## Alternatives Considered

### Separate Niche Researcher agent (as originally planned) + structured output bolted onto the main agent
- Pros: Matches the original phase-by-phase plan exactly
- Cons: Niche Researcher would duplicate benchmark-lookup tool usage already done by the main
  agent; the trigger condition for when to hand off ("ask for deeper research") is less natural
  than "user confirmed a niche, now finalize the deliverable"
- Rejected: Two loosely-related features demonstrated independently, rather than one coherent flow

### Single agent with `output_type` set from the start
- Pros: Simplest possible code, one agent total
- Cons: Forces every response — including clarifying questions — into the structured schema,
  which breaks the conversational interview phase entirely
- Rejected: Incompatible with the "ask questions, then recommend, then confirm" flow being modeled

## Consequences
- `OfferSummary` and `FinalPitch` are nested inside one `OfferPackage` model rather than being two
  independent top-level schemas as first drafted.
- A dedicated "Niche Researcher" agent (for deep, on-demand research into a single niche) is
  deferred — it can be reintroduced later as a third agent if deep research becomes a distinct step
  from summarization.
- The Offer Summarizer currently has no tools of its own; it relies entirely on conversation history
  passed through the handoff. If it later needs to re-verify data, tools would need to be added to it.
