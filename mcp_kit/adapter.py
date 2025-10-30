from typing import Any
from mcp_kit.clients.finance_client import FinanceClient
from mcp_kit.clients.location_client import LocationClient
from mcp_kit.clients.supabase_client import SupabaseClient


class Adapter:
    def __init__(self) -> None:
        self.supabase = SupabaseClient()
        self.finance = FinanceClient()
        self.location = LocationClient()
        self.connected: dict[str, Any] = {}

    async def connect_all(self) -> dict[str, Any]:
        try:
            await self.supabase.connect()
            self.connected["supabase"] = "connected"
        except Exception as e:
            self.connected["supabase"] = f"failed: {e}"

        try:
            await self.finance.connect()
            self.connected["finance"] = "connected"
        except Exception as e:
            self.connected["finance"] = f"failed: {e}"

        try:
            await self.location.connect()
            self.connected["location"] = "connected"
        except Exception as e:
            self.connected["location"] = f"failed: {e}"

        return self.connected

    async def check_running(self) -> dict[str, Any]:
        return self.connected

    async def get_available_tools(self) -> dict[str, Any]:
        tools: dict[str, Any] = {}
        if self.connected.get("finance") == "connected":
            tools["finance"] = await self.finance.get_tools()
        if self.connected.get("supabase") == "connected":
            tools["supabase"] = await self.supabase.get_tools()
        if self.connected.get("location") == "connected":
            tools["location"] = await self.location.get_tools()
        return tools

    async def disconnect_all(self) -> dict[str, Any]:
        try:
            await self.supabase.disconnect()
            self.connected["supabase"] = "disconnected"
        except Exception:
            pass

        try:
            await self.finance.disconnect()
            self.connected["finance"] = "disconnected"
        except Exception:
            pass

        try:
            await self.location.disconnect()
            self.connected["location"] = "disconnected"
        except Exception:
            pass

        return self.connected
