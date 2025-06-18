#!/usr/bin/env python3
"""
Nuxeo MCP Server tools.

This module defines the tools for the Nuxeo MCP Server.
"""

import logging
from typing import Any, Dict, Optional, Callable
from nuxeo_mcp.utility import format_docs, format_page

# Configure logging
logger = logging.getLogger("nuxeo_mcp.tools")

# Type aliases
ToolFunction = Callable[[Dict[str, Any]], Dict[str, Any]]


def register_tools(mcp, nuxeo) -> None:
    """
    Register MCP tools with the FastMCP server.
    
    Args:
        mcp: The FastMCP server instance
        client: The Nuxeo client instance
    """
    # Tool: Get repository info
    @mcp.tool(
        name="get_repository_info",
        description="Get information about the Nuxeo repository")
    def get_repository_info() -> Dict[str, Any]:
        """
        Get information about the Nuxeo repository.
        
        Args: None

        Returns:
            Information about the Nuxeo repository
        """

        server_info = nuxeo.client.server_info()
    
        return server_info


    @mcp.tool(
        name="get_children",
        description="list children of a folder document ")
    def get_children(uid:str|None = None, path:str|None = None) -> Dict[str, Any]:
        """
        List children from a parent document about the Nuxeo repository.
        
        Args: 
            uid : the folder document uuid
            path: the path of the folder document

        Returns:
            List of documents
        """

        return format_docs(nuxeo.documents.get_children(uid = uid, path = path))


    @mcp.tool(
        name="search",
        description="search document using a NXQL query")
    def search(query:str, pageSize:int=20, currentPageIndex:int=0) -> Dict[str, Any]:
        """
        Executes a Nuxeo Query Language (NXQL) statement and returns the matching documents.

        NXQL is a SQL-like language designed to query the Nuxeo content repository. This tool accepts
        a full NXQL query string, executes it, and returns the results.

        ## Query Syntax
        Basic NXQL syntax:
            SELECT (* | [DISTINCT] <select-clause>)
            FROM <doc-type>
            [WHERE <conditions>]
            [ORDER BY <sort-clause>]

        Example queries:
        - SELECT * FROM Document WHERE dc:title LIKE 'Invoice%'
        - SELECT ecm:uuid, dc:title FROM File WHERE ecm:fulltext = 'contract' ORDER BY dc:modified DESC
        - SELECT COUNT(ecm:uuid) FROM Document WHERE dc:created >= DATE '2024-01-01'

        ## Notes
        - You can query metadata, including standard fields like `dc:title`, `ecm:uuid`, `ecm:primaryType`, etc.
        - Use `NOW()` to compare against the current timestamp (e.g., `dc:modified < NOW('-P7D')`).
        - Full-text search is supported via `ecm:fulltext`.
        - List and complex properties can be addressed using `/` or wildcards (e.g., `dc:subjects/* = 'finance'`).
        - Aggregates like COUNT, MIN, MAX are supported (in VCS mode only).

        ## Limitations
        - NXQL execution depends on repository type (VCS, MongoDB, Elasticsearch).
        - Ensure query validity to avoid syntax errors or unsupported patterns.

        Parameters:
            query (str): A valid NXQL query string.
            pageSize (int) : Number of documents to list per page
            currentPageIndex (int) : index of the page to retrieve
            

        Returns:
            List of documents
        """

        return format_page(nuxeo.documents.query({"query" : query, "pageSize" : pageSize, "currentPageIndex": currentPageIndex }))

