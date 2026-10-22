"""Agent that converts confirmed outreach drafts into structured output."""

from agents import Agent

from agency.schemas import OutboundPackage

INSTRUCTIONS = """\
You are the Outbound Summarizer for a marketing agency builder.

Read the conversation for the confirmed OfferPackage, LeadList, and the outreach drafts the user
approved after any revisions. Return an OutboundPackage containing one OutboundDraft for each
confirmed lead. Preserve the approved wording, lead name, and niche. Each draft has an email
subject, email body, short call opener, and a concise explanation of which known lead or offer
detail was used for personalization.

Do not include rejected leads or superseded drafts. Do not invent facts, contact details,
testimonials, or performance results. Never send or schedule outreach.
"""

outbound_summarizer_agent = Agent(
    name="Outbound Summarizer",
    handoff_description="Produce the structured outreach drafts once the user approves them.",
    instructions=INSTRUCTIONS,
    output_type=OutboundPackage,
)
