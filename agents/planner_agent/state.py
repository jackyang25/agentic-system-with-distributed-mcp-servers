"""State for the Planner Agent workflow."""

from typing import Any, Optional

from typing_extensions import TypedDict


class PlannerState(TypedDict):
    # User input data (from frontend)
    income: Optional[float]
    state: Optional[str]  # State selection
    credit_score: Optional[int]
    zip_code: Optional[str]
    residential_units: Optional[int]
    current_debt: Optional[float]
    building_class: Optional[str]
    who_i_am: Optional[list]  # User identity/status selections
    what_looking_for: Optional[list]  # What they're looking for selections s

    # Program state
    program_agent_results: Optional[dict[str, Any]]

    # Geoscout agent
    geoscout_agent_results: Optional[dict[str, Any]]

    # Budgeting agent
    price_data: Optional[dict[str, Any]]  # Market pricing data (avg, min, max, etc.)
    property_data: Optional[dict[str, Any]]  # Results from home_id query
    monthly_budget: Optional[float]
    max_loan: Optional[float]
    budgeting_agent_results: Optional[dict[str, Any]]

    # Planner-specific outputs
    final_analysis: Optional[str]  # Comprehensive synthesis

    # Usage metadata
    usage_metadata: Optional[dict[str, Any]]
