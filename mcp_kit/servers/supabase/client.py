import os
import asyncio
from dotenv import load_dotenv
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

# Load environment variables from .env file
load_dotenv()

class SupabaseClient:
    def __init__(self, container_name="supabase-mcp-server"):
        self.container_name = container_name
        self.server_params = StdioServerParameters(
            command="docker",
            args=[
                "exec", "-i", container_name,
                "npx", 
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
        if self.session:
            return
            
        self._stdio_context = stdio_client(self.server_params)
        read_stream, write_stream = await self._stdio_context.__aenter__()
        
        self._session_context = ClientSession(read_stream, write_stream)
        self.session = await self._session_context.__aenter__()
        
        await self.session.initialize()
        print("Connected to Supabase MCP server")
    
    async def disconnect(self):
        """Close the persistent connection"""
        if not self.session:
            return
            
        try:
            if self._session_context:
                await self._session_context.__aexit__(None, None, None)
        except (Exception, asyncio.CancelledError):
            pass  # Ignore cleanup errors
            
        try:
            if self._stdio_context:
                await self._stdio_context.__aexit__(None, None, None)
        except (Exception, asyncio.CancelledError):
            pass  # Ignore cleanup errors
            
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
    
    async def query_properties(self, limit=1): # Wrappers are for parameter validation, error handling, and domain interface
        """Query NYC property sales data"""
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")
        result = await self.session.call_tool("execute_sql", {
            "query": f"SELECT * FROM public.nyc_property_sales LIMIT {limit};"
        })
        return result


