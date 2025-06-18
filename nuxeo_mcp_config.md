# Nuxeo MCP Server Configuration Examples

This document provides examples of how to configure the Nuxeo MCP server in your Cline MCP settings file.

## Example 1: Using stdio Transport

This configuration uses the stdio transport, which is the default transport for MCP servers. It's suitable for most use cases and provides good performance.

```json
{
  "mcpServers": {
    "NuxeoMCP": {
      "command": "bash",
      "args": ["-c", "source /Users/thierry.delprat/dev/nuxeo-mcp/venv/bin/activate && python -m nuxeo_mcp"],
      "env": {
        "NUXEO_URL": "http://localhost:8080/nuxeo",
        "NUXEO_USERNAME": "Administrator",
        "NUXEO_PASSWORD": "Administrator",
        "MCP_TRANSPORT": "stdio"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Example 2: Using HTTP Transport

This configuration uses the HTTP transport, which can be useful in certain scenarios, such as when you need to access the MCP server from a different machine or when you want to use tools like curl to interact with the server directly.

```json
{
  "mcpServers": {
    "NuxeoMCP": {
      "command": "bash",
      "args": ["-c", "source /Users/thierry.delprat/dev/nuxeo-mcp/venv/bin/activate && python -m nuxeo_mcp"],
      "env": {
        "NUXEO_URL": "http://localhost:8080/nuxeo",
        "NUXEO_USERNAME": "Administrator",
        "NUXEO_PASSWORD": "Administrator",
        "MCP_TRANSPORT": "http",
        "MCP_HTTP_PORT": "8123",
        "MCP_HTTP_HOST": "localhost"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Example 3: Using Both stdio and HTTP Transports

This configuration uses both stdio and HTTP transports, which provides the best compatibility with different clients. The stdio transport is used for direct communication with Cline, while the HTTP transport allows other tools to interact with the server.

```json
{
  "mcpServers": {
    "NuxeoMCP": {
      "command": "bash",
      "args": ["-c", "source /Users/thierry.delprat/dev/nuxeo-mcp/venv/bin/activate && python -m nuxeo_mcp"],
      "env": {
        "NUXEO_URL": "http://localhost:8080/nuxeo",
        "NUXEO_USERNAME": "Administrator",
        "NUXEO_PASSWORD": "Administrator",
        "MCP_TRANSPORT": "http+stdio",
        "MCP_HTTP_PORT": "8123"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Installation

To use one of these configurations:

1. Copy the desired configuration to your Cline MCP settings file.
2. Replace the paths with the actual paths to your nuxeo-mcp installation.
3. Adjust the environment variables as needed for your Nuxeo server.

> **Important Note**: We're using `python -m nuxeo_mcp` instead of directly executing the server.py file to avoid relative import issues. When a Python file is run directly, it doesn't have a parent package, so relative imports don't work. Using the `-m` flag ensures that Python treats the module as part of a package, allowing relative imports to work correctly.

The configuration file is typically located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Cline**: `~/.config/cline/cline_mcp_settings.json` or `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
