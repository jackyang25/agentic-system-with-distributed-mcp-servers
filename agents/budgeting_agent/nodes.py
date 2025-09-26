"""Nodes for the Budgeting Agent workflow."""

from logging import Logger
from typing import Any

from agents.budgeting_agent.state import BudgetingState
from mcp_kit.tools import (
    calculate_budget,
    loan_qualification,
    query_price_data_by_zip_and_units,
)
from utils.convenience import get_logger

logger: Logger = get_logger(name=__name__)


async def budget_calculation_node(state: BudgetingState) -> BudgetingState:
    """Calculate 30% budget from user income"""

    # Call the tool directly to get the budget (async)
    budget_result: Any = await calculate_budget.ainvoke(
        input={"income": state["income"]}
    )
    logger.info(f"Budget calculation result: {budget_result}")

    # Extract specific values
    state["monthly_budget"] = budget_result.get("budget", 0)
    state["budget_result"] = budget_result  # Keep full result for compatibility

    return state


async def loan_qualification_node(state: BudgetingState) -> BudgetingState:
    """Calculate maximum loan amount based on income and credit score"""

    # Call the loan qualification tool
    loan_result: Any = await loan_qualification.ainvoke(
        input={"income": state["income"], "credit_score": state["credit_score"]}
    )
    logger.info(f"Loan qualification result: {loan_result}")

    # Extract specific values
    state["max_loan"] = loan_result.get("max_loan", 0)
    state["loan_result"] = loan_result  # Keep full result for compatibility

    return state


async def price_data_query_node(state: BudgetingState) -> BudgetingState:
    """Query comprehensive price data by zip code and residential units"""

    # Call the price data query tool
    price_data_result: Any = await query_price_data_by_zip_and_units.ainvoke(
        input={
            "zip_code": state["zip_code"],
            "residential_units": state["residential_units"],
        }
    )
    logger.info(f"Price data query result: {price_data_result}")

    # Store just the raw tool result
    state["price_data"] = price_data_result

    return state
