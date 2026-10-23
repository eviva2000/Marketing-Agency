"""Structured output models produced once a niche has been confirmed."""

from pydantic import BaseModel


class OfferSummary(BaseModel):
    who: str
    what: str
    promise: str
    model: str
    delivery: str
    guarantee: str


class FinalPitch(BaseModel):
    who_we_help: str
    pain_points: list[str]
    promise: str
    proof_math: str


class OfferPackage(BaseModel):
    niche: str
    offer_summary: OfferSummary
    final_pitch: FinalPitch


class Lead(BaseModel):
    name: str
    how_found: str
    contact_info: str
    fit_reasoning: str
    outreach_angle: str


class LeadList(BaseModel):
    niche: str
    leads: list[Lead]
    offer_package: OfferPackage | None = None


class OutboundDraft(BaseModel):
    lead_name: str
    email_subject: str
    email_body: str
    call_opener: str
    personalization_rationale: str


class OutboundPackage(BaseModel):
    niche: str
    drafts: list[OutboundDraft]
