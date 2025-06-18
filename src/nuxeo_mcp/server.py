#!/usr/bin/env python3
"""
Nuxeo MCP Server implementation.

This server provides tools, resources, and prompt templates for interacting with
a Nuxeo Content Repository Server.
"""

import os
import logging
from typing import Any, Dict, List, Optional, Type, Callable, TypeVar, Union, cast

from fastmcp import FastMCP
from nuxeo.client import Nuxeo

# Import the tools, resources, and templates modules
from .tools import register_tools
from .resources import register_resources

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("nuxeo_mcp")


class NuxeoMCPServer:
    """MCP Server for Nuxeo Content Repository."""

    def __init__(
        self,
        nuxeo_url: str = "http://localhost:8080/nuxeo",
        username: str = "Administrator",
        password: str = "Administrator",
        fastmcp_class: Optional[Type[FastMCP]] = None,
    ):
        """
        Initialize the Nuxeo MCP Server.

        Args:
            nuxeo_url: URL of the Nuxeo server
            username: Nuxeo username
            password: Nuxeo password
            fastmcp_class: FastMCP class to use (for testing)
        """
        self.nuxeo_url = nuxeo_url
        self.username = username
        self.password = password
        
        # Initialize the Nuxeo client
        self.nuxeo = Nuxeo(
            host=nuxeo_url,
            auth=(username, password),
        )
        
        # Initialize the MCP server
        FastMCPClass = fastmcp_class or FastMCP
        self.mcp = FastMCPClass(
            name="nuxeo-mcp-server",
        )
        
        # Register tools and resources
        self._register_tools()
        self._register_resources()

    def _register_tools(self) -> None:
        """Register MCP tools."""
        register_tools(self.mcp, self.nuxeo)

    def _register_resources(self) -> None:
        """Register MCP resources."""
        register_resources(self.mcp, self.nuxeo)


    def run(self) -> None:
        """Run the MCP server."""
        self.mcp.run()


def main() -> None:
    """Run the Nuxeo MCP server."""
    # Get configuration from environment variables
    nuxeo_url = os.environ.get("NUXEO_URL", "http://localhost:8080/nuxeo")
    username = os.environ.get("NUXEO_USERNAME", "Administrator")
    password = os.environ.get("NUXEO_PASSWORD", "Administrator")
    
    # Create and run the server
    server = NuxeoMCPServer(
        nuxeo_url=nuxeo_url,
        username=username,
        password=password,
    )
    server.run()


if __name__ == "__main__":
    main()
