# Dockerfile for Location MCP Server
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
RUN pip install fastmcp httpx

# Copy application code
COPY utils/ ./utils/
COPY mcp_kit/servers/location/ .
COPY .env .

# Create non-root user for security
RUN useradd -m mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Default command - keep container running
CMD ["tail", "-f", "/dev/null"]
