# Dockerfile for Supabase MCP Server
FROM node:20


# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# No need to install - npx will download automatically

## Intentionally no CMD; container is kept idle by docker-compose and the
## MCP server is started via docker exec from the Python client.
