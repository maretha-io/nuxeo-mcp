#!/usr/bin/env python3
"""
Nuxeo MCP Server implementation.

This server provides tools, resources, and prompt templates for interacting with
a Nuxeo Content Repository Server.
"""

import os
import logging
import argparse
import sys
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
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Nuxeo MCP Server")
    parser.add_argument("--http", action="store_true", help="Run in HTTP mode")
    parser.add_argument("--port", type=int, default=8080, help="HTTP port (default: 8080)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="HTTP host (default: 0.0.0.0)")
    args = parser.parse_args()
    
    # Get configuration from environment variables
    nuxeo_url = os.environ.get("NUXEO_URL", "http://localhost:8080/nuxeo")
    username = os.environ.get("NUXEO_USERNAME", "Administrator")
    password = os.environ.get("NUXEO_PASSWORD", "Administrator")
    
    # Create the server
    server = NuxeoMCPServer(
        nuxeo_url=nuxeo_url,
        username=username,
        password=password,
    )
    
    # Run the server in the appropriate mode
    if args.http:
        logger.info(f"Starting MCP server in HTTP mode on {args.host}:{args.port}")
        try:
            # Run the server with streamable-http transport
            server.mcp.run(
                transport="streamable-http",
                host=args.host,
                port=args.port
            )
        except Exception as e:
            logger.error(f"Error starting HTTP server: {e}")
            logger.error("Please check the FastMCP documentation for HTTP mode instructions.")
            sys.exit(1)
    else:
        logger.info("Starting MCP server in stdio mode")
        server.run()


if __name__ == "__main__":
    main()
