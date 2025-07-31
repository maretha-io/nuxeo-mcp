FROM python:3.10-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy only the pyproject.toml file first to leverage Docker cache
COPY pyproject.toml .

# Copy the application
COPY . .

# Install the packaging module (required by nuxeo), uvicorn (for HTTP mode), and the package with its dependencies
RUN pip install --no-cache-dir packaging uvicorn && pip install --no-cache-dir -e .

# Expose the HTTP port
EXPOSE 8181

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MCP_MODE=http
ENV MCP_PORT=8181
ENV MCP_HOST=0.0.0.0

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${MCP_PORT}/health || exit 1

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Default values\n\
MODE=${MCP_MODE:-http}\n\
PORT=${MCP_PORT:-8181}\n\
HOST=${MCP_HOST:-0.0.0.0}\n\
\n\
# Start the server based on the mode\n\
if [ "$MODE" = "http" ]; then\n\
    echo "starting MCP in http mode"\n\
    exec python -m nuxeo_mcp --http --port "$PORT" --host "$HOST"\n\
elif [ "$MODE" = "sse" ]; then\n\
    echo "starting MCP in sse mode"\n\
    exec python -m nuxeo_mcp --sse --port "$PORT" --host "$HOST"\n\
else\n\
    echo "Invalid MCP_MODE: $MODE. Use either '\''http'\'' or '\''sse'\''."\n\
    exit 1\n\
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
