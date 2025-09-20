import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_kit.tools import get_transit_score, mcp_adapter

async def test_transit_score():
    """Test the get_transit_score tool with zip code 10002"""
    print("Testing get_transit_score with zip code 10002...")
    
    # Connect the adapter first (since we're not in the FastAPI app)
    print("Connecting to MCP services...")
    await mcp_adapter.connect_all()
    print("Connected!")
    
    try:
        # Test the transit score tool
        result = await get_transit_score.ainvoke({"zip_code": "10002"})
        print("Success! Result:")
        print(f"Type: {type(result)}")
        print(f"Result: {result}")
        
        # Check if result has expected structure
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
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting Location Transit Score Test...")
    print("=" * 50)
    asyncio.run(test_transit_score())
    print("=" * 50)
    print("Test completed!")
