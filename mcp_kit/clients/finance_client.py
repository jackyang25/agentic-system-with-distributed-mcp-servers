import asyncio
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

load_dotenv()


class FinanceClient:
    def __init__(self, container_name="finance-mcp-server") -> None:
        self.container_name: str = container_name
        self.server_params = StdioServerParameters(
            command="docker", args=["exec", "-i", container_name, "python", "server.py"]
        )
        self.session = None
        self._stdio_context = None
        self._session_context = None

    async def connect(self) -> None:
        if self.session:
            return

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
        logger.info("Connected to Finance MCP server")

    async def disconnect(self) -> None:
        if not self.session:
            return

        try:
            if self._session_context:
                await self._session_context.__aexit__(
                    exc_type=None, exc_val=None, exc_tb=None
                )
        except (Exception, asyncio.CancelledError):
            pass

        try:
            if self._stdio_context:
                await self._stdio_context.__aexit__(
                    typ=None, value=None, traceback=None
                )
        except (Exception, asyncio.CancelledError):
            pass

        self.session = None
        self._session_context = None
        self._stdio_context = None
        logger.info("Disconnected from Finance MCP server")

    async def get_tools(self) -> list[str]:
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")
        tools_response: ListToolsResult = await self.session.list_tools()
        return [tool.name for tool in tools_response.tools]

    async def calculate_budget(self, income: float) -> dict[str, Any]:
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")
        result: CallToolResult = await self.session.call_tool(
            name="calculate_budget", arguments={"income": income}
        )
        return self._parse_budget_data(result=result, income=income)

    async def loan_qualification(
        self, income: float, credit_score: int
    ) -> dict[str, Any]:
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")
        result: CallToolResult = await self.session.call_tool(
            name="loan_qualification",
            arguments={"income": income, "credit_score": credit_score},
        )
        return self._parse_loan_data(result=result)

    def _parse_budget_data(
        self, result: CallToolResult, income: float
    ) -> dict[str, Any]:
        if not result or not hasattr(result, "content") or not result.content:
            return {"error": "No result from MCP server", "raw_result": str(result)}

        try:
            if not isinstance(result.content, list) or len(result.content) == 0:
                return {"error": "Invalid result format", "raw_result": str(result)}

            content_text = result.content[0].text
            if not isinstance(content_text, str):
                return {"error": "Invalid result format", "raw_result": str(result)}

            budget_value = float(content_text)

            monthly_budget: float = budget_value / 12
            return {
                "budget": monthly_budget,
                "yearly_budget": budget_value,
                "income": income,
                "percentage": 0.30,
            }
        except (ValueError, TypeError, AttributeError):
            return {"error": "Failed to parse budget data", "raw_result": str(result)}

    def _parse_loan_data(self, result: CallToolResult) -> dict[str, Any]:
        if not result or not hasattr(result, "content") or not result.content:
            return {"error": "No result from MCP server", "raw_result": str(result)}

        try:
            if not isinstance(result.content, list) or len(result.content) == 0:
                return {"error": "Invalid result format", "raw_result": str(result)}

            content_text: str = result.content[0].text
            if not isinstance(content_text, str):
                return {"error": "Invalid result format", "raw_result": str(result)}

            loan_value: float = float(content_text)

            return {"max_loan": loan_value}
        except (ValueError, TypeError, AttributeError):
            return {"error": "Failed to parse loan data", "raw_result": str(result)}
