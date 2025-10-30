from typing import Any, Optional
from typing_extensions import TypedDict


class GeoScoutState(TypedDict):
    step_count: int
    error_count: int

    # user input data
    zip_code: Optional[str]

    # transit node output
    transit_score: int
    transit_summary: str

    # crime node output
    crime_summary: str
    crime_score: int

    # school node output
    school_summary: str
    exam_scores: int
    graduation_percentage: float
    school_score: int

    # synthesizer node output
    total_summary: str

    usage_metadata: Optional[dict[str, Any]]
