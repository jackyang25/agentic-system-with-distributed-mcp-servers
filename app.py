import asyncio
from mcp_kit.adapter import adapter

async def test_supabase_mcp():
    """Test client tools via adapter"""
    mcp_adapter = adapter()

    # Connect to all services
    await mcp_adapter.connect_all()
    print("Connection status:", await mcp_adapter.check_running())
    # Show all available tools via adapter
    try:
        all_tools = await mcp_adapter.get_available_tools()
        print(f"All available tools: {all_tools}")
    except Exception as e:
        print(f"Get all tools failed: {e}")
    
    # Test Finance client tools through adapter
    try:
        budget = await mcp_adapter.finance.calculate_budget(50000.0)
        print(f"Finance - Budget calculation: {budget}")
    except Exception as e:
        print(f"Finance - Budget calculation failed: {e}")
    
    # Test Supabase client tools through adapter
    try:
        properties = await mcp_adapter.supabase.query_properties(1)
        print(f"Supabase - Property query: {properties}")
    except Exception as e:
        print(f"Supabase - Property query failed: {e}")

    
    
    await mcp_adapter.disconnect_all()

def main():
    print("Starting MAREA")
    
    # Test Supabase MCP connection
    asyncio.run(test_supabase_mcp())

if __name__ == "__main__":
    main()