"""State for the GeoScout agent workflow."""

from typing import Any, Dict, List, Literal, Optional

from langchain_core.messages import BaseMessage
from typing_extensions import Annotated, TypedDict


class GeoScoutState(TypedDict):
    # Core workflow control
    messages: Annotated[List[BaseMessage], "add_messages"]
    current_step: str
    step_count: int
    workflow_status: Literal["in_progress", "completed", "error"]

    # User data collection
    location_preferences: Dict[str, Any]  # cities, priorities, home type

    # Agent results
    geo_scout_results: Optional[Dict[str, Any]]  # neighborhoods list

    # Basic error handling
    error_count: int
    session_id: str
