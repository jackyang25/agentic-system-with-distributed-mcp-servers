import asyncio
from mcp_kit.adapter import adapter

async def test_tools(mcp_adapter):
    """Test calculate budget and query properties tools"""
    print("\n" + "="*60)
    print("TESTING TOOLS")
    print("="*60)
    
    # Test Finance client tools through adapter
    print("\nTesting Finance Tool:")
    print("-" * 30)
    try:
        budget = await mcp_adapter.finance.calculate_budget(50000.0)
        print(f"SUCCESS: Budget calculation completed")
        print(f"   Result: {budget}")
    except Exception as e:
        print(f"FAILED: {e}")
    
    # Test Supabase client tools through adapter
    print("\nTesting Supabase Tool:")
    print("-" * 30)
    try:
        properties = await mcp_adapter.supabase.query_home_by_id(7)
        print(f"SUCCESS: Home query completed")
        print(f"   Result: {properties}")
    except Exception as e:
        print(f"FAILED: {e}")
    



async def test_budgeting_agent():
    """Test entry point for budgeting agent workflow"""
    print("\n" + "="*60)
    print("TESTING BUDGETING AGENT")
    print("="*60)
    
    # Mock user data that will be converted to state
    mock_user_data = {
        "income": 75000.0,
        "target_home_id": 7,
        "credit_score": 720,
        "zip_code": "10009"
    }
    
    print(f"\nMock User Data:")
    print(f"  Income: ${mock_user_data['income']:,.0f}")
    print(f"  Target Home ID: {mock_user_data['target_home_id']}")
    print(f"  Credit Score: {mock_user_data['credit_score']}")
    print(f"  Zip Code: {mock_user_data['zip_code']}")
    
    print(f"\nTesting Budgeting Agent Workflow:")
    print("-" * 30)
    
    try:
        # Import and call the budgeting agent
        from agents.budgeting_agent.graph import run_budgeting_agent
        result = await run_budgeting_agent(mock_user_data)
        print(f"SUCCESS: Budgeting agent completed")
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")


async def main():
    print("Starting MAREA")
    
    # Import and use the adapter from tools.py
    from mcp_kit.tools import mcp_adapter
    await mcp_adapter.connect_all()
    print("Connection status:", await mcp_adapter.check_running())
    
    # Test the tools
    await test_tools(mcp_adapter)
    
    # Test the budgeting agent
    await test_budgeting_agent()

    print("="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
    print("\n")
    
    # Clean up connections
    await mcp_adapter.disconnect_all()

if __name__ == "__main__":
    asyncio.run(main())
    