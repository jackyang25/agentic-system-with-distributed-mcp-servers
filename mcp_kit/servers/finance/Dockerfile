FROM python:3.12-slim

WORKDIR /app

RUN pip install fastmcp

COPY utils/ ./utils/
COPY mcp_kit/servers/finance/ .
COPY .env .

RUN useradd -m mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

CMD ["tail", "-f", "/dev/null"]
