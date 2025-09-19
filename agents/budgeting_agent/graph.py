"""Graph for the Budgeting Agent workflow."""

from langgraph.graph import StateGraph
from .state import BudgetingState
from .nodes import budget_calculation_node, loan_qualification_node


def initialize_graph() -> StateGraph:
    """Initialize the budgeting agent graph with model and tools."""
    graph = StateGraph(BudgetingState)
    
    # Add nodes
    graph.add_node("budget_calculation", budget_calculation_node)
    graph.add_node("loan_qualification", loan_qualification_node)
    
    # Set up the workflow: budget calculation -> loan qualification
    graph.set_entry_point("budget_calculation")
    graph.add_edge("budget_calculation", "loan_qualification")
    graph.set_finish_point("loan_qualification")
        
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
        "loan_result": None
    }
    
    # Create and run the graph
    agent = compile_graph()
    result = await agent.ainvoke(initial_state)
    
    return result
