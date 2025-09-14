# MCP Server Setup

Simple Supabase MCP server with tests and Docker.

## Quick Start

1. **Install dependencies:**
   ```bash
   make install
   ```

2. **Set up environment:**
   ```bash
   cp docker.env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Run tests:**
   ```bash
   make test
   ```

4. **Start MCP server:**
   ```bash
   ./scripts/start-supabase-mcp-server.sh
   ```

5. **Or use Docker:**
   ```bash
   docker-compose up
   ```

## What This Provides

MCP server gives agents access to:
- Database queries (`execute_sql`, `list_tables`)
- Project management (`get_project`, `list_projects`)
- Storage management (`list_storage_buckets`)

## Agent Usage

```python
import mcp
client = mcp.Client("http://localhost:3001")
data = client.call("execute_sql", query="SELECT * FROM properties")
```
