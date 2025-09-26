"""Graph for the Budgeting Agent workflow."""

from typing import Any

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents.budgeting_agent.nodes import (
    budget_calculation_node,
    loan_qualification_node,
    price_data_query_node,
)
from agents.budgeting_agent.state import BudgetingState


def initialize_graph() -> StateGraph[
    BudgetingState, None, BudgetingState, BudgetingState
]:
    """Initialize the budgeting agent graph with model and tools."""
    graph: StateGraph[BudgetingState, None, BudgetingState, BudgetingState] = (
        StateGraph(state_schema=BudgetingState)
    )

    # Add nodes
    graph.add_node(node="budget_calculation", action=budget_calculation_node)
    graph.add_node(node="loan_qualification", action=loan_qualification_node)
    graph.add_node(node="price_data_query", action=price_data_query_node)

    # Set up the workflow: budget calculation -> loan qualification -> average price query
    graph.set_entry_point(key="budget_calculation")
    graph.add_edge(start_key="budget_calculation", end_key="loan_qualification")
    graph.add_edge(start_key="loan_qualification", end_key="price_data_query")
    graph.set_finish_point(key="price_data_query")

    return graph


def compile_graph() -> CompiledStateGraph[
    BudgetingState, None, BudgetingState, BudgetingState
]:
    """Compile the graph into a runnable agent"""
    graph: StateGraph[BudgetingState, None, BudgetingState, BudgetingState] = (
        initialize_graph()
    )
    return graph.compile()


async def run_budgeting_agent(user_data: dict[str, Any]) -> dict[str, Any] | Any:
    """Entry point to run the budgeting agent with user data"""
    # Convert user_data to initial state
    initial_state: dict[str, Any] = {
        "income": user_data["income"],
        "target_home_id": user_data.get("target_home_id", None),
        "credit_score": user_data["credit_score"],
        "zip_code": user_data["zip_code"],
        "residential_units": user_data["residential_units"],
        "budget_result": None,
        "loan_result": None,
        "price_data": None,
        "monthly_budget": None,
        "max_loan": None,
        "usage_metadata": {},
    }

    # Create and run the graph
    agent: CompiledStateGraph[BudgetingState, None, BudgetingState, BudgetingState] = (
        compile_graph()
    )
    result: dict[str, Any] | Any = await agent.ainvoke(input=initial_state)

    return result
