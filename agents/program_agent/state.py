from typing import Any, Optional
from typing_extensions import TypedDict


class ProgramAgentState(TypedDict):
    who_i_am: Optional[list[str]]
    state: Optional[str]
    what_looking_for: Optional[list[str]]
    income: Optional[float]
    credit_score: Optional[int]
    zip_code: Optional[str]
    building_class: Optional[str]
    current_debt: Optional[float]
    residential_units: Optional[int]

    program_matcher_results: Optional[ # unfiltered results
        list[dict[str, Any]]
    ]
    programs_text: Optional[str]
    filtered_programs: Optional[str]

    usage_metadata: Optional[dict[str, Any]]
