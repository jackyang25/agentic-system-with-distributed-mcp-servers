from .clients.supabase_client import SupabaseClient
from .clients.finance_client import FinanceClient

class adapter:

    def __init__(self):
        self.supabase = SupabaseClient()
        self.finance = FinanceClient()
        self.connected = {}

    async def connect_all(self):
        """Connect to all MCP services and report status"""        
        # Try supabase
        try:
            await self.supabase.connect()
            self.connected["supabase"] = "connected"
        except Exception as e:
            self.connected["supabase"] = f"failed: {e}"
        
        # Try finance
        try:
            await self.finance.connect()
            self.connected["finance"] = "connected"
        except Exception as e:
            self.connected["finance"] = f"failed: {e}"
        
        return self.connected

    async def check_running(self):
        """Check which services are available"""
        return self.connected
    
    async def get_available_tools(self):
        """Get all available tools from connected services"""
        tools = {}
        if self.connected.get("finance") == "connected":
            tools["finance"] = await self.finance.get_tools()
        if self.connected.get("supabase") == "connected":
            tools["supabase"] = await self.supabase.get_tools()
        return tools

    async def disconnect_all(self):
        """Clean shutdown of all services"""        
        # Try supabase
        try:
            await self.supabase.disconnect()
            self.connected["supabase"] = "disconnected"
        except Exception as e:
            pass
        
        # Try finance
        try:
            await self.finance.disconnect()
            self.connected["finance"] = "disconnected"
        except Exception as e:
            pass
        
        return self.connected