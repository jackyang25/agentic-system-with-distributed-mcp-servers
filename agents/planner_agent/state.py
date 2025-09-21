"""State for the Planner Agent workflow."""

from typing import Any, Dict, Optional

from typing_extensions import TypedDict

class PlannerState(TypedDict):
    # Core workflow control
    current_step: str

    # User input data
    income: Optional[float]
    credit_score: Optional[int]
    zip_code: Optional[str]
    residential_units: Optional[int]
    rag_keywords: Optional[str]

    # Agent results (complete states from each agent)
    budgeting_agent_results: Optional[Dict[str, Any]]
    geoscout_agent_results: Optional[Dict[str, Any]] 
    program_agent_results: Optional[Dict[str, Any]]

    # Property analysis data
    price_data: Optional[Dict[str, Any]]          # Market pricing data (avg, min, max, etc.)
    property_data: Optional[Dict[str, Any]]       # Results from home_id query

    # Extracted values for easy access
    monthly_budget: Optional[float]
    max_loan: Optional[float]

    # Planner-specific outputs
    final_analysis: Optional[str]   # Comprehensive synthesis