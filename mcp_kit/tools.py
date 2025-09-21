from langchain_core.tools import tool  
from mcp_kit.adapter import adapter

# Global adapter instance
mcp_adapter = adapter()

@tool
async def calculate_budget(income: float) -> dict:
    """Calculate 30% budget from income using Finance MCP"""
    result = await mcp_adapter.finance.calculate_budget(income)
    return result

@tool
async def loan_qualification(income: float, credit_score: int) -> dict:
    """Calculate maximum loan amount based on income and credit score using Finance MCP"""
    result = await mcp_adapter.finance.loan_qualification(income, credit_score)
    return result

@tool
async def query_home_by_id(home_id: int) -> dict:
    """Query NYC property sales data using Supabase MCP by HOME_ID"""
    result = await mcp_adapter.supabase.query_home_by_id(home_id)
    return result

@tool
async def get_transit_score(zip_code: str) -> dict:
    """Get transit score and summary for a specific location using Location MCP"""
    result = await mcp_adapter.location.get_transit_score(zip_code)
    return result

@tool
async def query_price_data_by_zip_and_units(zip_code: str, residential_units: int) -> dict:
    """Query comprehensive price data by zip code and residential units using Supabase MCP"""
    result = await mcp_adapter.supabase.query_price_data_by_zip_and_units(zip_code, residential_units)
    return result

