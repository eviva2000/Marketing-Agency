"""Mock research tools — stand-ins for real market-data / web-search APIs.

All data below is fabricated for learning purposes, not real market research.
"""

from agents import function_tool

# Keyed by lowercase niche name. Real version would call a market-data API.
_NICHE_BENCHMARKS: dict[str, dict] = {
    "roofing": {
        "avg_job_value": "$8k-$25k",
        "demand_pattern": "High urgency, storm-driven spikes, high ticket",
        "competition_notes": "Saturated with lead aggregators (Angi, HomeAdvisor) selling shared leads",
        "pain_points": [
            "Drowning in shared, low-quality leads sold to 4-5 competitors at once",
            "Feast-and-famine demand — slammed in storm season, dead in winter",
            "Burned by agencies that promised results and delivered excuses",
            "Too busy running jobs to manage their own marketing",
        ],
    },
    "hvac": {
        "avg_job_value": "$3k-$12k",
        "demand_pattern": "Emergency-driven, steady year-round demand",
        "competition_notes": "Moderate competition, strong repeat/maintenance revenue",
        "pain_points": [
            "Unpredictable emergency call volume makes staffing hard",
            "Low differentiation between competing HVAC companies",
            "Review-site leads are expensive and low-intent",
        ],
    },
    "foundation": {
        "avg_job_value": "$5k-$20k",
        "demand_pattern": "Steady, less seasonal than roofing",
        "competition_notes": "High ticket, fewer specialized agencies targeting this niche",
        "pain_points": [
            "Homeowners are skeptical and need heavy trust-building before buying",
            "Long sales cycles compared to other home-service trades",
        ],
    },
}

_GENERIC_BENCHMARK = {
    "avg_job_value": "unknown — no benchmark data for this niche yet",
    "demand_pattern": "unknown",
    "competition_notes": "unknown",
    "pain_points": [],
}

# Keyed by broad industry keyword -> candidate niches with one-line rationale.
_INDUSTRY_NICHES: dict[str, list[dict]] = {
    "home services": [
        {"niche": "Roofing", "rationale": "High ticket, high urgency, massive ROI per closed job"},
        {"niche": "HVAC", "rationale": "Emergency-driven, year-round demand"},
        {"niche": "Foundation repair", "rationale": "High ticket, less competition"},
    ],
    "professional services": [
        {"niche": "Law firms (personal injury)", "rationale": "Very high value per client, big ad budgets"},
        {"niche": "Accounting firms", "rationale": "Predictable recurring revenue, easy to qualify leads"},
    ],
}

_GENERIC_NICHES = [
    {"niche": "Local home services", "rationale": "Broadly high-intent, easy to find via Google Ads"},
    {"niche": "Local professional services", "rationale": "High value per client, lower ad competition than e-commerce"},
]


@function_tool
def list_candidate_niches(industry: str) -> list[dict]:
    """Return a short list of candidate niches for a given broad industry, with a one-line rationale each."""
    return _INDUSTRY_NICHES.get(industry.strip().lower(), _GENERIC_NICHES)


@function_tool
def get_niche_benchmarks(niche: str) -> dict:
    """Return avg job value, demand pattern, competition notes, and common pain points for a specific niche."""
    return _NICHE_BENCHMARKS.get(niche.strip().lower(), _GENERIC_BENCHMARK)
