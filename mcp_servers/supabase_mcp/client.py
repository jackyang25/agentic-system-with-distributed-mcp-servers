import asyncio
import os
from dotenv import load_dotenv
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

# Load environment variables from .env file
load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.server_params = StdioServerParameters(
            command="npx",
            args=[
                "-y", 
                "@supabase/mcp-server-supabase@latest", 
                "--read-only",
                "--project-ref=" + os.getenv("SUPABASE_PROJECT_REF", "YOUR_PROJECT_REF"),
                "--access-token=" + os.getenv("SUPABASE_ACCESS_TOKEN", "your-token")
            ]
        )
        self.session = None
        self._stdio_context = None
        self._session_context = None
    
    async def connect(self):
        """Establish persistent connection to Supabase MCP server"""
        # Start the stdio client context manager
        self._stdio_context = stdio_client(self.server_params)
        read_stream, write_stream = await self._stdio_context.__aenter__()
        
        # Start the client session context manager
        self._session_context = ClientSession(read_stream, write_stream)
        self.session = await self._session_context.__aenter__()
        
        # Initialize the session
        await self.session.initialize()
        print("Connected to Supabase MCP server")
    
    async def disconnect(self):
        """Close the persistent connection"""
        try:
            if self._session_context:
                await self._session_context.__aexit__(None, None, None)
            if self._stdio_context:
                await self._stdio_context.__aexit__(None, None, None)
        finally:
            self.session = None
            self._session_context = None
            self._stdio_context = None
            print("Disconnected from Supabase MCP server")
    
    async def get_tools(self):
        """Get available tools"""
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")
        tools_response = await self.session.list_tools()
        return [tool.name for tool in tools_response.tools]
    
    async def query_properties(self, limit=1):
        """Query NYC property sales data"""
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")
        result = await self.session.call_tool("execute_sql", {
            "query": f"SELECT * FROM public.nyc_property_sales LIMIT {limit};"
        })
        return result

if __name__ == "__main__":
    async def test():
        client = SupabaseClient()
        
        try:
            print("Connecting to Supabase MCP server...")
            await client.connect()
            print("--------------------------------")
            
            print("Getting available tools...")
            tools = await client.get_tools()
            print("Available tools:", tools)
            print("--------------------------------")
            
            print("Querying properties...")
            result = await client.query_properties(1)
            print("Query completed successfully!")
            
            # Can do multiple operations with same session
            print("Querying more properties...")
            result2 = await client.query_properties(2)
            print("Second query completed!")
            print("--------------------------------")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await client.disconnect()
    
    asyncio.run(test())