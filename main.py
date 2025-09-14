"""Main entry point for the MCP client application."""

import asyncio
import os

from dotenv import load_dotenv

from mcp_services.client import get_mcp_data

load_dotenv(dotenv_path="./creds.env")
os.environ["OPENAI_API_KEY"] = os.getenv(key="OPENAI_API_KEY")
os.environ["MCP_SERVER_NAME_NAME"] = os.getenv(key="MCP_SERVER_NAME_NAME")
os.environ["MCP_SERVER_NAME_PORT"] = os.getenv(key="MCP_SERVER_NAME_PORT")

if not os.environ["MCP_SERVER_NAME_NAME"]:
    raise ValueError("MCP_SERVER_NAME_NAME environment variable is not set.")
if not os.environ["MCP_SERVER_NAME_PORT"]:
    raise ValueError("MCP_SERVER_NAME_PORT environment variable is not set.")


async def main():
    await get_mcp_data()


asyncio.run(main())
