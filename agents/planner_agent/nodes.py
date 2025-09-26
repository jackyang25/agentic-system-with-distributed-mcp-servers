"""Nodes for the Planner Agent workflow."""

from copy import deepcopy
from logging import Logger
from typing import Any

from langchain_core.messages.base import BaseMessage
from langchain_openai import ChatOpenAI

from agents.budgeting_agent.graph import run_budgeting_agent
from agents.geoscout_agent.graph import run_geoscout_agent
from agents.planner_agent.prompts import get_comprehensive_analysis_prompt
from agents.planner_agent.state import PlannerState
from agents.program_agent.graph import run_program_agent
from utils.convenience import get_logger, get_openai_model
from utils.token_tracking import token_usage_tracking

logger: Logger = get_logger(name=__name__)

openai_model: str = get_openai_model()


async def run_budgeting_agent_node(state: PlannerState) -> PlannerState:
    """Call the budgeting agent and store results in state"""
    agent_state = deepcopy(state)
    current_step: str = agent_state.get("current_step", "unknown")
    logger.info(f"STEP: {current_step} -> Calling budgeting agent...")

    # Extract user data from state
    user_data: dict[str, Any] = {
        "income": agent_state["income"],
        "credit_score": agent_state["credit_score"],
        "zip_code": agent_state["zip_code"],
        "residential_units": agent_state["residential_units"],
        "usage_metadata": agent_state.get("usage_metadata"),
    }

    # Call the budgeting agent
    budgeting_results: Any = await run_budgeting_agent(user_data=user_data)

    # Store results in state
    agent_state["budgeting_agent_results"] = budgeting_results

    # Extract primitive values for easy access
    agent_state["monthly_budget"] = budgeting_results.get("monthly_budget")
    agent_state["max_loan"] = budgeting_results.get("max_loan")
    agent_state["price_data"] = budgeting_results.get("price_data")

    agent_state["current_step"] = "budgeting_complete"
    agent_state["usage_metadata"] = budgeting_results.get("usage_metadata")

    return agent_state


async def run_program_agent_node(state: PlannerState) -> PlannerState:
    """Call the program agent and store results in state"""
    agent_state = deepcopy(state)
    current_step: str = agent_state.get("current_step", "unknown")
    logger.info(f"STEP: {current_step} -> Calling program agent...")

    # Extract user data from state for program agent (include more context for LLM filtering)
    user_data: dict[str, Any] = {
        "who_i_am": agent_state.get("who_i_am", []),
        "state": agent_state.get("state"),
        "what_looking_for": agent_state.get("what_looking_for", []),
        "income": agent_state.get("income"),
        "credit_score": agent_state.get("credit_score"),
        "zip_code": agent_state.get("zip_code"),
        "building_class": agent_state.get("building_class"),
        "current_debt": agent_state.get("current_debt"),
        "residential_units": agent_state.get("residential_units"),
        "usage_metadata": agent_state.get("usage_metadata"),
    }

    # Call the program agent
    program_results: Any = await run_program_agent(user_data=user_data)

    # Store results in planner state
    agent_state["program_agent_results"] = program_results
    agent_state["usage_metadata"] = program_results.get("usage_metadata")

    agent_state["current_step"] = "program_agent_complete"

    return agent_state


async def run_geoscout_agent_node(state: PlannerState) -> PlannerState:
    """Call the geoscout agent and store results in state"""
    agent_state = deepcopy(state)
    current_step: str = agent_state.get("current_step", "unknown")
    logger.info(f"STEP: {current_step} -> Calling geoscout agent...")

    # Extract user data from state
    user_data: dict[str, Any] = {
        "income": agent_state["income"],
        "credit_score": agent_state["credit_score"],
        "zip_code": agent_state["zip_code"],
        "usage_metadata": agent_state.get("usage_metadata"),
    }

    # Call the geoscout agent
    geoscout_results: dict[str, Any] = await run_geoscout_agent(user_data=user_data)

    # Store results in state
    agent_state["geoscout_agent_results"] = geoscout_results
    agent_state["usage_metadata"] = geoscout_results.get("usage_metadata")
    agent_state["current_step"] = "geoscout_complete"

    return agent_state


async def run_nodes(state: PlannerState) -> PlannerState:
    """Run all nodes in sequence for testing purposes"""
    budget_state = await run_budgeting_agent_node(state=state)
    program_state = await run_program_agent_node(state=state)
    geoscout_state = await run_geoscout_agent_node(state=state)
    # Budgeting state updates
    state.update(
        {
            "budgeting_agent_results": budget_state,
            "monthly_budget": budget_state.get("monthly_budget"),
            "max_loan": budget_state.get("max_loan"),
            "price_data": budget_state.get("price_data"),
            "property_data": budget_state.get("property_data"),
        }
    )

    # Geoscout state updates
    state.update(
        {
            "geoscout_agent_results": geoscout_state,
        }
    )

    # Program state updates
    state.update(
        {
            "program_agent_results": program_state,
        }
    )
    budget_token = budget_state.get("usage_metadata", {})
    program_token = program_state.get("usage_metadata", {})
    geoscout_token = geoscout_state.get("usage_metadata", {})
    total_token_usage = token_usage_tracking(
        token_history=state.get("usage_metadata"),
        usage_data=budget_token,
    )
    total_token_usage = token_usage_tracking(
        token_history=total_token_usage,
        usage_data=program_token,
    )
    total_token_usage = token_usage_tracking(
        token_history=total_token_usage,
        usage_data=geoscout_token,
    )
    state["usage_metadata"] = total_token_usage

    return state


async def synthesis_node(state: PlannerState) -> PlannerState:
    """Synthesize all agent results into final analysis"""
    current_step: str = state.get("current_step", "unknown")
    logger.info(f"STEP: {current_step} -> Generating final analysis...")

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
            updated_token_usage: dict[str, Any] = token_usage_tracking(
                token_history=state.get("usage_metadata"),
                usage_data=response.usage_metadata,
            )
            analysis: str = response.content
            logger.info("   LLM analysis completed")
        except Exception as e:
            logger.info(f"   LLM analysis failed: {e}")
            analysis = f"Analysis unavailable due to error: {str(e)}"
    else:
        analysis = "No budgeting results available for analysis."

    state["final_analysis"] = analysis
    state["usage_metadata"] = updated_token_usage
    state["current_step"] = "synthesis_complete"
    logger.info(
        f"Total token usage for all agents and synthesis: {state['usage_metadata']}"
    )
    logger.info("Workflow complete.")

    return state
