from typing import Any, Optional
from typing_extensions import TypedDict


class PlannerState(TypedDict):
    income: Optional[float]
    state: Optional[str]
    credit_score: Optional[int]
    zip_code: Optional[str]
    residential_units: Optional[int]
    current_debt: Optional[float]
    building_class: Optional[str]
    who_i_am: Optional[list]
    what_looking_for: Optional[list]

    program_agent_results: Optional[dict[str, Any]]

    geoscout_agent_results: Optional[dict[str, Any]]

    price_data: Optional[dict[str, Any]]
    property_data: Optional[dict[str, Any]]
    monthly_budget: Optional[float]
    max_loan: Optional[float]
    budgeting_agent_results: Optional[dict[str, Any]]

    final_analysis: Optional[str]

    usage_metadata: Optional[dict[str, Any]]
