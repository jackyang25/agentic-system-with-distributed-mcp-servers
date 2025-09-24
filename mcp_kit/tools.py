from typing import Any

from langchain_core.tools import tool

from mcp_kit.adapter import Adapter

# Global adapter instance
mcp_adapter = Adapter()


@tool
async def calculate_budget(income: float) -> dict[str, Any]:
    """Calculate 30% budget from income using Finance MCP"""
    result: dict[str, Any] = await mcp_adapter.finance.calculate_budget(income=income)
    return result


@tool
async def loan_qualification(income: float, credit_score: int) -> dict[str, Any]:
    """Calculate maximum loan amount based on income and credit score using Finance MCP"""
    result: dict[str, Any] = await mcp_adapter.finance.loan_qualification(
        income=income, credit_score=credit_score
    )
    return result


@tool
async def query_home_by_id(home_id: int) -> dict[str, Any]:
    """Query NYC property sales data using Supabase MCP by HOME_ID"""
    result: dict[str, Any] = await mcp_adapter.supabase.query_home_by_id(
        home_id=home_id
    )
    return result


@tool
async def get_transit_score(zip_code: str) -> dict[str, Any]:
    """Get transit score and summary for a specific location using Location MCP"""
    result: dict[str, Any] = await mcp_adapter.location.get_transit_score(
        zip_code=zip_code
    )
    return result


@tool
async def query_price_data_by_zip_and_units(
    zip_code: str, residential_units: int
) -> dict[str, Any]:
    """Query comprehensive price data by zip code and residential units using Supabase MCP"""
    result: dict[
        str, Any
    ] = await mcp_adapter.supabase.query_price_data_by_zip_and_units(
        zip_code=zip_code, residential_units=residential_units
    )
    return result


@tool
async def search_programs_rag(embedding: list, limit: int = 10) -> dict[str, Any]:
    """Search government programs using vector similarity search with RAG using embedding"""
    result: dict[str, Any] = await mcp_adapter.supabase.search_programs_rag(
        embedding=embedding, limit=limit
    )
    return result
