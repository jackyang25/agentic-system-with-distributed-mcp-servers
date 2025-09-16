"""Create client to interact with MCP servers."""

import os

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from mcp.types import Resource, Tool


async def get_mcp_data() -> None:
    mcp_server_name_name = os.environ["MCP_SERVER_NAME_NAME"]
    mcp_server_name_port = os.environ["MCP_SERVER_NAME_PORT"]

    client: Client[StreamableHttpTransport] = Client(
        transport=f"http://{mcp_server_name_name}:{mcp_server_name_port}/mcp"
    )
    async with client:
        tools: list[Tool] = await client.list_tools()
        resources: list[Resource] = await client.list_resources()
        for tool in tools:
            print(tool.name, tool.description, tool.title)
        print("-" * 20)
        for resource in resources:
            print(resource.name, resource.description)
