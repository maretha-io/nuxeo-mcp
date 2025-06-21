FROM python:3.10-slim

WORKDIR /app

# Copy only the pyproject.toml file first to leverage Docker cache
COPY pyproject.toml .

# Copy the application
COPY . .

# Install the packaging module (required by nuxeo), uvicorn (for HTTP mode), and the package with its dependencies
RUN pip install --no-cache-dir packaging uvicorn && pip install --no-cache-dir -e .

# Expose the HTTP port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the server in HTTP mode
CMD ["python", "-m", "nuxeo_mcp", "--http", "--port", "8080"]
