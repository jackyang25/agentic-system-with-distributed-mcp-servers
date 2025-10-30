"""State for the Program Agent workflow."""

from typing import Any, Optional

from typing_extensions import TypedDict


class ProgramAgentState(TypedDict):
    """State definition for the Program Agent workflow."""

    # User input data (for RAG)
    who_i_am: Optional[list[str]]
    state: Optional[str]
    what_looking_for: Optional[list[str]]
    income: Optional[float]
    credit_score: Optional[int]
    zip_code: Optional[str]
    building_class: Optional[str]
    current_debt: Optional[float]
    residential_units: Optional[int]

    # RAG results
    program_matcher_results: Optional[
        list[dict[str, Any]]
    ]  # Original RAG results (list)
    programs_text: Optional[str]
    filtered_programs: Optional[str]

    usage_metadata: Optional[dict[str, Any]]
