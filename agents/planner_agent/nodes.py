"""Nodes for the Planner Agent workflow."""

from .state import PlannerState
from .prompts import get_comprehensive_analysis_prompt
from agents.budgeting_agent.graph import run_budgeting_agent
from agents.program_agent.graph import run_program_agent


async def run_budgeting_agent_node(state: PlannerState):
    """Call the budgeting agent and store results in state"""
    current_step = state.get('current_step', 'unknown')
    print(f"STEP: {current_step} -> Calling budgeting agent...")
    
    # Extract user data from state
    user_data = {
        "income": state["income"],
        "credit_score": state["credit_score"],
        "zip_code": state["zip_code"],
        "residential_units": state["residential_units"]
    }
    
    # Call the budgeting agent
    budgeting_results = await run_budgeting_agent(user_data)
    
    # Store results in state
    state["budgeting_agent_results"] = budgeting_results
    
    # Extract primitive values for easy access
    state["monthly_budget"] = budgeting_results.get("monthly_budget")
    state["max_loan"] = budgeting_results.get("max_loan")
    state["price_data"] = budgeting_results.get("price_data")
    
    state["current_step"] = "budgeting_complete"
    
    return state


async def run_program_agent_node(state: PlannerState):
    """Call the program agent and store results in state"""
    current_step = state.get('current_step', 'unknown')
    print(f"STEP: {current_step} -> Calling program agent...")
    
    # Extract user data from state for program agent (include more context for LLM filtering)
    user_data = {
        "who_i_am": state.get("who_i_am", []),
        "state": state.get("state"),
        "what_looking_for": state.get("what_looking_for", []),
        "income": state.get("income"),
        "credit_score": state.get("credit_score"),
        "zip_code": state.get("zip_code"),
        "building_class": state.get("building_class"),
        "current_debt": state.get("current_debt"),
        "residential_units": state.get("residential_units")
    }
    
    # Call the program agent
    program_results = await run_program_agent(user_data)
    
    # Store results in planner state
    state["program_agent_results"] = program_results
    
    state["current_step"] = "program_agent_complete"
    
    return state


async def synthesis_node(state: PlannerState):
    """Synthesize all agent results into final analysis"""
    current_step = state.get('current_step', 'unknown')
    print(f"STEP: {current_step} -> Generating final analysis...")
    
    from langchain_openai import ChatOpenAI
    
    # Get budgeting results to check if we have data
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
        analysis_prompt = get_comprehensive_analysis_prompt(state)
        
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