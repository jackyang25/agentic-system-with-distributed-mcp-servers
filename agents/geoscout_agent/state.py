"""State for the agent_name workflow."""
from typing import Dict, List, Any, Optional, Literal
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import BaseMessage

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
