from typing import Any
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from agents.program_agent.nodes import filter_programs_node, rag_search_programs_node
from agents.program_agent.state import ProgramAgentState


def initialize_graph() -> StateGraph:
    graph: StateGraph[ProgramAgentState, None, ProgramAgentState, ProgramAgentState] = (
        StateGraph(state_schema=ProgramAgentState)
    )

    graph.add_node(node="rag_search_programs", action=rag_search_programs_node)
    graph.add_node(node="filter_programs", action=filter_programs_node)

    graph.set_entry_point(key="rag_search_programs")
    graph.add_edge(start_key="rag_search_programs", end_key="filter_programs")
    graph.set_finish_point(key="filter_programs")

    return graph


def compile_graph() -> CompiledStateGraph[
    ProgramAgentState, None, ProgramAgentState, ProgramAgentState
]:
    graph: StateGraph[ProgramAgentState, None, ProgramAgentState, ProgramAgentState] = (
        initialize_graph()
    )
    return graph.compile()


async def run_program_agent(user_data) -> Any:
    initial_state: dict[str, Any] = {
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
        "current_step": "search_programs",
        "usage_metadata": {},
    }

    agent: CompiledStateGraph[
        ProgramAgentState, None, ProgramAgentState, ProgramAgentState
    ] = compile_graph()
    result: Any = await agent.ainvoke(input=initial_state)

    return result
