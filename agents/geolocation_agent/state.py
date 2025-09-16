"""State for the Geolocation agent workflow."""

from typing import Any, TypedDict


class GeolocationState(TypedDict):
    """State for the Geolocation agent workflow."""

    region: str  # e.g., "Austin, TX"
    budget_max: int  # from Finance Agent
    zips: list[str]  # ZIP codes in the region
    medians: dict[str, int]  # ZIP -> median_home_value
    features: dict[
        str, dict[Any, Any]
    ]  # ZIP -> {school_rating, transit_score, safety_index, walkability}
    results: list[dict[Any, Any]]  # final output rows
    cache: dict[str, int]  # persisted median cache
    errors: list[str]  # error messages
