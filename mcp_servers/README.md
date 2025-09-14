# Supabase MCP Server

## Quick Start

### 1. Install Dependencies
```bash
npm install -g @supabase/mcp-server-supabase
```

### 2. Set Up Environment
1. Copy `config/database.env.example` to `config/database.env`
2. Update with your Supabase credentials:
   - Get your Personal Access Token from [Supabase Dashboard](https://supabase.com/dashboard/account/tokens)
   - Replace `your_personal_access_token_here` with your actual token

### 3. Start the MCP Server
```bash
../scripts/start-supabase-mcp-server.sh
```

The server will start and wait for AI agent connections.

## What This Provides

The Supabase MCP Server provides access to:
- Database queries (`execute_sql`, `list_tables`)
- Project management (`get_project`, `list_projects`)
- Edge Functions (`list_edge_functions`, `deploy_edge_function`)
- Storage management (`list_storage_buckets`)

## Testing

Run tests to verify everything is working:

```bash
# Run all tests
../scripts/run-tests.sh

# Or run tests directly
python3 -m pytest ../tests/test_mcp_setup.py -v
```

## Troubleshooting

- Make sure `config/database.env` exists and has valid credentials
- Ensure Node.js is installed (`node -v`)
- Check that the MCP server is running before connecting AI agents
- Run tests to diagnose issues: `../scripts/run-tests.sh`
