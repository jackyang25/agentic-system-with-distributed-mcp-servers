import asyncio
import os
from contextlib import _AsyncGeneratorContextManager
from logging import Logger
from typing import Any

from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from dotenv import load_dotenv
from mcp import ClientSession, ListToolsResult, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.message import SessionMessage
from mcp.types import CallToolResult

from utils.convenience import get_logger

logger: Logger = get_logger(name=__name__)

# Load environment variables from .env file
load_dotenv()


class LocationClient:
    def __init__(self, container_name="location-mcp-server") -> None:
        self.container_name: str = container_name
        self.server_params: StdioServerParameters = StdioServerParameters(
            command="docker",
            args=[
                "exec",
                "-e",
                f"WALKSCORE_API_KEY={os.getenv('WALKSCORE_API_KEY', 'your-api-key')}",
                "-i",
                container_name,
                "python",
                "server.py",
            ],
        )
        self.session = None
        self._stdio_context = None
        self._session_context = None

    async def connect(self) -> None:
        """Establish persistent connection to Location MCP server"""
        if self.session:
            return

        # Use proper async with pattern
        self._stdio_context: _AsyncGeneratorContextManager[
            tuple[
                MemoryObjectReceiveStream[SessionMessage | Exception],
                MemoryObjectSendStream[SessionMessage],
            ],
            None,
        ] = stdio_client(server=self.server_params)
        read_stream, write_stream = await self._stdio_context.__aenter__()

        self._session_context = ClientSession(
            read_stream=read_stream, write_stream=write_stream
        )
        self.session: ClientSession = await self._session_context.__aenter__()

        await self.session.initialize()
        logger.info("Connected to Location MCP server")

    async def disconnect(self) -> None:
        """Close the persistent connection"""
        if not self.session:
            return

        try:
            if self._session_context:
                await self._session_context.__aexit__(
                    exc_type=None, exc_val=None, exc_tb=None
                )
        except (Exception, asyncio.CancelledError):
            pass  # Ignore cleanup errors

        try:
            if self._stdio_context:
                await self._stdio_context.__aexit__(
                    typ=None, value=None, traceback=None
                )
        except (Exception, asyncio.CancelledError):
            pass  # Ignore cleanup errors

        self.session = None
        self._session_context = None
        self._stdio_context = None
        logger.info("Disconnected from Location MCP server")

    async def get_tools(self) -> list[str]:
        """Get available tools"""
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")
        tools_response: ListToolsResult = await self.session.list_tools()
        return [tool.name for tool in tools_response.tools]

    async def get_transit_score(self, zip_code: str) -> dict[str, Any]:
        """Get transit score and summary for a specific location"""
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")
        result: CallToolResult = await self.session.call_tool(
            name="get_transit_score", arguments={"zip_code": zip_code}
        )
        return self._parse_location_data(result=result, data_type="transit_score")

    def _parse_location_data(
        self, result: CallToolResult, data_type: str
    ) -> dict[str, Any]:
        """Parse MCP result and return clean location data"""
        if not result or not hasattr(result, "content") or not result.content:
            return result

        try:
            # The result.content is a list of TextContent objects
            if not isinstance(result.content, list) or len(result.content) == 0:
                return result

            content_text = result.content[0].text
            if not isinstance(content_text, str):
                return result

            # Try to parse as JSON first
            import json

            try:
                data: dict[str, Any] = json.loads(content_text)
                return data
            except json.JSONDecodeError:
                # If not JSON, return as text
                return {"data_type": data_type, "data": content_text}
        except (ValueError, TypeError, AttributeError):
            # If parsing fails, return original result
            return result
