# Civic Assistant Team 5

Simple MCP client setup for connecting to Supabase database.

## Quick Start

1. **Install dependencies:**
   ```bash
   make install
   ```

2. **Set up environment:**
   - You already have a `.env` file with your Supabase credentials
   - Contains: `SUPABASE_ACCESS_TOKEN` and `SUPABASE_PROJECT_REF`

3. **Test MCP connection:**
   ```bash
   python mcp_servers/supabase_mcp/client.py
   ```

4. **Start main application:**
   ```bash
   python main.py
   ```

## What This Provides

**MCP Client** connects to Supabase and provides access to:
- Database queries (`execute_sql`, `list_tables`)
- Documentation search (`search_docs`)
- Project management (`get_project_url`, `get_anon_key`)
- Edge functions (`list_edge_functions`, `deploy_edge_function`)
- Database branching (`create_branch`, `merge_branch`)

## How It Works

1. **MCP Client** (`client.py`) connects to Supabase MCP server via npx
2. **Uses your .env credentials** to authenticate
3. **No global installs needed** - npx handles downloads automatically
4. **20+ tools available** for database and project management

## Files Structure

- `main.py` - Main application entry point
- `mcp_servers/supabase_mcp/client.py` - MCP connection test
- `.env` - Your Supabase credentials (already configured)
- `requirements.txt` - Python dependencies
