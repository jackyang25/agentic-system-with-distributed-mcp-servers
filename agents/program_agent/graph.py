"""Graph for the Program Agent workflow."""
from langgraph.graph import StateGraph
from .state import ProgramMatcherState
from .nodes import fetch_government_programs

def build_program_graph():
    graph = StateGraph(ProgramMatcherState)

    # Add government programs node
    graph.add_node("government_programs", fetch_government_programs)

    # Entry + finish point
    graph.set_entry_point("government_programs")
    graph.set_finish_point("government_programs")

    # MUST compile or ainvoke won’t run
    return graph.compile()