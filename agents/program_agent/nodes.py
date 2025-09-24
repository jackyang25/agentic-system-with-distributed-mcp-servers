"""Nodes for the Program Agent workflow."""

from logging import Logger
from typing import Any

from langchain_core.messages.base import BaseMessage

from agents.program_agent.prompts import (
    create_batch_eligibility_prompt,
    format_program_summary,
    format_user_profile,
)
from agents.program_agent.state import ProgramAgentState
from mcp_kit.tools import search_programs_rag
from utils.convenience import get_logger, get_openai_model
from utils.embedder import NYProgramsEmbedder

logger: Logger = get_logger(name=__name__)

openai_model: str = get_openai_model()


async def rag_search_programs_node(state: ProgramAgentState) -> ProgramAgentState:
    """Search for government programs using RAG"""

    # Build search query from user data
    query_parts: list[Any] = []

    # Add who_i_am selections
    if state.get("who_i_am"):
        query_parts.extend(state["who_i_am"])

    # Add state
    if state.get("state"):
        query_parts.append(state["state"])

    # Add what_looking_for selections
    if state.get("what_looking_for"):
        query_parts.extend(state["what_looking_for"])

    # Combine into search query
    search_query: str = (
        " ".join(query_parts) if query_parts else "government assistance programs"
    )

    try:
        # Generate embedding for the search query using the embedder
        embedder = NYProgramsEmbedder()
        query_embedding: list[float] = embedder.generate_embedding(text=search_query)

        # Call RAG search tool with the embedding
        rag_result = await search_programs_rag.ainvoke(
            input={"embedding": query_embedding, "limit": 10}
        )

        if "error" in rag_result:
            state["program_matcher_results"] = []
            logger.info(f"RAG search error: {rag_result['error']}")
        else:
            # Extract programs from RAG result
            programs = rag_result.get("programs", [])
            state["program_matcher_results"] = programs

            # Log RAG results (limit to 1 element for brevity)
            if programs:
                logger.info(f"RAG search result: {programs[:1]}")
            else:
                logger.info("RAG search result: No programs found")

    except Exception:
        state["program_matcher_results"] = []

    state["current_step"] = "search_complete"
    return state


async def filter_programs_node(state: ProgramAgentState) -> ProgramAgentState:
    """Filter programs using LLM to determine user eligibility"""
    programs = state.get("program_matcher_results", [])
    if not programs:
        logger.info("No programs to filter")
        state["current_step"] = "filter_complete"
        return state

    from langchain_openai import ChatOpenAI

    # Initialize LLM
    model = ChatOpenAI(model=openai_model, temperature=0, timeout=30, max_retries=2)

    # Create user profile using prompt function
    user_profile: str = format_user_profile(state=state)

    # Store programs as string for access outside prompt
    programs_text: str = "\n\n".join(
        [
            f"Program {i + 1}:\n{format_program_summary(program=program)}"
            for i, program in enumerate(programs)
        ]
    )

    # Create batch prompt using prompt function
    batch_prompt: str = create_batch_eligibility_prompt(
        user_profile=user_profile, programs_text=programs_text
    )

    try:
        response: BaseMessage = await model.ainvoke(input=batch_prompt)
        decisions_text: str = response.content.strip()

        # Store LLM response as filtered programs (LLM already filtered)
        state["filtered_programs"] = decisions_text

        # Also store the original programs as string for reference
        state["programs_text"] = programs_text

    except Exception as e:
        logger.info(f"Error in batch filtering: {e}")
        # Fallback: include all programs if batch processing fails
        state["filtered_programs"] = programs_text

    state["current_step"] = "filter_complete"
    return state
