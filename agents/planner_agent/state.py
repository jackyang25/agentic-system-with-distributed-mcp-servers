"""State for the Planner Agent workflow."""

from typing import Any, Dict, Optional

from typing_extensions import TypedDict

class PlannerState(TypedDict):
    # Core workflow control
    current_step: str

    # User input data
    income: Optional[float]
    target_home_id: Optional[int]
    credit_score: Optional[int]
    zip_code: Optional[str]

    # Agent results (complete states from each agent)
    budgeting_agent_results: Optional[Dict[str, Any]]
    geoscout_agent_results: Optional[Dict[str, Any]] 
    program_agent_results: Optional[Dict[str, Any]]

    # Planner-specific outputs
    final_analysis: Optional[str]   # Comprehensive synthesis