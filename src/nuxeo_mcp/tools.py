#!/usr/bin/env python3
"""
Nuxeo MCP Server tools.

This module defines the tools for the Nuxeo MCP Server.
"""

import logging
import json
import os
from typing import Any, Dict, Optional, Callable, List, Annotated
from nuxeo_mcp.utility import (
    format,
    format_docs,
    format_doc,
    return_blob,
    is_uuid,
)
from nuxeo.models import Document
from mcp.types import ImageContent as Image
from pydantic import BaseModel, Field, model_validator

# Configure logging
logger = logging.getLogger("nuxeo_mcp.tools")

# Type aliases
ToolFunction = Callable[[Dict[str, Any]], Dict[str, Any]]



class DocRef(BaseModel):
    path: Annotated[str | None,  Field(description="Repository path")] = None
    uid:  Annotated[str | None,  Field(description="Nuxeo UID")]    = None

    @model_validator(mode="after")
    def one_of_path_or_uid(cls, v):
        if bool(v.path) == bool(v.uid):          # both or neither
            raise ValueError("Provide *exactly* one of 'path' or 'uid'")
        return v
    
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
    
    def get_children(ref: Annotated[str, Field(description="reference can be either a uuid or a path ")] ,
                      as_resource: Annotated[bool, Field(description="Return Document as nuxeo:// resource")] = False,       
) -> Dict[str, Any]:
        """
        List children from a parent document about the Nuxeo repository.
        
        Args: 
            ref: reference can be either a uuid or a path 

        Returns:
            List of documents
        """

        if is_uuid(ref):
            docs = nuxeo.documents.get_children(uid=ref)
        else:
            docs = nuxeo.documents.get_children(path=ref)       

        return format_docs(docs, as_resource=as_resource)

    @mcp.tool(name="search", description="search document using a NXQL query")
    def search(
        query: str,
        pageSize: int = 20,
        currentPageIndex: int = 0,
        content_type="application/json",
    ) -> dict[str, Any]:
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
            json object with 2 keys:
                "content" : the formatted list of documents,
                "content_type" : format used - for example "text/markdown"
        """

        return format(nuxeo.documents.query({"query" : query, "pageSize" : pageSize, "currentPageIndex": currentPageIndex }), content_type)


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


    @mcp.tool(
        name="create_document",
        description="Create a new document in the Nuxeo repository")
    def create_document(
        name: str,
        type: str,
        properties: Dict[str, Any],
        parent_path: str
    ) -> Dict[str, Any]:
        """
        Create a new document in the Nuxeo repository.
        
        This tool creates a new document with the specified properties in the Nuxeo repository.
        It supports creating any document type available in your Nuxeo instance, such as:
        
        - File: Standard document with attached content
        - Folder: Container for other documents
        - Note: Simple text document
        - Workspace: Collaborative space for documents
        - Picture: Image document with additional metadata
        - Video: Video document with additional metadata
        
        ## Example Usage
        
        Create a folder:
        ```
        create_document(
            name="my-folder",
            type="Folder",
            properties={"dc:title": "My Folder", "dc:description": "A test folder"},
            parent_path="/default-domain/workspaces"
        )
        ```
        
        Create a file:
        ```
        create_document(
            name="my-document",
            type="File",
            properties={
                "dc:title": "My Document", 
                "dc:description": "A test document"
            },
            parent_path="/default-domain/workspaces/my-folder"
        )
        ```
        
        Args:
            name: The name of the document (used in the document's path)
            type: The document type (e.g., 'File', 'Folder', 'Note')
            properties: Dictionary of document properties (e.g., {"dc:title": "My Document"})
            parent_path: Path of the parent document where this document will be created
        
        Returns:
            The created document formatted as markdown
        """
        new_doc = Document(
            name=name,
            type=type,
            properties=properties
        )
        
        doc = nuxeo.documents.create(new_doc, parent_path=parent_path)
        return format_doc(doc)


    @mcp.tool(
        name="get_document",
        description="Get a document from the Nuxeo repository")
    def get_document(
        ref: Annotated[str, Field(description="reference can be either a uuid or a path ")] ,       
        fetch_blob: Annotated[bool, Field(description="Return main blob")] = False,
        as_resource: Annotated[bool, Field(description="Return Document as nuxeo:// resource")] = False,
        conversion_format: Annotated[str, Field(description="Convert the document to a different format 'pdf', 'html')")]="",
        rendition: Annotated[str, Field(description="Fetch a specific rendition of the document (e.g., 'thumbnail')")] = ""
    ) -> str|bytes|Image:
        """
        Get a document from the Nuxeo repository.
        
        This tool retrieves a document from the Nuxeo repository by path or UID.
        It can also fetch the document's blob, convert it to a different format,
        or fetch a rendition of the document.
        
        ## Document Identification
        
        You must provide either a path or a UID to identify the document:
        - Path: The document's path in the repository (e.g., "/default-domain/workspaces/my-folder")
        - UID: The document's unique identifier (e.g., "12345678-1234-1234-1234-123456789012")
        
        ## Blob Operations
        
        - fetch_blob: Set to true to fetch the document's main blob (if it has one)
        - conversion_format: Convert the document to a different format (e.g., "pdf", "html")
        - rendition: Fetch a specific rendition of the document (e.g., "thumbnail")
        
        ## Other parameters

        - as_resource: Set to true to get a Nuxeo Resource.

        ## Example Usage
        
        Get a document by path:
        ```
        get_document(ref="/default-domain/workspaces/my-folder")
        ```
        
        Get a document by UID:
        ```
        get_document(ref="12345678-1234-1234-1234-123456789012")
        ```
        
        Get a document's thumbnail:
        ```
        get_document(
            ref="/default-domain/workspaces/my-document",
            rendition="thumbnail"
        )
        ```
        
        Args:
            ref: reference can be either a uuid or a path 
            fetch_blob: Whether to fetch the document's blob
            as_resource: Whether to fetch the document as a nuxeo:// resource
            conversion_format: Format to convert the document to (e.g., 'pdf')
            rendition: Rendition to fetch (e.g., 'thumbnail')
        
        Returns:
            The document formatted as markdown or the blob
        """
        
        if is_uuid(ref):
            doc = nuxeo.documents.get(uid=ref)
        else:
            doc = nuxeo.documents.get(path=ref)        
        
        if as_resource:
            return f"nuxeo://{doc.uid}"
        
        # Handle blob operations if requested
        blob_info = {}
        
        if fetch_blob:
            try:
                # built in method do not propagate headers
                # blob = doc.fetch_blob()

                r=nuxeo.client.request('GET', f"api/v1/repo/default/id/{doc.uid}/@blob/blobholder:0")

                disposition = r.headers["content-disposition"]
                filename = disposition.split(";")[-1].split("=")[-1]
                mime= r.headers["content-type"]
                content_length = int(r.headers["content-length"])

                blob_info = {
                    "name": filename,
                    "mime_type": mime,
                    "size": content_length,
                    "content" : r.content
                }
                return return_blob(blob_info)
            except Exception as e:
                blob_info["blob_error"] = str(e)
        
        if conversion_format:
            try:
                # built in method do not propagate headers
                # conversion = doc.convert({'format': conversion_format})

                r=nuxeo.client.request('GET', path=f"api/v1/repo/default/id/{doc.uid}", adapter="blob/blobholder:0/@convert", params={"format":conversion_format})
                disposition = r.headers["content-disposition"]
                filename = disposition.split(";")[-1].split("=")[-1]
                mime= r.headers["content-type"]
                content_length = int(r.headers["content-length"])

                blob_info = {
                    "format": conversion_format,
                    "name": filename,
                    "mime_type": mime,
                    "size": content_length,
                    "content" : r.content
                }
                return return_blob(blob_info)
            except Exception as e:
                # Log the error for debugging
                logger.error(f"Conversion error: {e}")
                # Return error information instead of continuing
                return {"error": f"Conversion failed: {str(e)}"}
        
        if rendition:
            try:
                # built in method do not propagate headers
                # rendition_blob = doc.fetch_rendition(rendition)
                adapter = f"rendition/{rendition}"
                r=nuxeo.client.request('GET', path=f"api/v1/repo/default/id/{doc.uid}", adapter=adapter)
                disposition = r.headers["content-disposition"]
                filename = disposition.split(";")[-1].split("=")[-1]
                mime= r.headers["content-type"]
                content_length = int(r.headers["content-length"])

                blob_info = {
                    "name": filename,
                    "mime_type": mime,
                    "size": content_length,
                    "content" : r.content                
                }

                return return_blob(blob_info)

            except Exception as e:
                return str(e)
        
        # Format the document
        result = format_doc(doc)
               
        return result


    @mcp.tool(
        name="update_document",
        description="Update an existing document in the Nuxeo repository")
    def update_document(
        path: str = None,
        uid: str = None,
        properties: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Update an existing document in the Nuxeo repository.
        
        This tool updates an existing document in the Nuxeo repository with the specified properties.
        You can identify the document to update by either its path or UID.
        
        ## Document Identification
        
        You must provide either a path or a UID to identify the document:
        - Path: The document's path in the repository (e.g., "/default-domain/workspaces/my-folder")
        - UID: The document's unique identifier (e.g., "12345678-1234-1234-1234-123456789012")
        
        ## Properties
        
        The properties parameter should be a dictionary of document properties to update.
        Common properties include:
        
        - dc:title: Document title
        - dc:description: Document description
        - dc:creator: Document creator
        - dc:contributors: Document contributors
        - dc:created: Creation date
        - dc:modified: Modification date
        
        ## Example Usage
        
        Update a document's title:
        ```
        update_document(
            path="/default-domain/workspaces/my-folder",
            properties={"dc:title": "Updated Folder Title"}
        )
        ```
        
        Update multiple properties:
        ```
        update_document(
            uid="12345678-1234-1234-1234-123456789012",
            properties={
                "dc:title": "Updated Title",
                "dc:description": "Updated Description"
            }
        )
        ```
        
        Args:
            path: Path of the document (mutually exclusive with uid)
            uid: UID of the document (mutually exclusive with path)
            properties: Dictionary of document properties to update
        
        Returns:
            The updated document formatted as markdown
        """
        if not path and not uid:
            raise ValueError("Either path or uid must be provided")
        
        if path and uid:
            raise ValueError("Only one of path or uid should be provided")
        
        doc = nuxeo.documents.get(path=path, uid=uid)
        
        if properties:
            for key, value in properties.items():
                doc.properties[key] = value
        
        doc.save()
        return format_doc(doc)


    @mcp.tool(
        name="delete_document",
        description="Delete a document from the Nuxeo repository")
    def delete_document(
        uid: str = None
    ) -> Dict[str, Any]:
        """
        Delete a document from the Nuxeo repository.
        
        This tool deletes a document from the Nuxeo repository.
        You can identify the document to delete by either its path or UID.
        
        ## Document Identification
        
        You must provide a UID to identify the document:
        - UID: The document's unique identifier (e.g., "12345678-1234-1234-1234-123456789012")
        
        ## Example Usage
                
        Delete a document by UID:
        ```
        delete_document(uid="12345678-1234-1234-1234-123456789012")
        ```
        
        Args:
            uid: UID of the document (mutually exclusive with path)
        
        Returns:
            Status of the deletion operation
        """
        if not uid:
            raise ValueError("uid must be provided")
        
        result = nuxeo.documents.delete(uid=uid)
        return {"status": "success", "message": f"Document deleted successfully"}
