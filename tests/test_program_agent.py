"""Run the Program Agent."""
import asyncio
from agents.program_agent.graph import build_program_graph


async def run_agent():
    """Run the program agent with a sample user profile."""
    graph = build_program_graph()

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
        "session_id": "demo-session"
    }
    
    final_state = await graph.ainvoke(initial_state)

    print("\n🏡 Available Funding Programs:\n")
    for prog in final_state.get("program_matcher_results", []):
        print(f"- {prog['program_name']}: {prog['benefits']} (Source: {prog['source']})")


async def visualize_graph():
    """Export the Program Agent workflow graph as PNG."""
    graph = build_program_graph()
    compiled = graph.compile()
    compiled.get_graph().draw_mermaid_png("program_agent_graph.png")
    print("📊 Program Agent workflow graph saved as program_agent_graph.png")


if __name__ == "__main__":
    # 👉 Choose which one you want to run:
    asyncio.run(run_agent())       # run the agent with profile
    # asyncio.run(visualize_graph()) # uncomment to export graph



    




