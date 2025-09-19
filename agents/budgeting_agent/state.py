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
    
    # Tool results
    budget_result: Optional[Dict[str, Any]]
    property_result: Optional[Dict[str, Any]]
    
    # Analysis and output
    analysis: Optional[Dict[str, Any]]
    final_output: Optional[Dict[str, Any]]

