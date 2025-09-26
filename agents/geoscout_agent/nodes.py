"""Geoscout agent nodes."""

from typing import Any

from langchain_core.messages.base import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.geoscout_agent.prompts import (
    CommuteStructure,
    CrimeStructure,
    SchoolStructure,
    get_crime_score_prompt,
    get_school_score_prompt,
    get_synthesizer_prompt,
    get_transit_score_prompt,
)
from agents.geoscout_agent.state import GeoScoutState
from mcp_kit.tools import get_transit_score
from utils.convenience import get_gemini_model
from utils.token_tracking import token_usage_tracking

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
    llm = ChatGoogleGenerativeAI(model=gemini_model, stream_usage=True)
    structured_llm = llm.with_structured_output(
        schema=CommuteStructure,
        method="json_mode",
    )
    prompt: str = get_transit_score_prompt(
        zipcode=state["zip_code"], commute_result=transit_score
    )
    usage = None

    structured: CommuteStructure | None = None

    async for ev in structured_llm.astream_events(input=prompt):
        if ev["event"] == "on_chat_model_end":
            usage = ev["data"]["output"].usage_metadata  # AIMessage.usage_metadata
        elif ev["event"] == "on_chain_end" and ev["name"] == "RunnableSequence":
            structured = ev["data"]["output"]  # CommuteStructure
    updated_token_usage: dict[str, Any] = token_usage_tracking(
        token_history=state.get("usage_metadata"),
        usage_data=usage,
    )
    state.update(
        {
            "transit_summary": structured.transit_summary,
            "usage_metadata": updated_token_usage,
        }
    )
    return state


async def node_crime_rate(state: GeoScoutState) -> GeoScoutState:
    """Calculate maximum loan amount based on income and credit score"""
    llm = ChatGoogleGenerativeAI(model=gemini_model, stream_usage=True)
    prompt: str = get_crime_score_prompt(zipcode=state["zip_code"])
    structured_llm = llm.with_structured_output(
        schema=CrimeStructure,
        method="json_mode",
    )
    usage = None

    structured: CommuteStructure | None = None

    async for ev in structured_llm.astream_events(input=prompt):
        if ev["event"] == "on_chat_model_end":
            usage = ev["data"]["output"].usage_metadata  # AIMessage.usage_metadata
        elif ev["event"] == "on_chain_end" and ev["name"] == "RunnableSequence":
            structured = ev["data"]["output"]  # CommuteStructure
    updated_token_usage: dict[str, Any] = token_usage_tracking(
        token_history=state.get("usage_metadata"),
        usage_data=usage,
    )
    state.update(
        {
            "crime_summary": structured.crime_summary,
            "crime_score": structured.crime_score,
            "usage_metadata": updated_token_usage,
        }
    )
    return state


async def node_school_rate(state: GeoScoutState) -> GeoScoutState:
    """Calculate maximum loan amount based on income and credit score"""
    llm = ChatGoogleGenerativeAI(model=gemini_model, stream_usage=True)
    prompt: str = get_school_score_prompt(zipcode=state["zip_code"])
    structured_llm = llm.with_structured_output(
        schema=SchoolStructure,
        method="json_mode",
    )
    usage = None

    structured: CommuteStructure | None = None

    async for ev in structured_llm.astream_events(input=prompt):
        if ev["event"] == "on_chat_model_end":
            usage = ev["data"]["output"].usage_metadata  # AIMessage.usage_metadata
        elif ev["event"] == "on_chain_end" and ev["name"] == "RunnableSequence":
            structured = ev["data"]["output"]  # CommuteStructure
    updated_token_usage: dict[str, Any] = token_usage_tracking(
        token_history=state.get("usage_metadata"),
        usage_data=usage,
    )
    state.update(
        {
            "school_summary": structured.school_summary,
            "school_score": structured.school_score,
            "usage_metadata": updated_token_usage,
        }
    )
    return state


async def node_synthesizer(state: GeoScoutState) -> GeoScoutState:
    """Calculate maximum loan amount based on income and credit score"""
    llm = ChatGoogleGenerativeAI(model=gemini_model)
    prompt: str = get_synthesizer_prompt(commute_state=state)
    response: BaseMessage = await llm.ainvoke(input=prompt)
    updated_token_usage: dict[str, Any] = token_usage_tracking(
        token_history=state.get("usage_metadata"),
        usage_data=response.usage_metadata,
    )
    state.update(
        {
            "total_summary": response.content,
            "usage_metadata": updated_token_usage,
        }
    )
    return state
