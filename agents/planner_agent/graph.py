"""Graph for the Planner Agent workflow."""
from langgraph.graph import StateGraph
from states.planner_state import PlannerState
from .nodes import assess_workflow

def build_planner_graph():
    graph = StateGraph(PlannerState)
    
    # Single assessment node
    graph.add_node("assess_workflow", assess_workflow)
    
    # Entry + finish point
    graph.set_entry_point("assess_workflow")
    graph.set_finish_point("assess_workflow")
    
    return graph.compile()