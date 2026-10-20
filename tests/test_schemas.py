"""Tests for the structured-output schemas in agency.schemas."""

import pytest
from pydantic import ValidationError

from agency.schemas import FinalPitch, OfferPackage, OfferSummary


def _offer_summary() -> OfferSummary:
    return OfferSummary(
        who="Roofing companies doing $1M+/year",
        what="Done-for-you lead generation via Google Ads",
        promise="10 qualified leads/month or you don't pay",
        model="Pay-per-qualified-lead",
        delivery="Landing page, ad campaigns, lead routing",
        guarantee="First 10 leads free if we miss the target",
    )


def _final_pitch() -> FinalPitch:
    return FinalPitch(
        who_we_help="Roofing companies tired of shared leads",
        pain_points=["Shared leads", "Seasonal demand", "No in-house marketing"],
        promise="10 exclusive leads/month, guaranteed",
        proof_math="One $15k roofing job pays for a year of this service",
    )


def test_offer_package_builds_with_all_required_fields():
    package = OfferPackage(
        niche="Roofing",
        offer_summary=_offer_summary(),
        final_pitch=_final_pitch(),
    )

    assert package.niche == "Roofing"
    assert package.offer_summary.model == "Pay-per-qualified-lead"
    assert len(package.final_pitch.pain_points) == 3


def test_offer_package_requires_offer_summary_and_final_pitch():
    with pytest.raises(ValidationError):
        OfferPackage(niche="Roofing")
