from langchain_core.tools import tool  
from mcp_kit.adapter import adapter

# Global adapter instance
mcp_adapter = adapter()

@tool
async def calculate_budget(income: float) -> dict:
    """Calculate 30% budget from income using Finance MCP"""
    result = await mcp_adapter.finance.calculate_budget(income)
    return {"budget": result}

@tool
async def query_properties(limit: int = 1) -> dict:
    """Query NYC property sales data using Supabase MCP"""
    result = await mcp_adapter.supabase.query_properties(limit)
    return {"properties": result}


