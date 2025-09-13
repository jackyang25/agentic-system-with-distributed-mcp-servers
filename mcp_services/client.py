"""Create client to interact with MCP servers."""

import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from fastmcp import Client, FastMCP
from fastmcp.client.transports import StreamableHttpTransport
from langchain_openai import ChatOpenAI
from mcp.types import Resource, Tool

load_dotenv(dotenv_path="./creds.env")
os.environ["OPENAI_API_KEY"] = os.getenv(key="OPENAI_API_KEY")
os.environ["MCP_SERVER_NAME_NAME"] = os.getenv(key="MCP_SERVER_NAME_NAME")
os.environ["MCP_SERVER_NAME_PORT"] = os.getenv(key="MCP_SERVER_NAME_PORT")

if not os.environ["MCP_SERVER_NAME_NAME"]:
    raise ValueError("MCP_SERVER_NAME_NAME environment variable is not set.")
if not os.environ["MCP_SERVER_NAME_PORT"]:
    raise ValueError("MCP_SERVER_NAME_PORT environment variable is not set.")

mcp_server_name_name = os.environ["MCP_SERVER_NAME_NAME"]
mcp_server_name_port = os.environ["MCP_SERVER_NAME_PORT"]

llm: ChatOpenAI = ChatOpenAI(model="gpt-4.1-mini")

math_mcp: FastMCP[Any] = FastMCP(name="EnhancedMathServer")


client: Client[StreamableHttpTransport] = Client(
    transport=f"http://{mcp_server_name_name}:{mcp_server_name_port}/mcp"
)


async def get_mcp_data() -> None:
    async with client:
        tools: list[Tool] = await client.list_tools()
        resources: list[Resource] = await client.list_resources()
        for tool in tools:
            print(tool.name, tool.description, tool.title)
        print("-" * 20)
        for resource in resources:
            print(resource.name, resource.description)


asyncio.run(main=get_mcp_data())
