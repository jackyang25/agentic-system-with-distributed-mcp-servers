"""Main entry point for the MCP client application."""

import asyncio
import os

from dotenv import load_dotenv
from fastmcp import Client

# Load environment variables
load_dotenv(dotenv_path="./.env")

# --- Required API keys ---
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
if not os.environ["OPENAI_API_KEY"]:
    raise ValueError("OPENAI_API_KEY is not set in .env")

# --- MCP configuration ---
os.environ["MCP_SERVER_NAME_NAME"] = os.getenv("MCP_SERVER_NAME_NAME", "")
os.environ["MCP_SERVER_NAME_PORT"] = os.getenv("MCP_SERVER_NAME_PORT", "")

if not os.environ["MCP_SERVER_NAME_NAME"]:
    raise ValueError("MCP_SERVER_NAME_NAME is not set in .env")
if not os.environ["MCP_SERVER_NAME_PORT"]:
    raise ValueError("MCP_SERVER_NAME_PORT is not set in .env")

# Dynamically build MCP URL
mcp_host = os.getenv("MCP_SERVER_NAME_NAME", "mcp_server_name")
mcp_port = os.getenv("MCP_SERVER_NAME_PORT", "5050")
mcp_url = f"http://{mcp_host}:{mcp_port}/mcp"

print("🔗 Connecting to:", mcp_url)

client = Client(mcp_url)

# --- LangSmith Monitoring (must be set before chains/agents are used) ---
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
if not os.environ["LANGSMITH_API_KEY"]:
    print(" LANGSMITH_API_KEY not set. Traces will not be uploaded.")

os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")
os.environ["LANGSMITH_PROJECT"] = os.getenv(
    "LANGSMITH_PROJECT", "civic-assistant-team-5"
)

print("✅ LangSmith monitoring enabled:", os.environ["LANGSMITH_PROJECT"])

# Import AFTER env setup to ensure LangSmith tracing applies globally
from mcp_servers.servers.server_name.client import get_mcp_data


async def main():
    """Run MCP client loop."""
    # Optionally pass MCP_URL into your client function if it accepts it
    await get_mcp_data()


if __name__ == "__main__":
    asyncio.run(main())
