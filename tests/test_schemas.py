"""Tests for the structured-output schemas in agency.schemas."""

import pytest
from pydantic import ValidationError

from agency.schemas import FinalPitch, Lead, LeadList, OfferPackage, OfferSummary


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


def _lead() -> Lead:
    return Lead(
        name="Acme Roofing Co.",
        how_found="Found via Google search for 'roofing companies in Austin, TX'",
        contact_info="https://acmeroofing.example/contact",
        fit_reasoning="Does $1M+/year in revenue and relies on shared leads today",
        outreach_angle="Offer a free trial batch of exclusive leads",
    )


def test_lead_list_builds_with_all_required_fields():
    lead_list = LeadList(niche="Roofing", leads=[_lead(), _lead()])

    assert lead_list.niche == "Roofing"
    assert len(lead_list.leads) == 2
    assert lead_list.leads[0].name == "Acme Roofing Co."


def test_lead_list_requires_niche_and_leads():
    with pytest.raises(ValidationError):
        LeadList(niche="Roofing")
