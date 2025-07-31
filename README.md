# Nuxeo MCP Server

![Build and Unit Tests](https://github.com/tiry/nx-mcp-poc/actions/workflows/build-and-unit-tests.yml/badge.svg)
![Integration Tests](https://github.com/tiry/nx-mcp-poc/actions/workflows/integration-tests.yml/badge.svg)

A Model Context Protocol (MCP) server for interacting with a Nuxeo Content Repository Server. This server provides tools, resources, and prompt templates for AI assistants to interact with Nuxeo content repositories.

## Features

- 🔄 Connect to a Nuxeo Content Repository Server
- 🛠️ MCP Tools for common Nuxeo operations (query, retrieve, create, update, delete documents)
- 📚 MCP Resources for accessing Nuxeo content
- 🧩 MCP Resource Templates for dynamic content access
- 🐳 Docker support for testing with a Nuxeo server
- 🧪 Comprehensive test suite with pytest

## Requirements

- Python 3.10+
- Nuxeo Server (can be run via Docker)
- Docker (for testing)

## Installation

```bash
pip install nuxeo-mcp
```

## Quick Start

```bash
# Start the MCP server with default settings
nuxeo-mcp

# With custom configuration
NUXEO_URL="http://mynuxeo.example.com/nuxeo" NUXEO_USERNAME="admin" NUXEO_PASSWORD="secret" nuxeo-mcp
```

## Documentation

- [Developer Guide](DEVELOPER.md) - How to build, run tests, and extend the project
- [Usage Guide](USAGE.md) - How to use the MCP Server

## Docker

### Building the Docker Image

You can build a Docker image for the nuxeo-mcp server using the Dockerfile provided at the root of the project:

```bash
# Build the Docker image with the name nuxeo-mcp-server
docker build -t nuxeo-mcp-server .
```

To build a x86 compatible image on a arm device:

```bash
docker buildx build --platform linux/amd64 -t nuxeo-mcp-server:latest .
```


### Running the Docker Container

Once built, you can run the nuxeo-mcp server in a Docker container:

```bash
# Run the container in SSE mode (default), exposing port 8181
docker run -p 8181:8181 --name nuxeo-mcp nuxeo-mcp-server
```

### Environment Variables

You can configure the nuxeo-mcp server using environment variables:

#### Nuxeo Connection Settings

```bash
# Run with custom Nuxeo connection settings
docker run -p 8181:8181 \
  -e NUXEO_URL="http://mynuxeo.example.com/nuxeo" \
  -e NUXEO_USERNAME="admin" \
  -e NUXEO_PASSWORD="secret" \
  nuxeo-mcp-server
```

#### Server Mode Configuration

The Docker container supports configurable server modes through environment variables:

- `MCP_MODE`: Server mode (`sse` or `http`, default: `sse`)
- `MCP_PORT`: Server port (default: `8181`)
- `MCP_HOST`: Server host (default: `0.0.0.0`)

```bash
# Run in HTTP mode
docker run -p 8181:8181 \
  -e MCP_MODE=http \
  --name nuxeo-mcp \
  nuxeo-mcp-server

# Run in SSE mode (default)
docker run -p 8181:8181 \
  -e MCP_MODE=sse \
  --name nuxeo-mcp \
  nuxeo-mcp-server

# Run on a different port
docker run -p 9000:9000 \
  -e MCP_PORT=9000 \
  --name nuxeo-mcp \
  nuxeo-mcp-server
```

## Configuring with Cline

To use the Nuxeo MCP server with Cline, you need to add a configuration to your Cline MCP settings file. See the [Nuxeo MCP Server Configuration Examples](./nuxeo_mcp_config.md) for detailed examples of how to configure the server with different transport options.

The configuration file is typically located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Cline**: `~/.config/cline/cline_mcp_settings.json` or `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

## License

This project is licensed under the MIT License.
