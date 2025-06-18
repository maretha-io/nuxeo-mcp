"""
Unit tests for the Nuxeo MCP Server.

These tests verify the functionality of the MCP server using mocks,
without requiring a connection to a real Nuxeo server.
"""

import pytest
import unittest.mock as mock
import sys
from typing import List, Dict, Any, Optional, Callable, Union, Type
from unittest.mock import MagicMock, patch

# Create mocks for the unit tests
mock_nuxeo_client = MagicMock()
mock_fastmcp = MagicMock()

# Create a mock FastMCP class for unit tests
class MockFastMCP:
    def __init__(self, name: str):
        self.name: str = name
        self.tools: List[Dict[str, Any]] = []
        self.resources: List[Dict[str, Any]] = []
    
    def tool(self, name: str, description: str, input_schema: Optional[Dict[str, Any]] = None):
        def decorator(func):
            self.tools.append({
                "name": name, 
                "description": description, 
                "input_schema": input_schema,
                "func": func
            })
            return func
        return decorator
    
    def resource(self, uri: str, name: str, description: str):
        def decorator(func):
            self.resources.append({"uri": uri, "name": name, "description": description, "func": func})
            return func
        return decorator
    
    
    def list_tools(self) -> List[Any]:
        return [type('Tool', (), {'name': t['name']}) for t in self.tools]
    
    def list_resources(self) -> List[Any]:
        return [type('Resource', (), {'uri': r['uri']}) for r in self.resources]
    
    
    def run(self) -> None:
        pass

# Patch the FastMCP class for unit tests
sys.modules['fastmcp'] = mock_fastmcp
sys.modules['fastmcp'].FastMCP = MockFastMCP

# Import the server module after patching
from nuxeo_mcp.server import NuxeoMCPServer


@pytest.mark.unit
def test_mcp_server_initialization() -> None:
    """Test that the MCP server can be initialized."""
    # Mock the Nuxeo client to avoid actual connection
    with mock.patch('nuxeo_mcp.server.Nuxeo'):
        server = NuxeoMCPServer(
            nuxeo_url="http://localhost:8080/nuxeo",
            username="Administrator",
            password="Administrator",
            fastmcp_class=MockFastMCP,
        )
        
        # Check that the server was initialized correctly
        assert server.nuxeo_url == "http://localhost:8080/nuxeo"
        assert server.username == "Administrator"
        assert server.password == "Administrator"
        assert server.mcp is not None


@pytest.mark.unit
def test_mcp_tools_registration() -> None:
    """Test that the MCP server registers tools correctly."""
    # Mock the Nuxeo client to avoid actual connection
    with mock.patch('nuxeo_mcp.server.Nuxeo'):
        server = NuxeoMCPServer(fastmcp_class=MockFastMCP)
        
        # Get the list of tools
        tools = server.mcp.list_tools()
        
        # Check that the expected tools are registered
        tool_names = [tool.name for tool in tools]
        assert "get_repository_info" in tool_names


@pytest.mark.unit
def test_mcp_resources_registration() -> None:
    """Test that the MCP server registers resources correctly."""
    # Mock the Nuxeo client to avoid actual connection
    with mock.patch('nuxeo_mcp.server.Nuxeo'):
        server = NuxeoMCPServer(fastmcp_class=MockFastMCP)
        
        # Get the list of resources
        resources = server.mcp.list_resources()
        
        # Check that the expected resources are registered
        resource_uris = [resource.uri for resource in resources]
        assert "nuxeo://info" in resource_uris
