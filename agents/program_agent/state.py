# Used a TypedDict so the graph knows the keys available.
from typing import Any, Dict, List, Literal, Optional
from langchain_core.messages import BaseMessage
from typing_extensions import Annotated, TypedDict

class ProgramMatcherState(TypedDict):
    messages: Annotated[List[BaseMessage], "add_messages"]
    current_step: str
    step_count: int
    workflow_status: Literal["in_progress", "completed", "error"]
    user_profile: Dict[str, Any]
    program_matcher_results: List[Dict[str, Any]]  # <-- make sure it's a list
    error_count: int
    session_id: str
