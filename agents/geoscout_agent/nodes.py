"""Geoscout agent nodes."""

from typing import Any

from langchain_core.messages.base import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.geoscout_agent.prompts import (
    CommuteStructure,
    CrimeStructure,
    get_crime_score_prompt,
    get_synthesizer_prompt,
    get_transit_score_prompt,
)
from agents.geoscout_agent.state import GeoScoutState
from mcp_kit.tools import get_transit_score
from utils.convenience import get_gemini_model

gemini_model: str = get_gemini_model()


async def node_commute_score(state: GeoScoutState) -> GeoScoutState:
    """Calculate maximum loan amount based on income and credit score"""
    transit_score: dict[str, Any] = await get_transit_score.ainvoke(
        input={"zip_code": state["zip_code"]}
    )
    state.update(
        {
            "current_step": "commute_score",
            "step_count": 1,
            "error_count": 0,
            "transit_score": transit_score.get("transit_score", 0),
            "transit_summary": transit_score.get("summary", ""),
        }
    )
    llm = ChatGoogleGenerativeAI(model=gemini_model)
    structured_llm = llm.with_structured_output(
        schema=CommuteStructure,
        method="json_mode",
    )
    prompt: str = get_transit_score_prompt(
        zipcode=state["zip_code"], commute_result=transit_score
    )
    response: BaseMessage = await structured_llm.ainvoke(input=prompt)
    state.update(
        {
            "transit_summary": response.transit_summary,
        }
    )
    return state


async def node_crime_rate(state: GeoScoutState) -> GeoScoutState:
    """Calculate maximum loan amount based on income and credit score"""
    llm = ChatGoogleGenerativeAI(model=gemini_model)
    prompt: str = get_crime_score_prompt(zipcode=state["zip_code"])
    structured_llm = llm.with_structured_output(
        schema=CrimeStructure,
        method="json_mode",
    )
    response: BaseMessage = await structured_llm.ainvoke(input=prompt)
    state.update(
        {
            "crime_summary": response.crime_summary,
            "crime_score": response.crime_score,
        }
    )
    return state


async def node_synthesizer(state: GeoScoutState) -> GeoScoutState:
    """Calculate maximum loan amount based on income and credit score"""
    llm = ChatGoogleGenerativeAI(model=gemini_model)
    prompt: str = get_synthesizer_prompt(commute_state=state)
    response: BaseMessage = await llm.ainvoke(input=prompt)
    state.update(
        {
            "total_summary": response.content,
        }
    )
    return state
