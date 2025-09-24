"""Nodes for the Planner Agent workflow."""

from logging import Logger
from typing import Any

from langchain_core.messages.base import BaseMessage

from agents.budgeting_agent.graph import run_budgeting_agent
from agents.geoscout_agent.graph import run_geoscout_agent
from agents.planner_agent.prompts import get_comprehensive_analysis_prompt
from agents.planner_agent.state import PlannerState
from agents.program_agent.graph import run_program_agent
from utils.convenience import get_logger, get_openai_model

logger: Logger = get_logger(name=__name__)

openai_model: str = get_openai_model()


async def run_budgeting_agent_node(state: PlannerState) -> PlannerState:
    """Call the budgeting agent and store results in state"""
    current_step: str = state.get("current_step", "unknown")
    logger.info(f"STEP: {current_step} -> Calling budgeting agent...")

    # Extract user data from state
    user_data: dict[str, Any] = {
        "income": state["income"],
        "credit_score": state["credit_score"],
        "zip_code": state["zip_code"],
        "residential_units": state["residential_units"],
    }

    # Call the budgeting agent
    budgeting_results: Any = await run_budgeting_agent(user_data=user_data)

    # Store results in state
    state["budgeting_agent_results"] = budgeting_results

    # Extract primitive values for easy access
    state["monthly_budget"] = budgeting_results.get("monthly_budget")
    state["max_loan"] = budgeting_results.get("max_loan")
    state["price_data"] = budgeting_results.get("price_data")

    state["current_step"] = "budgeting_complete"

    return state


async def run_program_agent_node(state: PlannerState) -> PlannerState:
    """Call the program agent and store results in state"""
    current_step: str = state.get("current_step", "unknown")
    logger.info(f"STEP: {current_step} -> Calling program agent...")

    # Extract user data from state for program agent (include more context for LLM filtering)
    user_data: dict[str, Any] = {
        "who_i_am": state.get("who_i_am", []),
        "state": state.get("state"),
        "what_looking_for": state.get("what_looking_for", []),
        "income": state.get("income"),
        "credit_score": state.get("credit_score"),
        "zip_code": state.get("zip_code"),
        "building_class": state.get("building_class"),
        "current_debt": state.get("current_debt"),
        "residential_units": state.get("residential_units"),
    }

    # Call the program agent
    program_results: Any = await run_program_agent(user_data=user_data)

    # Store results in planner state
    state["program_agent_results"] = program_results

    state["current_step"] = "program_agent_complete"

    return state


async def run_geoscout_agent_node(state: PlannerState) -> PlannerState:
    """Call the geoscout agent and store results in state"""
    current_step: str = state.get("current_step", "unknown")
    logger.info(f"STEP: {current_step} -> Calling geoscout agent...")

    # Extract user data from state
    user_data: dict[str, Any] = {
        "income": state["income"],
        "credit_score": state["credit_score"],
        "zip_code": state["zip_code"],
    }

    # Call the geoscout agent
    geoscout_results: dict[str, Any] = await run_geoscout_agent(user_data=user_data)

    # Store results in state
    state["geoscout_agent_results"] = geoscout_results
    state["current_step"] = "geoscout_complete"

    return state


async def synthesis_node(state: PlannerState) -> PlannerState:
    """Synthesize all agent results into final analysis"""
    current_step: str = state.get("current_step", "unknown")
    logger.info(f"STEP: {current_step} -> Generating final analysis...")

    from langchain_openai import ChatOpenAI

    # Get budgeting results to check if we have data
    budgeting_results: dict[str, Any] = state.get("budgeting_agent_results", {})

    if budgeting_results:
        logger.info("   Calling LLM for analysis...")
        # Use LLM to provide comprehensive analysis
        model = ChatOpenAI(
            model=openai_model,
            timeout=30,  # 30 second timeout
            max_retries=2,
        )

        # Get the comprehensive analysis prompt from prompts.py
        analysis_prompt: str = get_comprehensive_analysis_prompt(state=state)

        try:
            response: BaseMessage = await model.ainvoke(input=analysis_prompt)
            analysis: str = response.content
            logger.info("   LLM analysis completed")
        except Exception as e:
            logger.info(f"   LLM analysis failed: {e}")
            analysis = f"Analysis unavailable due to error: {str(e)}"
    else:
        analysis = "No budgeting results available for analysis."

    state["final_analysis"] = analysis
    state["current_step"] = "synthesis_complete"

    return state
