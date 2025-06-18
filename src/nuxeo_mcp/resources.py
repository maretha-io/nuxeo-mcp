#!/usr/bin/env python3
"""
Nuxeo MCP Server resources.

This module defines the resources for the Nuxeo MCP Server.
"""

import logging
from typing import Any, Dict, Optional, Callable
from nuxeo_mcp.utility import format_doc

# Configure logging
logger = logging.getLogger("nuxeo_mcp.resources")

# Type aliases
ResourceFunction = Callable[[], Dict[str, Any]]


def register_resources(mcp, nuxeo) -> None:
    """
    Register MCP resources with the FastMCP server.
    
    Args:
        mcp: The FastMCP server instance
        nuxeo: The Nuxeo client instance
    """
    # Get the Nuxeo URL and username from the client
    nuxeo_url = nuxeo.client.host    # Resource: Nuxeo Server Information
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
                "connected": True,
                "version": version,
            }
            return info
        except Exception as e:
            logger.error(f"Error getting Nuxeo info: {e}")
            return {"error": str(e)}


    @mcp.resource(
        uri="nuxeo://{uid}",
        name="Get  Document using UUID",
        description="Get  Document using UUID",
    )
    def get_document(uid: str) -> Dict[str, Any]:

        return format_doc(nuxeo.documents.get(uid = uid).as_dict())

    @mcp.resource(
        uri="nuxeo://{path*}",
        name="Get  Document using the path",
        description="Get  Document using the path",
    )
    def get_document_by_path(path: str) -> Dict[str, Any]:

        if not path.startswith("/"):
            path = f"/{path}"

        return format_doc(nuxeo.documents.get(path = path).as_dict())


