"""Graph for the Budgeting Agent workflow."""

from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from mcp_kit.tools import calculate_budget, query_home_by_id
from .state import BudgetingState
from .nodes import budget_calculation_node


def initialize_graph() -> StateGraph:
    """Initialize the budgeting agent graph with model and tools."""
    graph = StateGraph(BudgetingState)
    
    # Add budget calculation node
    graph.add_node("budget_calculation", budget_calculation_node)
    
    
    # Set entry point and end point (since we only have one node for testing)
    graph.set_entry_point("budget_calculation")
    graph.set_finish_point("budget_calculation")
    
    # TODO: Add more nodes and edges here
    
    return graph


def compile_graph():
    """Compile the graph into a runnable agent"""
    graph = initialize_graph()
    return graph.compile()


async def run_budgeting_agent(user_data):
    """Entry point to run the budgeting agent with user data"""
    # Convert user_data to initial state
    initial_state = {
        "income": user_data["income"],
        "target_home_id": user_data["target_home_id"],
        "credit_score": user_data["credit_score"],
        "zip_code": user_data["zip_code"],
        "budget_result": None,
        "property_result": None,
        "analysis": None,
        "final_output": None
    }
    
    # Create and run the graph
    agent = compile_graph()
    result = await agent.ainvoke(initial_state)
    
    return result
