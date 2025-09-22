"""Graph for the Program Agent workflow."""

from langgraph.graph import StateGraph
from .state import ProgramAgentState
from .nodes import rag_search_programs_node, filter_programs_node


def initialize_graph() -> StateGraph:
    """Initialize the program agent graph with model and tools."""
    graph = StateGraph(ProgramAgentState)
    
    # Add nodes
    graph.add_node("rag_search_programs", rag_search_programs_node)
    graph.add_node("filter_programs", filter_programs_node)
    
    # Set up the workflow: RAG search -> filter programs
    graph.set_entry_point("rag_search_programs")
    graph.add_edge("rag_search_programs", "filter_programs")
    graph.set_finish_point("filter_programs")
        
    return graph


def compile_graph():
    """Compile the graph into a runnable agent"""
    graph = initialize_graph()
    return graph.compile()


async def run_program_agent(user_data):
    """Entry point to run the program agent with user data"""
    # Convert user_data to initial state
    initial_state = {
        "who_i_am": user_data["who_i_am"],
        "state": user_data["state"],
        "what_looking_for": user_data["what_looking_for"],
        "income": user_data["income"],
        "credit_score": user_data["credit_score"],
        "zip_code": user_data["zip_code"],
        "building_class": user_data["building_class"],
        "current_debt": user_data["current_debt"],
        "residential_units": user_data["residential_units"],
        "program_matcher_results": [],
        "current_step": "search_programs"
    }
    
    # Create and run the graph
    agent = compile_graph()
    result = await agent.ainvoke(initial_state)
    
    return result
