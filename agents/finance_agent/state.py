"""State for the Finance Agent workflow."""

from typing import Any, Dict, List, Literal, Optional

from langchain_core.messages import BaseMessage
from typing_extensions import Annotated, TypedDict


class FinanceState(TypedDict):
    # Core workflow control
    messages: Annotated[List[BaseMessage], "add_messages"]
    current_step: str
    step_count: int
    workflow_status: Literal["in_progress", "completed", "error"]

    # User data collection
    user_financial_data: Dict[str, Any]  # income, debt, credit_score, etc.

    # Agent results
    finance_results: Optional[Dict[str, Any]]  # max_price, monthly_payment

    # Basic error handling
    error_count: int
    session_id: str
