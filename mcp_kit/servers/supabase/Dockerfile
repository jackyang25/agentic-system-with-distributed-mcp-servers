# Dockerfile for Supabase MCP Server
FROM node:20


# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# No need to install - npx will download automatically

# Default command - start the MCP server
# Environment variables will be passed from docker-compose
CMD ["npx", "@supabase/mcp-server-supabase", "--read-only", "--project-ref=${SUPABASE_PROJECT_REF}", "--access-token=${SUPABASE_ACCESS_TOKEN}"]
