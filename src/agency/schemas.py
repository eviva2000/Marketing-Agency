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
