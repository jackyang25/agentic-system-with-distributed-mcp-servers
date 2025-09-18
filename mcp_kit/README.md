# MCP Integration

This directory contains MCP (Model Context Protocol) integration components for MAREA.

## Structure

```
mcp_kit/
├── README.md          # This file
├── adapter.py         # MCP adapter for connecting to servers
├── tools.py           # MCP tools and utilities
├── servers/           # MCP server implementations
│   ├── finance/       # Finance MCP server
│   └── supabase/      # Supabase MCP server
└── clients/           # MCP client implementations
    ├── finance_client.py
    └── supabase_client.py
```

## Supabase MCP Server

The Supabase MCP server provides database access through the MCP protocol.

### Configuration
- **Container**: `supabase-mcp-server`
- **Base Image**: `node:20`
- **Package**: `@supabase/mcp-server-supabase@latest`

### Environment Variables
- `SUPABASE_PROJECT_REF`: Your Supabase project reference
- `SUPABASE_ACCESS_TOKEN`: Your Supabase access token

### Available Tools
- `execute_sql` - Execute SQL queries
- `list_tables` - List database tables
- `search_docs` - Search documentation
- `get_project_url` - Get project URL
- And 15+ more tools for database management

### Usage
The MCP server runs in a separate container and communicates with MAREA via Docker exec and stdin/stdout pipes.

```python
from mcp_kit.clients.supabase_client import SupabaseClient

client = SupabaseClient("supabase-mcp-server")
await client.connect()
tools = await client.get_tools()
result = await client.query_properties(1)
```

### Communication Flow
```
MAREA Container → Docker Socket → Supabase MCP Container → Supabase API
```