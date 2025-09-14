"""Test MCP client to all servers."""

import os

import pytest
from fastmcp import Client

from tests.conftest import load_environment_variables


class TestMCPEnhancedMathServer:
    """Test the MCP client for the EnhancedMathServer."""

    @pytest.mark.anyio
    async def test_list_tools_and_resources(self):
        """Test listing tools and resources from the MCP server."""
        load_environment_variables()
        mcp_server_name_name = os.environ.get("MCP_SERVER_NAME_NAME")
        mcp_server_name_port = os.environ.get("MCP_SERVER_NAME_PORT")
        client_url = f"http://{mcp_server_name_name}:{mcp_server_name_port}/mcp"

        async with Client(transport=client_url) as mcp_client:  # <-- open session
            tools = await mcp_client.list_tools()
            resources = await mcp_client.list_resources()

        tool_names = [tool.name for tool in tools]
        resource_names = [resource.name for resource in resources]

        assert "calculate_percentage" in tool_names
        assert "get_server_capabilities" in resource_names
