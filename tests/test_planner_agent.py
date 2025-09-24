import pytest

from mcp_kit.tools import mcp_adapter


@pytest.mark.anyio
async def test_tools() -> None:
    """Test calculate budget and query properties tools"""
    print("\n" + "=" * 60)
    print("TESTING TOOLS")
    print("=" * 60)

    # Test Finance client tools through adapter
    print("\nTesting Finance Tool:")
    print("-" * 30)
    try:
        budget = await mcp_adapter.finance.calculate_budget(income=50000.0)
        print("SUCCESS: Budget calculation completed")
        print(f"   Result: {budget}")
    except Exception as e:
        print(f"FAILED: {e}")

    # Test Supabase client tools through adapter
    print("\nTesting Supabase Tool:")
    print("-" * 30)
    try:
        properties = await mcp_adapter.supabase.query_home_by_id(home_id=7)
        print("SUCCESS: Home query completed")
        print(f"   Result: {properties}")
    except Exception as e:
        print(f"FAILED: {e}")


@pytest.mark.anyio
async def test_planner_agent() -> None:
    """Test entry point for planner agent workflow"""
    print("\n" + "=" * 60)
    print("TESTING PLANNER AGENT")
    print("=" * 60)

    # Mock user data that will be converted to state
    mock_user_data = {
        "income": 75000.0,
        "target_home_id": 7,
        "credit_score": 720,
        "zip_code": "10009",
    }

    print("\nMock User Data:")
    print(f"  Income: ${mock_user_data['income']:,.0f}")
    print(f"  Target Home ID: {mock_user_data['target_home_id']}")
    print(f"  Credit Score: {mock_user_data['credit_score']}")
    print(f"  Zip Code: {mock_user_data['zip_code']}")

    print("\nTesting Planner Agent Workflow:")
    print("-" * 30)

    try:
        # Import and call the planner agent
        from agents.planner_agent.graph import run_planner_agent

        result = await run_planner_agent(user_data=mock_user_data)
        print("SUCCESS: Planner agent completed")

        # Format the result for better readability
        print("\n" + "=" * 60)
        print("PLANNER AGENT RESULTS")
        print("=" * 60)

        # Show gathered data
        print("\nGATHERED DATA:")
        print("-" * 30)
        if result.get("budgeting_agent_results"):
            budget_data = result["budgeting_agent_results"]
            print(f"• Income: ${budget_data.get('income', 'N/A'):,.2f}")
            print(f"• Credit Score: {budget_data.get('credit_score', 'N/A')}")
            print(f"• Target Home ID: {budget_data.get('target_home_id', 'N/A')}")
            print(f"• Zip Code: {budget_data.get('zip_code', 'N/A')}")

            budget_result = budget_data.get("budget_result", {}).get("budget", {})
            loan_result = budget_data.get("loan_result", {}).get("max_loan", {})

            print(
                f"• Monthly Budget (30% of income): ${budget_result.get('budget', 'N/A'):,.2f}"
            )
            print(
                f"• Maximum Loan Qualification: ${loan_result.get('max_loan', 'N/A'):,.2f}"
            )
        else:
            print("• No budgeting data available")

        # Show analysis
        print("\nFINAL ANALYSIS:")
        print("-" * 30)
        if result.get("final_analysis"):
            print(result["final_analysis"])
        else:
            print("No analysis available")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"FAILED: {e}")
        import traceback

        traceback.print_exc()

    print("\n")
