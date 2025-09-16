"""State for the agent_name workflow."""
from typing import Dict, List, Any, Optional, Literal
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import BaseMessage

class ProgramMatcherState(TypedDict):
    # Core workflow control
    messages: Annotated[List[BaseMessage], "add_messages"]
    current_step: str
    step_count: int
    workflow_status: Literal["in_progress", "completed", "error"]
    
    # User data collection
    user_profile: Dict[str, Any]  # first_time_buyer, military, etc.
    
    # Agent results
    program_matcher_results: Optional[Dict[str, Any]]  # eligible programs
    
    # Basic error handling
    error_count: int
    session_id: str