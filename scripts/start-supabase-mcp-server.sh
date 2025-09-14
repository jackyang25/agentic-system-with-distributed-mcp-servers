#!/bin/bash

# Civic Assistant Team 5 - Supabase MCP Server Startup Script
echo "Supabase MCP Server"
echo "============================================="

# Check if config/database.env exists
if [ ! -f "config/database.env" ]; then
    echo "Error: config/database.env file not found!"
    echo "   Please create config/database.env with your Supabase credentials"
    echo "   You can copy from config/database.env.example"
    exit 1
fi

# Load environment variables from config/database.env
export $(grep -v '^#' config/database.env | xargs)

# Check if required variables are set
if [ -z "$SUPABASE_ACCESS_TOKEN" ] || [ "$SUPABASE_ACCESS_TOKEN" = "your_personal_access_token_here" ]; then
    echo "Error: SUPABASE_ACCESS_TOKEN not set!"
    echo "   Please update database.env with your actual Supabase Personal Access Token"
    exit 1
fi

if [ -z "$SUPABASE_PROJECT_REF" ]; then
    echo "Error: SUPABASE_PROJECT_REF not set!"
    exit 1
fi

# Start the Supabase MCP Server
echo "Starting Supabase MCP Server..."
echo "   Project: $SUPABASE_PROJECT_REF"
echo "   Server will run until you press Ctrl+C"
echo "   Connect your AI agent to this server"
echo ""

npx @supabase/mcp-server-supabase --project-ref $SUPABASE_PROJECT_REF --read-only
