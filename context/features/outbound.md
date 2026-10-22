# Feature: outbound

## Status
Implemented; manual smoke check pending

## Objective

Add an Outbound stage that takes the confirmed `OfferPackage` and `LeadList` from the earlier
stages and prepares tailored outreach for those prospects. It should create realistic, reviewable
drafts (for example, an email and a call opener per lead) using the lead's known fit and contact
details plus the offer's promise. The user reviews and refines the drafts; nothing is sent.

Success: running the CLI through Offer → Lead Gen → Outbound lets the user review and adjust
outreach drafts, then produces a structured `OutboundPackage` grounded only in the confirmed offer,
lead list, and conversation. No message is dispatched.

## Assumptions to validate

- Outbound is a single capability: create and refine outreach drafts for the confirmed leads.
- Initial deliverable is one personalized email draft and one short call opener per lead. A
  multi-touch campaign can be added later if it proves useful.
- Drafts must not invent personal facts, contact details, testimonials, or results. They may use
  public business details already in the `LeadList` and the confirmed offer.
- The current local CLI and Agents SDK handoff flow remain the interface; no UI or delivery
  integration is part of this module.

## Background / design questions

The Lead Gen flow currently ends with `lead_list_summarizer_agent`, which returns a structured
`LeadList` and has no handoffs. The end-to-end intent calls for one continuous Offer → Lead Gen →
Outbound session. Before implementation, decide how the user moves from a completed lead list into
Outbound and how both structured results remain available in conversation context. Prefer an SDK
handoff if the existing `output_type` + `handoffs` pattern works on a later turn, as it does for
Offer → Lead Gen; confirm with a `FakeModel` spike before relying on that behavior.

Other decisions to settle while refining the spec:

- Keep the first release to email + call opener, or support a user-selected channel?
- Should the user confirm each draft, or review/refine the full batch before structured output?
- What should the output schema contain beyond lead identity, channel, subject, body/script, and
  personalization rationale?

## Scope

- Add an Outbound conversational agent that uses the confirmed `OfferPackage` and `LeadList` to
  draft individualized outreach for the confirmed leads.
- Let the user review the drafts and request edits before confirming the batch.
- Add a structured-output summarizer and schema for the confirmed drafts (proposed name:
  `OutboundPackage`), preserving which lead each draft belongs to.
- Chain Lead Gen → Outbound in the existing CLI session and display the structured result clearly.
- Add `FakeModel` behavior tests with no real API calls, following existing agent test patterns.
- Update README, project overview, current-feature history, and this spec when the module passes
  its checkpoint.

Out of scope: sending email or making calls, connecting to an email provider or CRM, automated
follow-up scheduling, tracking opens/replies, and building the web UI (a later roadmap module).

## Task list

### Phase 1: Resolve interface and handoff

- [x] Task 1: Use email + call opener per lead, batch review, and an `OutboundPackage` containing
      each lead name and both drafts.
- [x] Task 2: Confirm the structured-output plus handoff transition from the Lead List Summarizer
      to Outbound with `FakeModel`; the existing SDK pattern works on a later turn.

### Phase 2: Agents and schema

- [x] Task 3: Add the outbound draft models to `src/agency/schemas.py` with schema tests.
- [x] Task 4: Add the Outbound conversational agent with instructions to personalize drafts while
      avoiding unsupported claims or fabricated facts.
- [x] Task 5: Add the Outbound Summarizer agent that returns only drafts confirmed by the user.
- [x] Task 6: Wire Lead Gen → Outbound through the resolved handoff pattern.

### Phase 3: CLI and behavior tests

- [x] Task 7: Add `FakeModel` tests for handoff and structured output; ensure default tests make
      no real API calls. Drafting and revisions require the manual check in Task 11.
- [x] Task 8: Update CLI rendering for the new structured output.
- [x] Task 9: Run `python3 -m pytest` and `ruff check .`.

### Phase 4: Docs and manual check

- [x] Task 10: Update README and `context/project-overview.md` to describe the implemented Outbound
      stage and revise roadmap status.
- [ ] Task 11: With a real `OPENAI_API_KEY`, manually run Offer → Lead Gen → Outbound and verify
      the drafts match the confirmed offer and leads. Confirm that no sending mechanism exists.
      A focused live Outbound run with one supplied offer and lead passed: the agent drafted an
      email and call opener, then returned one structured draft after approval. The full pipeline
      run remains to be checked.
- [ ] Task 12: Move this entry to completed history in `context/current-feature.md` after the
      checkpoint passes.

## Checkpoint

- [x] `ruff check .` passes with zero errors.
- [x] `python3 -m pytest` passes with zero real API/network calls.
- [x] The CLI supports the continuous Offer → Lead Gen → Outbound workflow through SDK handoffs.
- [x] The structured output associates each draft with a confirmed lead name.
- [x] The focused live draft used only the supplied offer and lead details.
- [x] The focused live run returned structured output only after approval.
- [x] No email, call, or other outreach is dispatched.
- [x] README and project overview describe the implemented stage.

## Decisions for this release

- Create one email and call opener per confirmed lead by default; allow a user-selected subset.
- Review and refine the batch before approval and structured output.
- Use the confirmed `LeadList` for personalization without additional web research.
