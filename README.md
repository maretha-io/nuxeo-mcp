# Nuxeo MCP Server

A Model Context Protocol (MCP) server for interacting with a Nuxeo Content Repository Server. This server provides tools, resources, and prompt templates for AI assistants to interact with Nuxeo content repositories.

## Features

- 🔄 Connect to a Nuxeo Content Repository Server
- 🛠️ MCP Tools for common Nuxeo operations
- 📚 MCP Resources for accessing Nuxeo content
- 🧩 MCP Resource Templates for dynamic content access
- 🐳 Docker support for testing with a Nuxeo server
- 🧪 Comprehensive test suite with pytest

## Requirements

- Python 3.9+
- Nuxeo Server (can be run via Docker)
- Docker (for testing)

## Building and Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/nuxeo-mcp.git
cd nuxeo-mcp
```

### 2. Set up a virtual environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Unix/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
# Install the package in development mode
pip install -e .

# For development with additional tools
pip install -e ".[dev]"
```

### 4. Build the package

```bash
# Build the package
python -m build

# This will create distribution files in the dist/ directory
```

## Running the Server Locally

### Starting the MCP Server

You can run the MCP server using one of the following methods:

```bash
# Using the entry point script
nuxeo-mcp

# Or directly with Python module
python -m nuxeo_mcp

# Or from the source directory
python -m src.nuxeo_mcp.server
```

### Configuration Options

The server can be configured using the following environment variables:

- `NUXEO_URL`: URL of the Nuxeo server (default: `http://localhost:8080/nuxeo`)
- `NUXEO_USERNAME`: Username for Nuxeo authentication (default: `Administrator`)
- `NUXEO_PASSWORD`: Password for Nuxeo authentication (default: `Administrator`)

Example with custom configuration:

```bash
NUXEO_URL="http://mynuxeo.example.com/nuxeo" NUXEO_USERNAME="admin" NUXEO_PASSWORD="secret" nuxeo-mcp
```

### Configuring with Cline

To use the Nuxeo MCP server with Cline, you need to add a configuration to your Cline MCP settings file. See the [Nuxeo MCP Server Configuration Examples](./nuxeo_mcp_config.md) for detailed examples of how to configure the server with different transport options:

- Using stdio transport only
- Using HTTP transport only
- Using both stdio and HTTP transports

The configuration file is typically located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Cline**: `~/.config/cline/cline_mcp_settings.json` or `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

### Running Nuxeo with Docker

For development and testing, you can run a Nuxeo server using Docker:

```bash
# Pull the Nuxeo image
docker pull nuxeo/nuxeo:latest

# Run Nuxeo container
docker run -d --name nuxeo -p 8080:8080 \
  -e NUXEO_DEV_MODE=true \
  -e NUXEO_PACKAGES="nuxeo-web-ui" \
  nuxeo/nuxeo:latest

# Check if Nuxeo is running
docker ps | grep nuxeo

# View Nuxeo logs
docker logs -f nuxeo
```

Access the Nuxeo server at http://localhost:8080/nuxeo with default credentials Administrator/Administrator.

### Seeding the Nuxeo Repository with Test Data

The project includes a script to initialize the Nuxeo repository with sample documents for testing:

```bash
# Run the seed script with default settings
./seed_nuxeo.py

# Or with custom settings
./seed_nuxeo.py --url http://mynuxeo.example.com/nuxeo --username admin --password secret
```

This script will:
1. Create a folder in the Nuxeo workspaces
2. Create a File document with a dummy PDF attachment
3. Create a Note document with random text

The script outputs the paths and IDs of the created documents, which can be used for testing the MCP server.

## Running Tests

The project includes a comprehensive test suite using pytest with different test categories.

### Running All Tests

```bash
# Run all tests
pytest
```

### Running Unit Tests Only

```bash
# Run unit tests only
pytest -m unit -v
```

### Running Integration Tests

Integration tests require a running Nuxeo server (automatically managed via Docker):

```bash
# Run integration tests
pytest --integration -m integration -v -s
```

The `-s` flag allows you to see the output from the tests, which is useful for debugging.

### Test Categories

- **Unit Tests**: Tests that don't require external services and use mocks
- **Integration Tests**: Tests that require a running Nuxeo server

### Skipping Docker-dependent Tests

If you want to skip tests that require Docker:

```bash
SKIP_DOCKER=true pytest
```

### Debugging Tests

For more verbose output during tests:

```bash
# Enable verbose output
pytest -v

# Show print statements and real-time output
pytest -s

# Show logs
pytest --log-cli-level=INFO
```

## MCP Server Capabilities

### Tools

- `get_repository_info`: Get information about the Nuxeo repository

### Resources

- `nuxeo://info`: Basic information about the connected Nuxeo server


## Development

### Project Structure

```
nuxeo-mcp/
├── src/
│   └── nuxeo_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py
│       ├── tools.py
│       ├── resources.py
│       └── utility.py
├── tests/
│   ├── conftest.py
│   ├── test_basic.py
│   ├── test_server.py
│   └── test_integration.py
├── specs/
│   ├── 01_init.md
│   ├── 02_tests.md
│   ├── 03_seed.md
│   ├── 04_type_hinting.md
│   └── 05_simplify.md
├── seed_nuxeo.py
├── pyproject.toml
└── README.md
```

### Adding New Tools

To add a new tool to the MCP server, add a new function in the `tools.py` file:

```python
# In src/nuxeo_mcp/tools.py
def register_tools(mcp, nuxeo) -> None:
    # ... existing tools ...
    
    @mcp.tool(
        name="your_tool_name",
        description="Description of your tool",
        input_schema={
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of param1",
                },
            },
            "required": ["param1"],
        },
    )
    def your_tool_name(args: Dict[str, Any]) -> Dict[str, Any]:
        """Your tool implementation."""
        # Implementation here
        return {"result": "Your result"}
```

### Adding New Resources

To add a new resource to the MCP server, add a new function in the `resources.py` file:

```python
# In src/nuxeo_mcp/resources.py
def register_resources(mcp, nuxeo) -> None:
    # ... existing resources ...
    
    @mcp.resource(
        uri="nuxeo://your-resource",
        name="Your Resource Name",
        description="Description of your resource",
    )
    def get_your_resource() -> Dict[str, Any]:
        """Your resource implementation."""
        # Implementation here
        return {"result": "Your result"}
```

### Utility Functions

The `utility.py` module provides utility functions for working with Nuxeo documents and other common tasks:

#### Document Formatting

The `format_doc` function formats a Nuxeo document as markdown text:

```python
from nuxeo_mcp.utility import format_doc

# Get a document from Nuxeo
doc = nuxeo.client.get_document('/path/to/document')

# Format the document as markdown
markdown = format_doc(doc)
print(markdown)
```

The formatted output includes:
- Basic document information (UID, type, title, path, facets)
- Document flags (isProxy, isCheckedOut, isTrashed, isVersion)
- Document properties grouped by namespace in markdown tables

You can use this function to generate human-readable representations of Nuxeo documents for documentation, reports, or user interfaces.


## License

MIT
