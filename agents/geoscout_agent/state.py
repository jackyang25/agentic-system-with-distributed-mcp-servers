"""State for the GeoScout agent workflow."""

from typing import Any, Optional

from typing_extensions import TypedDict


class GeoScoutState(TypedDict):
    """State definition for the GeoScout Agent workflow."""

    step_count: int
    error_count: int

    # User input data
    zip_code: Optional[str]

    # Transit node output
    transit_score: int
    transit_summary: str

    # Crime node output
    crime_summary: str
    crime_score: int

    # School node output
    school_summary: str
    exam_scores: int
    graduation_percentage: float
    school_score: int

    # Synthesizer node output
    total_summary: str

    # Usage metadata
    usage_metadata: Optional[dict[str, Any]]
