"""State for the Program Agent workflow."""

from typing import Any, Dict, List, Literal, Optional

from langchain_core.messages import BaseMessage
from typing_extensions import Annotated, TypedDict


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
