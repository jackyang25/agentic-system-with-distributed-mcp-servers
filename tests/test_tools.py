import pytest
from mcp_kit.tools import mcp_adapter


@pytest.mark.anyio
async def test_tools() -> None:
    print("\n" + "=" * 60)
    print("TESTING TOOLS")
    print("=" * 60)

    # test Finance client tools
    print("\nTesting Finance Tool:")
    print("-" * 30)
    try:
        budget = await mcp_adapter.finance.calculate_budget(income=50000.0)
        print("SUCCESS: Budget calculation completed")
        print(f"   Result: {budget}")
    except Exception as e:
        print(f"FAILED: {e}")

    # test Supabase client tools
    print("\nTesting Supabase Tool:")
    print("-" * 30)
    try:
        properties = await mcp_adapter.supabase.query_home_by_id(home_id=7)
        print("SUCCESS: Home query completed")
        print(f"   Result: {properties}")
    except Exception as e:
        print(f"FAILED: {e}")
