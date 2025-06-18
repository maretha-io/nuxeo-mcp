# Using the `nuxeo://info` Resource

The `nuxeo://info` resource is a key feature of the Nuxeo MCP Server that provides basic information about the connected Nuxeo server. This document explains how to use this resource and what information it provides.

## Resource Description

- **URI**: `nuxeo://info`
- **Name**: Nuxeo Server Information
- **Description**: Basic information about the connected Nuxeo server

## Information Provided

The `nuxeo://info` resource returns a JSON object with the following information:

```json
{
  "url": "http://localhost:8080/nuxeo",
  "username": "Administrator",
  "connected": true,
  "version": "2023.x"
}
```

- **url**: The URL of the Nuxeo server
- **username**: The username used to connect to the Nuxeo server
- **connected**: A boolean indicating whether the connection to the Nuxeo server is active
- **version**: The version of the Nuxeo server (if available)

## How to Access the Resource

### Using Claude with Cline

Once you have configured the Nuxeo MCP server in your Cline settings (see [Nuxeo MCP Server Configuration Examples](./nuxeo_mcp_config.md)), you can access the `nuxeo://info` resource directly in your conversations with Claude:

```
Can you tell me about the Nuxeo server I'm connected to? Use the nuxeo://info resource.
```

Claude will then use the MCP server to access the resource and display the information about your Nuxeo server.

### Using the MCP HTTP API

If you've configured the Nuxeo MCP server to use the HTTP transport, you can also access the resource using a standard HTTP client like curl:

```bash
curl http://localhost:8123/resource/nuxeo%3A%2F%2Finfo
```

Replace `8123` with the port number you specified in your configuration.

## Implementation Details

The `nuxeo://info` resource is implemented in the `resources.py` file:

```python
@mcp.resource(
    uri="nuxeo://info",
    name="Nuxeo Server Information",
    description="Basic information about the connected Nuxeo server",
)
def get_nuxeo_info() -> Dict[str, Any]:
    """
    Get basic information about the Nuxeo server.
    
    Returns:
        Basic information about the Nuxeo server
    """
    try:
        # Get server information from the Nuxeo client
        try:
            server_info = nuxeo.client.server_info()
            version = server_info.get("productVersion", "Unknown")
        except Exception:
            version = "Unknown"
            
        info = {
            "url": nuxeo_url,
            "username": username,
            "connected": True,
            "version": version,
        }
        return info
    except Exception as e:
        logger.error(f"Error getting Nuxeo info: {e}")
        return {"error": str(e)}
```

The resource attempts to retrieve the server information from the Nuxeo client, including the product version. If this fails, it still returns the basic connection information with the version marked as "Unknown".

## Use Cases

The `nuxeo://info` resource is useful for:

1. **Verifying Connectivity**: Quickly check if the MCP server is properly connected to the Nuxeo server
2. **Identifying the Server**: Get information about which Nuxeo server you're connected to
3. **Checking Credentials**: Verify that you're authenticated with the correct username
4. **Version Checking**: Determine the version of the Nuxeo server for compatibility checks

## Example Usage in a Workflow

Here's an example of how you might use the `nuxeo://info` resource in a workflow:

1. Start by checking the connection to the Nuxeo server using `nuxeo://info`
2. If connected, proceed with document operations
3. If not connected, troubleshoot the connection issues

This resource serves as a simple health check for your Nuxeo integration.
