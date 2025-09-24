import pytest

from mcp_kit.clients.location_client import LocationClient


@pytest.mark.anyio
async def test_location_client_direct() -> None:
    """Test the LocationClient directly with zip code 10002"""
    print("Testing LocationClient directly with zip code 10002...")

    client = LocationClient()

    try:
        # Connect to the location service
        print("Connecting to location service...")
        await client.connect()
        print("Connected!")

        # Get available tools
        print("Getting available tools...")
        tools = await client.get_tools()
        print(f"Available tools: {tools}")

        # Test transit stops
        print("Testing get_transit_stops...")
        result = await client.get_transit_stops("10002")
        print("Success! Result:")
        print(f"Type: {type(result)}")
        print(f"Result: {result}")

        # Disconnect
        print("Disconnecting...")
        await client.disconnect()
        print("Disconnected!")

    except Exception as e:
        print(f"Error testing location client: {e}")
        import traceback

        traceback.print_exc()

        # Try to disconnect even if there was an error
        try:
            await client.disconnect()
        except:
            pytest.fail(reason="Failed to disconnect after error.")
