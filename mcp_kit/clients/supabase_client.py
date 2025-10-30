import asyncio
import json
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

load_dotenv()


class SupabaseClient:
    def __init__(self, container_name: str = "supabase-mcp-server") -> None:
        self.container_name: str = container_name
        self.server_params: StdioServerParameters = StdioServerParameters(
            command="docker",
            args=[
                "exec",
                "-i",
                container_name,
                "npx",
                "@supabase/mcp-server-supabase@latest",
                "--read-only",
                "--project-ref="
                + os.getenv("SUPABASE_PROJECT_REF", "YOUR_PROJECT_REF"),
                "--access-token=" + os.getenv("SUPABASE_ACCESS_TOKEN", "your-token"),
            ],
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
        logger.info("Connected to Supabase MCP server")

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
        logger.info("Disconnected from Supabase MCP server")

    async def get_tools(self) -> list[str]:
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")
        tools_response: ListToolsResult = await self.session.list_tools()
        return [tool.name for tool in tools_response.tools]

    async def query_home_by_id(self, home_id: str) -> dict[str, Any]:
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")

        query: str = (
            f'SELECT * FROM public.nyc_property_sales WHERE "HOME_ID" = {home_id};'
        )

        result: CallToolResult = await self.session.call_tool(
            name="execute_sql", arguments={"query": query}
        )

        return self._parse_property_data(result=result)

    async def query_price_data_by_zip_and_units(
        self, zip_code: str, residential_units: int
    ) -> dict[str, Any]:
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")

        query: str = f"""
        SELECT 
            AVG(CAST("SALE PRICE" AS NUMERIC)) as average_sale_price,
            MIN(CAST("SALE PRICE" AS NUMERIC)) as min_sale_price,
            MAX(CAST("SALE PRICE" AS NUMERIC)) as max_sale_price,
            COUNT(*) as total_properties,
            "ZIP CODE" as zip_code,
            "RESIDENTIAL UNITS" as residential_units
        FROM public.nyc_property_sales 
        WHERE "ZIP CODE" = '{zip_code}' 
        AND CAST("RESIDENTIAL UNITS" AS INTEGER) = {residential_units}
        AND "SALE PRICE" ~ '^[0-9]+$'
        GROUP BY "ZIP CODE", "RESIDENTIAL UNITS";
        """

        result: CallToolResult = await self.session.call_tool(
            name="execute_sql", arguments={"query": query}
        )

        return self._parse_price_data(result=result)

    async def search_programs_rag(self, embedding, limit=10) -> dict[str, Any]:
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")

        embedding_str: str = json.dumps(embedding)

        query_sql: str = f"""
        SELECT 
            program_name,
            formatted_text,
            jurisdiction,
            assistance_type,
            max_benefit,
            eligibility,
            source,
            embedding_vector <-> '{embedding_str}' as distance
        FROM public.nyc_programs_rag 
        ORDER BY embedding_vector <-> '{embedding_str}'
        LIMIT {limit};
        """

        result: CallToolResult = await self.session.call_tool(
            name="execute_sql", arguments={"query": query_sql}
        )

        return self._parse_programs_rag_results(result=result)

    def _parse_programs_rag_results(self, result: CallToolResult) -> dict[str, Any]:
        """Parse MCP result and return clean program search data"""
        if not result or not hasattr(result, "content") or not result.content:
            return {"error": "No results found"}

        try:
            if not isinstance(result.content, list) or len(result.content) == 0:
                return {"error": "No results found"}

            content_text: str = result.content[0].text
            if not isinstance(content_text, str):
                return {"error": "Invalid response format"}

            start_marker: str = "<untrusted-data-"
            end_marker: str = "</untrusted-data-"
            start_idx: int = content_text.find(start_marker)
            end_idx: int = content_text.find(end_marker)

            if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
                return {"error": "No data found in response"}

            json_start: int = content_text.find("[", start_idx)
            json_end: int = content_text.find("]", json_start)

            if json_start == -1 or json_end == -1 or json_start >= json_end:
                return {"error": "No JSON data found"}

            json_str: str = content_text[json_start : json_end + 1]
            json_str: str = json_str.replace('\\"', '"')
            raw_programs: Any = json.loads(json_str)

            if not isinstance(raw_programs, list):
                return {"error": "Invalid data format"}

            programs: list[Any] = []
            for i, program in enumerate(raw_programs):
                if isinstance(program, dict):
                    programs.append(
                        {
                            "rank": i + 1,
                            "program_name": program.get("program_name", ""),
                            "formatted_text": program.get("formatted_text", ""),
                            "jurisdiction": program.get("jurisdiction", ""),
                            "assistance_type": program.get("assistance_type", ""),
                            "max_benefit": program.get("max_benefit", ""),
                            "eligibility": program.get("eligibility", ""),
                            "source": program.get("source", ""),
                            "similarity_score": 1 - float(program.get("distance", 1)),
                        }
                    )

            return {"programs": programs, "total_found": len(programs)}

        except (
            json.JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
            AttributeError,
        ) as e:
            logger.info(f"DEBUG: Program RAG search parsing failed with error: {e}")
            logger.info(f"DEBUG: Content text: {content_text[:200]}...")
            return {"error": f"Failed to parse results: {str(e)}"}

    def _parse_property_data(self, result: CallToolResult) -> Any:
        if not result or not hasattr(result, "content") or not result.content:
            return result

        try:
            if not isinstance(result.content, list) or len(result.content) == 0:
                return result

            content_text: str = result.content[0].text
            if not isinstance(content_text, str):
                return result

            start_marker: str = "<untrusted-data-"
            end_marker: str = "</untrusted-data-"
            start_idx: int = content_text.find(start_marker)
            end_idx: int = content_text.find(end_marker)

            if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
                return result

            json_start: int = content_text.find("[", start_idx)
            json_end: int = content_text.find("]", json_start)

            if json_start == -1 or json_end == -1 or json_start >= json_end:
                return result

            json_str: str = content_text[json_start : json_end + 1]
            json_str: str = json_str.replace('\\"', '"')
            property_list: Any = json.loads(json_str)

            if not isinstance(property_list, list) or len(property_list) == 0:
                return result

            property_data: Any = property_list[0]
            if not isinstance(property_data, dict):
                return result

            return {
                "home_id": property_data.get("HOME_ID"),
                "address": property_data.get("ADDRESS"),
                "neighborhood": property_data.get("NEIGHBORHOOD"),
                "sale_price": property_data.get("SALE PRICE"),
                "zip_code": property_data.get("ZIP CODE"),
                "year_built": property_data.get("YEAR BUILT"),
            }
        except (
            json.JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
            AttributeError,
        ) as e:
            logger.info(f"DEBUG: Parsing failed with error: {e}")
            logger.info(f"DEBUG: Content text: {content_text[:200]}...")
            return result

    def _parse_price_data(self, result) -> Any:
        if not result or not hasattr(result, "content") or not result.content:
            return result

        try:
            if not isinstance(result.content, list) or len(result.content) == 0:
                return result

            content_text: str = result.content[0].text
            if not isinstance(content_text, str):
                return result

            start_marker: str = "<untrusted-data-"
            end_marker: str = "</untrusted-data-"
            start_idx: int = content_text.find(start_marker)
            end_idx: int = content_text.find(end_marker)

            if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
                return result

            json_start: int = content_text.find("[", start_idx)
            json_end: int = content_text.find("]", json_start)

            if json_start == -1 or json_end == -1 or json_start >= json_end:
                return result

            json_str: str = content_text[json_start : json_end + 1]
            json_str: str = json_str.replace('\\"', '"')
            data_list: Any = json.loads(json_str)

            if not isinstance(data_list, list) or len(data_list) == 0:
                return {"error": "No data found for the specified criteria"}

            data: Any = data_list[0]
            if not isinstance(data, dict):
                return {"error": "Invalid data format"}

            return {
                "zip_code": data.get("zip_code"),
                "residential_units": data.get("residential_units"),
                "average_sale_price": round(
                    number=float(data.get("average_sale_price", 0)), ndigits=2
                )
                if data.get("average_sale_price")
                else 0,
                "min_sale_price": round(
                    number=float(data.get("min_sale_price", 0)), ndigits=2
                )
                if data.get("min_sale_price")
                else 0,
                "max_sale_price": round(
                    number=float(data.get("max_sale_price", 0)), ndigits=2
                )
                if data.get("max_sale_price")
                else 0,
                "total_properties": data.get("total_properties", 0),
            }
        except (
            json.JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
            AttributeError,
        ) as e:
            logger.info(f"DEBUG: Average price parsing failed with error: {e}")
            logger.info(f"DEBUG: Content text: {content_text[:200]}...")
            return result
