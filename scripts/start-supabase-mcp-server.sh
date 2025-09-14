#!/bin/bash

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Start MCP server
npx @supabase/mcp-server-supabase --project-ref $SUPABASE_PROJECT_REF --read-only
