"""Graph for the Planner Agent workflow."""

from langgraph.graph import StateGraph
from .state import PlannerState
from .nodes import run_budgeting_agent_node, synthesis_node


def initialize_graph() -> StateGraph:
    """Initialize the planner agent graph with sequential agent calls."""
    graph = StateGraph(PlannerState)
    
    # Add nodes for each agent
    graph.add_node("run_budgeting_agent", run_budgeting_agent_node)
    graph.add_node("synthesis", synthesis_node)
    
    # Set up the workflow: budgeting -> synthesis
    graph.set_entry_point("run_budgeting_agent")
    graph.add_edge("run_budgeting_agent", "synthesis")
    graph.set_finish_point("synthesis")
    
    return graph


def compile_graph():
    """Compile the graph into a runnable agent"""
    graph = initialize_graph()
    return graph.compile()


async def run_planner_agent(user_data):
    """Entry point to run the planner agent with user data"""
    # Convert user_data to initial state
    initial_state = {
        "current_step": "starting",
        "income": user_data["income"],
        "target_home_id": user_data["target_home_id"],
        "credit_score": user_data["credit_score"],
        "zip_code": user_data["zip_code"],
        "budgeting_agent_results": None,
        "geoscout_agent_results": None,
        "program_agent_results": None,
        "final_analysis": None
    }
    
    # Create and run the graph
    agent = compile_graph()
    result = await agent.ainvoke(initial_state)
    
    return result