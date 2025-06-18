# Nuxeo Introspection Tools

This specification outlines the implementation of tools for introspecting the Nuxeo server configuration.

## Overview

These tools will provide capabilities to:
1. List document types and schemas
2. List available Automation Operations

## Implementation Details

### 1. List Document Types and Schemas

This tool will retrieve information about all document types and schemas defined in the Nuxeo server.

```python
@mcp.tool(
    name="get_document_types",
    description="Get information about document types and schemas defined in the Nuxeo server")
def get_document_types() -> Dict[str, Any]:
    """
    Get information about document types and schemas defined in the Nuxeo server.
    
    Returns:
        Dictionary containing document types and their definitions
    """
    types_info = nuxeo.client.request('GET', 'api/v1/config/types/')
    return types_info.json()
```

### 2. List Schemas

This tool will retrieve detailed information about all schemas defined in the Nuxeo server.

```python
@mcp.tool(
    name="get_schemas",
    description="Get detailed information about schemas defined in the Nuxeo server")
def get_schemas() -> Dict[str, Any]:
    """
    Get detailed information about schemas defined in the Nuxeo server.
    
    Returns:
        List of schemas with their definitions
    """
    schemas = nuxeo.client.request('GET', 'api/v1/config/schemas/')
    return schemas.json()
```

### 3. List Automation Operations

This tool will retrieve information about all available Automation Operations in the Nuxeo server.

```python
@mcp.tool(
    name="get_operations",
    description="Get information about available Automation Operations in the Nuxeo server")
def get_operations() -> Dict[str, Any]:
    """
    Get information about available Automation Operations in the Nuxeo server.
    
    Returns:
        Dictionary of operations with their documentation
    """
    return nuxeo.operations.operations
```

## Utility Functions

We may need to add utility functions to format the output of these tools for better readability, similar to the existing `format_docs` and `format_page` functions.

## Integration

These tools will be added to the `tools.py` file and registered with the MCP server in the `register_tools` function.
