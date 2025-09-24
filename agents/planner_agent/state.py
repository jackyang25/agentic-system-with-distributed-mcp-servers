"""State for the Planner Agent workflow."""

from typing import Any, Optional

from typing_extensions import TypedDict


class PlannerState(TypedDict):
    # Core workflow control
    current_step: str

    # User input data (from frontend)
    income: Optional[float]
    credit_score: Optional[int]
    zip_code: Optional[str]
    residential_units: Optional[int]
    current_debt: Optional[float]

    # RAG STATE
    who_i_am: Optional[list]  # User identity/status selections
    state: Optional[str]  # State selection
    what_looking_for: Optional[list]  # What they're looking for selections
    building_class: Optional[str]

    # Agent results (complete states from each agent)
    budgeting_agent_results: Optional[dict[str, Any]]
    geoscout_agent_results: Optional[dict[str, Any]]
    program_agent_results: Optional[dict[str, Any]]

    # Property analysis data
    price_data: Optional[dict[str, Any]]  # Market pricing data (avg, min, max, etc.)
    property_data: Optional[dict[str, Any]]  # Results from home_id query

    # Extracted values for easy access
    monthly_budget: Optional[float]
    max_loan: Optional[float]

    # Planner-specific outputs
    final_analysis: Optional[str]  # Comprehensive synthesis
