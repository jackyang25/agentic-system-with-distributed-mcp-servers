from logging import Logger
from typing import Any
from langchain_core.messages.base import BaseMessage
from langchain_openai import ChatOpenAI
from agents.program_agent.prompts import (
    create_batch_eligibility_prompt,
    format_program_summary,
    format_user_profile,
)
from agents.program_agent.state import ProgramAgentState
from mcp_kit.tools import search_programs_rag
from utils.convenience import get_logger, get_openai_model
from utils.embedder import NYProgramsEmbedder
from utils.token_tracking import token_usage_tracking

logger: Logger = get_logger(name=__name__)
openai_model: str = get_openai_model()


async def rag_search_programs_node(state: ProgramAgentState) -> ProgramAgentState:
    query_parts: list[Any] = []

    if state.get("who_i_am"):
        query_parts.extend(state["who_i_am"])

    if state.get("state"):
        query_parts.append(state["state"])

    if state.get("what_looking_for"):
        query_parts.extend(state["what_looking_for"])

    search_query: str = (
        " ".join(query_parts) if query_parts else "government assistance programs"
    )

    try:
        embedder = NYProgramsEmbedder()
        query_embedding: list[float] = embedder.generate_embedding(text=search_query)

        rag_result = await search_programs_rag.ainvoke(
            input={"embedding": query_embedding, "limit": 10}
        )

        if "error" in rag_result:
            state["program_matcher_results"] = []
            logger.info(f"RAG search error: {rag_result['error']}")
        else:
            programs = rag_result.get("programs", [])
            state["program_matcher_results"] = programs

            if programs:
                logger.info(f"RAG search result: {programs[:1]}")
            else:
                logger.info("RAG search result: No programs found")

    except Exception:
        state["program_matcher_results"] = []

    state["current_step"] = "search_complete"
    return state


async def filter_programs_node(state: ProgramAgentState) -> ProgramAgentState:
    programs = state.get("program_matcher_results", [])
    if not programs:
        logger.info("No programs to filter")
        state["current_step"] = "filter_complete"
        return state

    user_profile: str = format_user_profile(state=state)

    programs_text: str = "\n\n".join(
        [
            f"Program {i + 1}:\n{format_program_summary(program=program)}"
            for i, program in enumerate(programs)
        ]
    )

    batch_prompt: str = create_batch_eligibility_prompt(
        user_profile=user_profile, programs_text=programs_text
    )

    try:
        model = ChatOpenAI(model=openai_model, temperature=0, timeout=30, max_retries=2)
        response: BaseMessage = await model.ainvoke(input=batch_prompt)
        updated_token_usage: dict[str, Any] = token_usage_tracking(
            token_history=state.get("usage_metadata"),
            usage_data=response.usage_metadata,
        )
        decisions_text: str = response.content.strip()

        state["filtered_programs"] = decisions_text

        state["programs_text"] = programs_text

        state["usage_metadata"] = updated_token_usage

    except Exception as e:
        logger.info(f"Error in batch filtering: {e}")
        state["filtered_programs"] = programs_text

    state["current_step"] = "filter_complete"
    return state
