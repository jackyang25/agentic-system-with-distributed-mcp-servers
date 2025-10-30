import pytest
import traceback
from mcp_kit.tools import get_transit_score, mcp_adapter


@pytest.mark.anyio
async def test_transit_score():
    print("Testing get_transit_score with zip code 10002...")
    print("Connecting to MCP services...")
    await mcp_adapter.connect_all()
    print("Connected!")

    try:
        result = await get_transit_score.ainvoke({"zip_code": "10002"})
        print("Success! Result:")
        print(f"Type: {type(result)}")
        print(f"Result: {result}")

        if isinstance(result, dict) and "transit_score" in result:
            transit_data = result["transit_score"]
            print(f"\nTransit Data Type: {type(transit_data)}")
            if isinstance(transit_data, dict):
                print(f"Keys: {list(transit_data.keys())}")
                if "transit_score" in transit_data:
                    print(f"Transit Score: {transit_data['transit_score']}/100")
                if "description" in transit_data:
                    print(f"Description: {transit_data['description']}")
                if "summary" in transit_data:
                    print(f"Summary: {transit_data['summary']}")
                if "status" in transit_data:
                    print(f"Status: {transit_data['status']}")
        else:
            print(f"Unexpected result structure: {result}")

    except Exception as e:
        print(f"Error testing transit score: {e}")
        traceback.print_exc()
