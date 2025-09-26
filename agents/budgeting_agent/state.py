"""State for the Budgeting Agent workflow."""

from typing import Any, Dict, Optional

from typing_extensions import TypedDict


class BudgetingState(TypedDict):
    """State definition for the Budgeting Agent workflow."""

    # User input data
    income: Optional[float]
    target_home_id: Optional[int]
    credit_score: Optional[int]
    zip_code: Optional[str]
    residential_units: Optional[int]

    # Tool results
    budget_result: Optional[Dict[str, Any]]
    loan_result: Optional[Dict[str, Any]]
    price_data: Optional[Dict[str, Any]]

    # Extracted values for easy access
    monthly_budget: Optional[float]
    max_loan: Optional[float]

    # Usage metadata
    usage_metadata: Optional[dict[str, Any]]
