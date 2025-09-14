import asyncio
import os
from dotenv import load_dotenv
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

# Load environment variables from .env file
load_dotenv()

async def main():
    # set up how to start the MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y", 
            "@supabase/mcp-server-supabase@latest", 
            "--read-only",
            "--project-ref=" + os.getenv("SUPABASE_PROJECT_REF", "YOUR_PROJECT_REF")
        ],
        env={
            "SUPABASE_ACCESS_TOKEN": os.getenv("SUPABASE_ACCESS_TOKEN", "your-token")
        }
    )

    # start and connect
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_response = await session.list_tools()
            print("Available tools:", [tool.name for tool in tools_response.tools])

if __name__ == "__main__":
    asyncio.run(main())