"""Main entry point for the MCP client application."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="./creds.env")

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
MCP_HOST = os.environ["MCP_SERVER_NAME_NAME"]
MCP_PORT = os.environ["MCP_SERVER_NAME_PORT"]
MCP_URL = f"http://{MCP_HOST}:{MCP_PORT}/mcp"
print(f"🔗 Using MCP server URL: {MCP_URL}")

# --- LangSmith Monitoring (must be set before chains/agents are used) ---
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
if not os.environ["LANGSMITH_API_KEY"]:
    print("⚠️  LANGSMITH_API_KEY not set. Traces will not be uploaded.")

os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "civic-assistant-team-5")

print("✅ LangSmith monitoring enabled:", os.environ["LANGSMITH_PROJECT"])

# Import AFTER env setup to ensure LangSmith tracing applies globally
from mcp_services.client import get_mcp_data


async def main():
    """Run MCP client loop."""
    # Optionally pass MCP_URL into your client function if it accepts it
    await get_mcp_data()


if __name__ == "__main__":
    asyncio.run(main())