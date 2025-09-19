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
    
    async def query_home_by_id(self, home_id): # Wrappers are for parameter validation, error handling, and domain interface
        """Query NYC property sales data by HOME_ID"""
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")
        
        query = f"SELECT * FROM public.nyc_property_sales WHERE \"HOME_ID\" = {home_id};"
            
        result = await self.session.call_tool("execute_sql", {
            "query": query
        })
        
        # Parse and return clean data
        return self._parse_property_data(result)
    
    def _parse_property_data(self, result):
        """Parse MCP result and return clean property data"""
        if not result or not hasattr(result, 'content') or not result.content:
            return result
            
        import json
        try:
            # The result.content is a list of TextContent objects
            if not isinstance(result.content, list) or len(result.content) == 0:
                return result
                
            content_text = result.content[0].text
            if not isinstance(content_text, str):
                return result
                
            # Extract the JSON part between the boundaries
            start_marker = '<untrusted-data-'
            end_marker = '</untrusted-data-'
            start_idx = content_text.find(start_marker)
            end_idx = content_text.find(end_marker)
            
            if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
                return result
                
            # Find the JSON array within the boundaries
            json_start = content_text.find('[', start_idx)
            json_end = content_text.find(']', json_start)
            
            if json_start == -1 or json_end == -1 or json_start >= json_end:
                return result
                
            json_str = content_text[json_start:json_end + 1]
            # Unescape the JSON string to handle escaped quotes
            json_str = json_str.replace('\\"', '"')
            property_list = json.loads(json_str)
            
            if not isinstance(property_list, list) or len(property_list) == 0:
                return result
                
            property_data = property_list[0]
            if not isinstance(property_data, dict):
                return result
                    
            # Return only key fields for LLM analysis
            return {
                "home_id": property_data.get("HOME_ID"),
                "address": property_data.get("ADDRESS"),
                "neighborhood": property_data.get("NEIGHBORHOOD"),
                "sale_price": property_data.get("SALE PRICE"),
                "zip_code": property_data.get("ZIP CODE"),
                "year_built": property_data.get("YEAR BUILT")
            }
        except (json.JSONDecodeError, KeyError, IndexError, TypeError, AttributeError) as e:
            # Debug: print the error to see what's happening
            print(f"DEBUG: Parsing failed with error: {e}")
            print(f"DEBUG: Content text: {content_text[:200]}...")
            # If anything goes wrong, return original result
            return result


