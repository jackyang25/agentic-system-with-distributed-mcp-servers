# Dockerfile for Finance MCP Server
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install FastMCP
RUN pip install fastmcp

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Default command - keep container running
CMD ["tail", "-f", "/dev/null"]
