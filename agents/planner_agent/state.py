"""State for the Finance Agent workflow."""

from typing import Any, Dict, List, Literal, Optional

from langchain_core.messages import BaseMessage
from typing_extensions import Annotated, TypedDict

class PlannerState(TypedDict):
    # Core workflow control
    messages: Annotated[List[BaseMessage], "add_messages"]
    current_step: str
    step_count: int
    workflow_status: Literal["in_progress", "completed", "error"]

    # Orchestration data
    collected_data: Dict[str, Any]  # All user data across agents
    missing_data_fields: List[str]  # What's still needed
    next_agent: Optional[str]       # Which agent to route to next
    agents_completed: List[str]     # ["finance", "geo_scout"]

    # Cross-agent results (for routing decisions)
    finance_results: Optional[Dict[str, Any]]
    geo_scout_results: Optional[Dict[str, Any]] 
    program_matcher_results: Optional[Dict[str, Any]]

    # Planner-specific outputs
    workflow_progress: float        # 0.0 to 1.0
    recommended_questions: List[str] # Questions for missing data

    # Basic error handling
    error_count: int
    session_id: str