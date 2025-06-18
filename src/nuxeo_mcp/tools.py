#!/usr/bin/env python3
"""
Nuxeo MCP Server tools.

This module defines the tools for the Nuxeo MCP Server.
"""

import logging
import json
import os
from typing import Any, Dict, Optional, Callable, List
from nuxeo_mcp.utility import format_docs, format_page, format_doc

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


    @mcp.tool(
        name="get_document_types",
        description="Get information about document types and schemas defined in the Nuxeo server")
    def get_document_types() -> Dict[str, Any]:
        """
        Get information about document types and schemas defined in the Nuxeo server.
        
        This tool retrieves comprehensive information about all document types and their
        associated schemas defined in the Nuxeo server. The information includes:
        
        - Document type hierarchy (parent-child relationships)
        - Facets associated with each document type
        - Schemas associated with each document type
        
        Returns:
            Dictionary containing document types and their definitions with two main keys:
            - 'doctypes': Information about document types
            - 'schemas': Basic schema information
        """
        types_info = nuxeo.client.request('GET', 'api/v1/config/types/')
        return types_info.json()


    @mcp.tool(
        name="get_schemas",
        description="Get detailed information about schemas defined in the Nuxeo server")
    def get_schemas() -> List[Dict[str, Any]]:
        """
        Get detailed information about schemas defined in the Nuxeo server.
        
        This tool retrieves detailed information about all schemas defined in the Nuxeo server.
        For each schema, it provides:
        
        - Schema name and prefix
        - All fields defined in the schema with their types
        - Field constraints and default values
        
        Returns:
            List of schemas with their complete definitions
        """
        schemas = nuxeo.client.request('GET', 'api/v1/config/schemas/')
        return schemas.json()


    @mcp.tool(
        name="get_operations",
        description="Get information about available Automation Operations in the Nuxeo server")
    def get_operations() -> Dict[str, Any]:
        """
        Get information about available Automation Operations in the Nuxeo server.
        
        This tool retrieves comprehensive information about all Automation Operations
        available in the Nuxeo server. For each operation, it provides:
        
        - Operation ID and aliases
        - Category and label
        - Description and documentation
        - Input/output types (signature)
        - Parameters with their types, descriptions, and constraints
        
        Example usage:
            To get information about a specific operation:
            operations = get_operations()
            operation_info = operations["Document.AddACL"]
        
        Returns:
            Dictionary where each key is an Operation name and the value is its documentation
        """
        return nuxeo.operations.operations


    @mcp.tool(
        name="execute_operation",
        description="Execute a Nuxeo Operation with the specified parameters and input")
    def execute_operation(
        operation_id: str,
        params: Dict[str, Any] = None,
        input_type: str = None,
        input_value: str = None,
        file_path: str = None
    ) -> Any:
        """
        Execute a Nuxeo Operation with the specified parameters and input.
        
        This tool allows you to execute any Nuxeo Automation Operation with various
        input types and parameters. It supports:
        
        - Document path or UID as input
        - File upload as input
        - Parameters for the operation
        - Automatic formatting of document results
        
        ## Input Types
        
        - 'document_path': Use a document path as input (e.g., '/default-domain/workspaces/my-doc')
        - 'document_uid': Use a document UID as input
        - 'file': Upload a file as input (requires file_path parameter)
        - None: No input (for operations that don't require input)
        
        ## Examples
        
        1. Set synchronization on a folder:
           ```
           execute_operation(
               operation_id="NuxeoDrive.SetSynchronization",
               params={"enable": True},
               input_type="document_path",
               input_value="/My Folder"
           )
           ```
        
        2. Attach a blob to a document:
           ```
           execute_operation(
               operation_id="Blob.AttachOnDocument",
               params={"document": "/foo"},
               input_type="file",
               file_path="/path/to/file.pdf"
           )
           ```
        
        Args:
            operation_id: The ID of the operation to execute
            params: Dictionary of parameters to pass to the operation
            input_type: Type of input ('document_path', 'document_uid', 'file', 'none')
            input_value: Value of the input (document path, document UID, or None)
            file_path: Path to a file to upload as input (only used when input_type is 'file')
        
        Returns:
            The result of the operation execution, formatted if it's a document or list of documents
        """
        # Create a new operation
        operation = nuxeo.operations.new(operation_id)
        
        # Set parameters if provided
        if params:
            operation.params = params
        
        # Set input based on input_type
        if input_type in ['document_path', 'document_uid', 'document'] :
            operation.input_obj = input_value
        elif input_type == 'file' and file_path:
            # Check if file exists
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")
                
            # Upload the file and use it as input
            with open(file_path, 'rb') as f:
                uploaded = nuxeo.uploads.batch().upload(f, chunked=True)
            operation.input_obj = uploaded
        
        # Execute the operation
        result = operation.execute()
        
        # Format the result if it's a document or list of documents
        if hasattr(result, 'is_document') and result.is_document:
            return format_doc(result)
        elif isinstance(result, list) and len(result) > 0 and hasattr(result[0], 'is_document') and result[0].is_document:
            return format_docs(result)
        
        # Return the raw result for other types
        return result
