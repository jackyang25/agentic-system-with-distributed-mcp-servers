"""Graph for the Planner Agent workflow."""

from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents.planner_agent.nodes import (
    run_nodes,
    synthesis_node,
)
from agents.planner_agent.state import PlannerState


def initialize_graph() -> StateGraph:
    graph: StateGraph[PlannerState, None, PlannerState, PlannerState] = StateGraph(
        state_schema=PlannerState
    )
    graph.add_node(node="run_nodes", action=run_nodes)
    graph.add_node(node="synthesis", action=synthesis_node)

    graph.add_edge(start_key=START, end_key="run_nodes")
    graph.add_edge(start_key="run_nodes", end_key="synthesis")
    graph.add_edge(start_key="synthesis", end_key=END)
    return graph


def compile_graph() -> CompiledStateGraph[
    PlannerState, None, PlannerState, PlannerState
]:
    """Compile the graph into a runnable agent"""
    graph: StateGraph[PlannerState, None, PlannerState, PlannerState] = (
        initialize_graph()
    )
    return graph.compile()


async def run_planner_agent(user_data) -> dict[str, Any] | Any:
    """Entry point to run the planner agent with user data"""
    # Convert user_data to initial state
    initial_state: dict[str, Any] = {
        "current_step": "starting",
        "income": user_data["income"],
        "credit_score": user_data["credit_score"],
        "zip_code": user_data["zip_code"],
        "residential_units": user_data["residential_units"],
        "who_i_am": user_data["who_i_am"],
        "state": user_data["state"],
        "what_looking_for": user_data["what_looking_for"],
        "building_class": user_data["building_class"],
        "current_debt": user_data["current_debt"],
        "budgeting_agent_results": None,
        "geoscout_agent_results": None,
        "program_agent_results": None,
        "final_analysis": None,
        "usage_metadata": {},
    }

    # Create and run the graph
    agent: CompiledStateGraph[PlannerState, None, PlannerState, PlannerState] = (
        compile_graph()
    )
    result: dict[str, Any] | Any = await agent.ainvoke(input=initial_state)

    return result
