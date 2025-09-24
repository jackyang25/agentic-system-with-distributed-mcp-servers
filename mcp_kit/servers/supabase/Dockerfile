# Dockerfile for Supabase MCP Server
FROM node:20


# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser
