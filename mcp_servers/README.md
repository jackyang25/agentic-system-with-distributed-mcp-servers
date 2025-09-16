# MCP Servers

This directory contains MCP (Model Context Protocol) server configurations for MAREA.

## Structure

```
mcp_servers/
├── README.md          # This file
├── Dockerfile         # Supabase MCP server container
└── supabase/
    └── client.py      # Supabase MCP client wrapper
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
from mcp_servers.supabase.client import SupabaseClient

client = SupabaseClient("supabase-mcp-server")
await client.connect()
tools = await client.get_tools()
result = await client.query_properties(1)
```

### Communication Flow
```
MAREA Container → Docker Socket → Supabase MCP Container → Supabase API
```