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

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8181/health || exit 1

# Run the server in HTTP mode
#CMD ["python", "-m", "nuxeo_mcp", "--http", "--port", "8181"]
CMD ["python", "-m", "nuxeo_mcp", "--sse", "--port", "8181"]
