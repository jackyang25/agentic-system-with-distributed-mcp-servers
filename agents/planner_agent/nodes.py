"""Nodes for the Planner Agent workflow."""

from .state import PlannerState
from .prompts import get_comprehensive_analysis_prompt
from agents.budgeting_agent.graph import run_budgeting_agent


async def run_budgeting_agent_node(state: PlannerState):
    """Call the budgeting agent and store results in state"""
    current_step = state.get('current_step', 'unknown')
    print(f"STEP: {current_step} -> Calling budgeting agent...")
    
    # Extract user data from state
    user_data = {
        "income": state["income"],
        "target_home_id": state["target_home_id"],
        "credit_score": state["credit_score"],
        "zip_code": state["zip_code"]
    }
    
    # Call the budgeting agent
    budgeting_results = await run_budgeting_agent(user_data)
    
    # Store results in state
    state["budgeting_agent_results"] = budgeting_results
    state["current_step"] = "budgeting_complete"
    
    return state


async def synthesis_node(state: PlannerState):
    """Synthesize all agent results into final analysis"""
    current_step = state.get('current_step', 'unknown')
    print(f"STEP: {current_step} -> Generating final analysis...")
    
    from langchain_openai import ChatOpenAI
    
    # For now, just return the budgeting results as analysis
    # You can expand this later to include other agents
    budgeting_results = state.get("budgeting_agent_results", {})
    
    if budgeting_results:
        print("   Calling LLM for analysis...")
        # Use LLM to provide comprehensive analysis
        model = ChatOpenAI(
            model="gpt-4o-mini",
            timeout=30,  # 30 second timeout
            max_retries=2
        )
        
        # Get the comprehensive analysis prompt from prompts.py
        analysis_prompt = get_comprehensive_analysis_prompt(budgeting_results)
        
        try:
            response = await model.ainvoke(analysis_prompt)
            analysis = response.content
            print("   LLM analysis completed")
        except Exception as e:
            print(f"   LLM analysis failed: {e}")
            analysis = f"Analysis unavailable due to error: {str(e)}"
    else:
        analysis = "No budgeting results available for analysis."
    
    state["final_analysis"] = analysis
    state["current_step"] = "synthesis_complete"
    
    return state