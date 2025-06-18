# Simplifying the Server Implementation

This specification describes the simplification of the Nuxeo MCP Server implementation by separating the tools, resources, and templates into separate Python files.

## Overview

The current implementation of the Nuxeo MCP Server has all the tools, resources, and resource templates defined in a single `server.py` file. This can make the file large and difficult to maintain as more functionality is added. By separating these components into separate files, we can improve code organization, maintainability, and testability.

## Requirements

1. Create separate Python files for tools, resources, and resource templates
2. Maintain all existing functionality
3. Ensure all tests continue to pass
4. Update documentation to reflect the new structure

## Implementation

### File Structure

The new file structure will be:

```
src/nuxeo_mcp/
├── __init__.py
├── __main__.py
├── server.py
├── tools.py
├── resources.py
└── templates.py
```

### server.py

The `server.py` file will be simplified to:

- Import the tools, resources, and templates from their respective files
- Initialize the Nuxeo client and MCP server
- Register the tools, resources, and templates
- Provide the main entry point for running the server

### tools.py

The `tools.py` file will contain:

- Functions that implement the MCP tools
- Type definitions for tool functions
- Helper functions for tool implementation

### resources.py

The `resources.py` file will contain:

- Functions that implement the MCP resources
- Type definitions for resource functions
- Helper functions for resource implementation

### templates.py

The `templates.py` file will contain:

- Functions that implement the MCP resource templates
- Type definitions for template functions
- Helper functions for template implementation

## Registration Process

The registration process will be modified to:

1. Import the tool, resource, and template functions from their respective files
2. Register them with the MCP server in the `NuxeoMCPServer` class

## Testing

All existing tests should continue to pass with the new implementation. The tests may need to be updated to import from the new files if they directly import any functions that have been moved.

## Future Enhancements

This new structure will make it easier to:

- Add new tools, resources, and templates without modifying the core server code
- Test individual components in isolation
- Organize tools, resources, and templates by functionality
