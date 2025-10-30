from typing import Any
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from agents.geoscout_agent.nodes import (
    node_commute_score,
    node_crime_rate,
    node_school_rate,
    node_synthesizer,
)
from agents.geoscout_agent.state import GeoScoutState


def initialize_graph() -> GeoScoutState:
    graph: StateGraph[GeoScoutState] = StateGraph(state_schema=GeoScoutState)

    graph.add_node(node="node_commute_score", action=node_commute_score)
    graph.add_node(node="node_crime_rate", action=node_crime_rate)
    graph.add_node(node="node_school_rate", action=node_school_rate)
    graph.add_node(node="node_synthesizer", action=node_synthesizer)

    graph.add_edge(start_key=START, end_key="node_commute_score")
    graph.add_edge(start_key="node_commute_score", end_key="node_crime_rate")
    graph.add_edge(start_key="node_crime_rate", end_key="node_school_rate")
    graph.add_edge(start_key="node_school_rate", end_key="node_synthesizer")
    graph.add_edge(start_key="node_synthesizer", end_key=END)

    return graph


def compile_graph() -> CompiledStateGraph[
    GeoScoutState, None, GeoScoutState, GeoScoutState
]:
    graph: GeoScoutState = initialize_graph()
    return graph.compile()


async def run_geoscout_agent(user_data: dict[Any, Any]) -> dict[str, Any] | Any:
    initial_state: dict[str, Any] = {
        "current_step": "start",
        "step_count": 0,
        "error_count": 0,
        "zip_code": user_data.get("zip_code", None),
        "transit_score": 0,
        "transit_summary": "",
        "crime_summary": "",
        "crime_score": 0,
        "school_summary": "",
        "school_score": 0,
        "total_summary": "",
        "usage_metadata": {},
    }

    agent: CompiledStateGraph[GeoScoutState, None, GeoScoutState, GeoScoutState] = (
        compile_graph()
    )
    result: dict[str, Any] | Any = await agent.ainvoke(input=initial_state)

    return result
