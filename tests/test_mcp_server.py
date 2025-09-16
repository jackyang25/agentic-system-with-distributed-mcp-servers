"""Test all MCP servers."""

from typing import Callable

from mcp_servers.servers.server_name import server as server_name


class TestMCPServerName:
    """Test the MCP server_name server."""

    def test_add_numbers_tool(self):
        """Test the add_numbers tool."""
        tool = server_name.add_numbers.fn
        assert isinstance(tool, Callable)
        a = 1.0
        b = 1.0
        expected_output = {
            "operation": "addition",
            "expression": f"{a} + {b}",
            "result": a + b,
            "operands": {"a": a, "b": b},
            "operation_type": "arithmetic",
            "properties": {
                "commutative": True,
                "associative": True,
                "identity_element": 0,
            },
        }
        assert tool(a, b) == expected_output
