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
    
    async def query_price_data_by_zip_and_units(self, zip_code: str, residential_units: int):
        """Query comprehensive price data by zip code and residential units"""
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")
        
        query = f"""
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
            
        result = await self.session.call_tool("execute_sql", {
            "query": query
        })
        
        # Parse and return clean data
        return self._parse_price_data(result)

    async def search_programs_rag(self, embedding, limit=10):
        """Search government programs using vector similarity search with RAG"""
        if not self.session:
            raise RuntimeError("Not connected. Call connect() first.")
        
        import json
        
        # Convert embedding to JSON string for SQL query
        embedding_str = json.dumps(embedding)
        
        # Query the nyc_programs_rag table using vector similarity
        query_sql = f"""
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
        
        # Execute the query
        result = await self.session.call_tool("execute_sql", {
            "query": query_sql
        })
        
        # Parse and return clean data
        return self._parse_programs_rag_results(result)

    def _parse_programs_rag_results(self, result):
        """Parse MCP result and return clean program search data"""
        if not result or not hasattr(result, 'content') or not result.content:
            return {"error": "No results found"}
            
        import json
        try:
            # The result.content is a list of TextContent objects
            if not isinstance(result.content, list) or len(result.content) == 0:
                return {"error": "No results found"}
                
            content_text = result.content[0].text
            if not isinstance(content_text, str):
                return {"error": "Invalid response format"}
                
            # Extract the JSON part between the boundaries
            start_marker = '<untrusted-data-'
            end_marker = '</untrusted-data-'
            start_idx = content_text.find(start_marker)
            end_idx = content_text.find(end_marker)
            
            if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
                return {"error": "No data found in response"}
                
            # Find the JSON array within the boundaries
            json_start = content_text.find('[', start_idx)
            json_end = content_text.find(']', json_start)
            
            if json_start == -1 or json_end == -1 or json_start >= json_end:
                return {"error": "No JSON data found"}
                
            json_str = content_text[json_start:json_end + 1]
            # Unescape the JSON string to handle escaped quotes
            json_str = json_str.replace('\\"', '"')
            raw_programs = json.loads(json_str)
            
            if not isinstance(raw_programs, list):
                return {"error": "Invalid data format"}
            
            # Format results with rank as key
            programs = []
            for i, program in enumerate(raw_programs):
                if isinstance(program, dict):
                    programs.append({
                        "rank": i + 1,
                        "program_name": program.get("program_name", ""),
                        "formatted_text": program.get("formatted_text", ""),
                        "jurisdiction": program.get("jurisdiction", ""),
                        "assistance_type": program.get("assistance_type", ""),
                        "max_benefit": program.get("max_benefit", ""),
                        "eligibility": program.get("eligibility", ""),
                        "source": program.get("source", ""),
                        "similarity_score": 1 - float(program.get("distance", 1))  # Convert distance to similarity
                    })
            
            return {
                "programs": programs,
                "total_found": len(programs)
            }
            
        except (json.JSONDecodeError, KeyError, IndexError, TypeError, AttributeError) as e:
            print(f"DEBUG: Program RAG search parsing failed with error: {e}")
            print(f"DEBUG: Content text: {content_text[:200]}...")
            return {"error": f"Failed to parse results: {str(e)}"}

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

    def _parse_price_data(self, result):
        """Parse MCP result and return clean price data"""
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
            data_list = json.loads(json_str)
            
            if not isinstance(data_list, list) or len(data_list) == 0:
                return {"error": "No data found for the specified criteria"}
                
            data = data_list[0]
            if not isinstance(data, dict):
                return {"error": "Invalid data format"}
                    
            # Return comprehensive price data
            return {
                "zip_code": data.get("zip_code"),
                "residential_units": data.get("residential_units"),
                "average_sale_price": round(float(data.get("average_sale_price", 0)), 2) if data.get("average_sale_price") else 0,
                "min_sale_price": round(float(data.get("min_sale_price", 0)), 2) if data.get("min_sale_price") else 0,
                "max_sale_price": round(float(data.get("max_sale_price", 0)), 2) if data.get("max_sale_price") else 0,
                "total_properties": data.get("total_properties", 0)
            }
        except (json.JSONDecodeError, KeyError, IndexError, TypeError, AttributeError) as e:
            # Debug: print the error to see what's happening
            print(f"DEBUG: Average price parsing failed with error: {e}")
            print(f"DEBUG: Content text: {content_text[:200]}...")
            # If anything goes wrong, return original result
            return result


