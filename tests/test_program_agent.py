"""Run the Program Agent."""

import pytest
from langgraph.graph.state import CompiledStateGraph

from agents.program_agent.graph import compile_graph
from agents.program_agent.state import ProgramAgentState
from utils.convenience import load_secrets

load_secrets()


@pytest.mark.anyio
async def test_run_agent() -> None:
    """Run the program agent with a sample user profile."""
    graph: CompiledStateGraph[
        ProgramAgentState, None, ProgramAgentState, ProgramAgentState
    ] = compile_graph()

    # User input profile
    initial_state = {
        "messages": [],
        "current_step": "start",
        "step_count": 0,
        "workflow_status": "in_progress",
        "user_profile": {
            "credit_score": 640,
            "income": 55000,
            "military": False,
            "first_time_buyer": True,
        },
        "program_matcher_results": [],
        "error_count": 0,
        "session_id": "demo-session",
    }

    final_state = await graph.ainvoke(input=initial_state)

    print("\n🏡 Available Funding Programs:\n")
    for prog in final_state.get("program_matcher_results", []):
        print(
            f"- {prog['program_name']}: {prog['benefits']} (Source: {prog['source']})"
        )
