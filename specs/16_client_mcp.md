# MCP Client and Docker Integration

This specification outlines the creation of a Python CLI client for the Nuxeo MCP Server, a Dockerfile for the MCP Server, and a GitHub Action workflow for integration testing.

## Python CLI Client

### Overview

The Python CLI client will connect to the MCP server using HTTP and invoke tools like search and get_document. This client will be used for integration testing in GitHub Actions.

### Features

- Connect to the MCP server via HTTP
- Call the search tool
- Call the get_document tool
- Format and display results

### Implementation Details

The client will be implemented as a Python script that uses the `requests` library to make HTTP requests to the MCP server. It will provide a command-line interface for invoking the MCP tools.

```python
#!/usr/bin/env python3
"""
Nuxeo MCP Client

A command-line client for interacting with the Nuxeo MCP Server using the FastMCP client library.
"""

import argparse
import asyncio
import json
import sys
from typing import Dict, Any, Optional

from fastmcp import Client


async def search(url: str, query: str, page_size: int = 20, page_index: int = 0) -> Dict[str, Any]:
    """
    Search for documents using the search tool.
    
    Args:
        url: The URL of the MCP server
        query: The NXQL query to execute
        page_size: Number of results per page
        page_index: Page index
        
    Returns:
        The search results
    """
    client = Client(url)
    
    async with client:
        result = await client.call_tool("search", {
            "query": query,
            "pageSize": page_size,
            "currentPageIndex": page_index
        })
        
        # The result might be a list of content objects, extract the text content
        if isinstance(result, list) and len(result) > 0 and hasattr(result[0], 'text'):
            return json.loads(result[0].text)
        return result


async def get_document(url: str, path: Optional[str] = None, uid: Optional[str] = None, 
                      fetch_blob: bool = False, conversion_format: Optional[str] = None, 
                      rendition: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a document by path or ID.
    
    Args:
        url: The URL of the MCP server
        path: The path of the document
        uid: The UID of the document
        fetch_blob: Whether to fetch the document's blob
        conversion_format: Format to convert the document to
        rendition: Rendition to fetch
        
    Returns:
        The document
    """
    if not path and not uid:
        raise ValueError("Either path or uid must be provided")
    
    arguments = {}
    if path:
        arguments["path"] = path
    if uid:
        arguments["uid"] = uid
    if fetch_blob:
        arguments["fetch_blob"] = fetch_blob
    if conversion_format:
        arguments["conversion_format"] = conversion_format
    if rendition:
        arguments["rendition"] = rendition
    
    client = Client(url)
    
    async with client:
        result = await client.call_tool("get_document", arguments)
        
        # The result might be a list of content objects, extract the text content
        if isinstance(result, list) and len(result) > 0 and hasattr(result[0], 'text'):
            return json.loads(result[0].text)
        return result


def main():
    parser = argparse.ArgumentParser(description="Nuxeo MCP Client")
    parser.add_argument("--url", default="http://localhost:8080", help="URL of the MCP server")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for documents")
    search_parser.add_argument("query", help="NXQL query")
    search_parser.add_argument("--page-size", type=int, default=20, help="Number of results per page")
    search_parser.add_argument("--page-index", type=int, default=0, help="Page index")
    
    # Get document command
    get_doc_parser = subparsers.add_parser("get-document", help="Get a document")
    get_doc_parser.add_argument("--path", help="Path of the document")
    get_doc_parser.add_argument("--uid", help="UID of the document")
    get_doc_parser.add_argument("--fetch-blob", action="store_true", help="Fetch the document's blob")
    get_doc_parser.add_argument("--conversion-format", help="Format to convert the document to")
    get_doc_parser.add_argument("--rendition", help="Rendition to fetch")
    
    args = parser.parse_args()
    
    if args.command == "search":
        result = asyncio.run(search(args.url, args.query, args.page_size, args.page_index))
        print(json.dumps(result, indent=2))
    elif args.command == "get-document":
        result = asyncio.run(get_document(args.url, args.path, args.uid, args.fetch_blob, 
                                        args.conversion_format, args.rendition))
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Dockerfile for MCP Server

### Overview

The Dockerfile will create an image for the Nuxeo MCP Server that can run in HTTP mode.

### Implementation Details

```dockerfile
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
```

## Docker Compose Configuration

### Overview

The Docker Compose configuration will define services for both the Nuxeo Server and the MCP Server.

### Implementation Details

```yaml
version: '3'

services:
  nuxeo:
    image: docker-private.packages.nuxeo.com/nuxeo/nuxeo:2025
    environment:
      - NUXEO_DEV_MODE=true
    ports:
      - "8080:8080"
    networks:
      - mcp-network

  mcp:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - NUXEO_URL=http://nuxeo:8080/nuxeo
      - NUXEO_USERNAME=Administrator
      - NUXEO_PASSWORD=Administrator
    ports:
      - "8081:8080"
    depends_on:
      - nuxeo
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
```

## GitHub Action Workflow

### Overview

The GitHub Action workflow will use Docker Compose to start the MCP Server and Nuxeo Server, and use the client to test the search tool.

### Implementation Details

```yaml
name: Docker Integration Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  docker-integration-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests fastmcp
        
    - name: Login to Nuxeo Docker Registry
      uses: docker/login-action@v2
      with:
        registry: docker-private.packages.nuxeo.com
        username: ${{ secrets.NUXEO_DOCKER_USERNAME }}
        password: ${{ secrets.NUXEO_DOCKER_PASSWORD }}
        
    - name: Start services with Docker Compose
      run: |
        docker compose up -d
        
    - name: Wait for Nuxeo to start
      run: |
        echo "Waiting for Nuxeo to start..."
        timeout=300
        start_time=$(date +%s)
        while ! curl -s http://localhost:8080/nuxeo/runningstatus > /dev/null; do
          current_time=$(date +%s)
          elapsed=$((current_time - start_time))
          if [ $elapsed -gt $timeout ]; then
            echo "Timeout waiting for Nuxeo to start"
            exit 1
          fi
          echo "Waiting for Nuxeo to start... ($elapsed seconds)"
          sleep 5
        done
        echo "Nuxeo is running"
        
    - name: Initialize Nuxeo repository
      run: |
        python seed_nuxeo.py --url http://localhost:8080/nuxeo --username Administrator --password Administrator
        
    - name: Wait for MCP Server to start
      run: |
        echo "Waiting for MCP Server to start..."
        timeout=60
        start_time=$(date +%s)
        while ! curl -s http://localhost:8081/mcp/health > /dev/null; do
          current_time=$(date +%s)
          elapsed=$((current_time - start_time))
          if [ $elapsed -gt $timeout ]; then
            echo "Timeout waiting for MCP Server to start"
            exit 1
          fi
          echo "Waiting for MCP Server to start... ($elapsed seconds)"
          sleep 2
        done
        echo "MCP Server is running"
        
    - name: Test search tool
      run: |
        python mcp_client.py --url http://localhost:8081 search "SELECT * FROM Document WHERE ecm:primaryType = 'File'"
        
    - name: Test get-document tool
      run: |
        python mcp_client.py --url http://localhost:8081 get-document --path "/default-domain"
```

## Implementation Plan

1. Create the Python CLI client (`mcp_client.py`)
2. Create the Dockerfile
3. Create the Docker Compose configuration (`docker-compose.yml`)
4. Create the GitHub Action workflow file
5. Test the client locally
6. Test the Docker Compose setup locally
7. Push the changes to GitHub and verify the workflow runs successfully
