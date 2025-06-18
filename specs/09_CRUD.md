# Nuxeo Document CRUD Tools

This specification outlines the implementation of tools for performing CRUD (Create, Read, Update, Delete) operations on Nuxeo documents.

## Overview

These tools will provide capabilities to:
1. Create documents
2. Read documents (including fetching blobs, conversions, and renditions)
3. Update documents
4. Delete documents

## Implementation Details

### 1. Create Document

This tool will create a new document in the Nuxeo repository.

```python
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
    
    Args:
        name: The name of the document
        type: The document type (e.g., 'File', 'Folder', 'Note')
        properties: Dictionary of document properties
        parent_path: Path of the parent document
    
    Returns:
        The created document
    """
    from nuxeo.models import Document
    
    new_doc = Document(
        name=name,
        type=type,
        properties=properties
    )
    
    doc = nuxeo.documents.create(new_doc, parent_path=parent_path)
    return format_doc(doc)
```

### 2. Read Document

This tool will retrieve a document from the Nuxeo repository by path or UID.

```python
@mcp.tool(
    name="get_document",
    description="Get a document from the Nuxeo repository")
def get_document(
    path: str = None,
    uid: str = None,
    fetch_blob: bool = False,
    conversion_format: str = None,
    rendition: str = None
) -> Dict[str, Any]:
    """
    Get a document from the Nuxeo repository.
    
    Args:
        path: Path of the document (mutually exclusive with uid)
        uid: UID of the document (mutually exclusive with path)
        fetch_blob: Whether to fetch the document's blob
        conversion_format: Format to convert the document to (e.g., 'pdf')
        rendition: Rendition to fetch (e.g., 'thumbnail')
    
    Returns:
        The document
    """
    if not path and not uid:
        raise ValueError("Either path or uid must be provided")
    
    if path and uid:
        raise ValueError("Only one of path or uid should be provided")
    
    doc = nuxeo.documents.get(path=path, uid=uid)
    
    if fetch_blob:
        blob = doc.fetch_blob()
        # Handle blob
    
    if conversion_format:
        conversion = doc.convert({'format': conversion_format})
        # Handle conversion
    
    if rendition:
        rendition_blob = doc.fetch_rendition(rendition)
        # Handle rendition
    
    return format_doc(doc)
```

### 3. Update Document

This tool will update an existing document in the Nuxeo repository.

```python
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
    
    Args:
        path: Path of the document (mutually exclusive with uid)
        uid: UID of the document (mutually exclusive with path)
        properties: Dictionary of document properties to update
    
    Returns:
        The updated document
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
```

### 4. Delete Document

This tool will delete a document from the Nuxeo repository.

```python
@mcp.tool(
    name="delete_document",
    description="Delete a document from the Nuxeo repository")
def delete_document(
    path: str = None,
    uid: str = None
) -> Dict[str, Any]:
    """
    Delete a document from the Nuxeo repository.
    
    Args:
        path: Path of the document (mutually exclusive with uid)
        uid: UID of the document (mutually exclusive with path)
    
    Returns:
        Status of the deletion operation
    """
    if not path and not uid:
        raise ValueError("Either path or uid must be provided")
    
    if path and uid:
        raise ValueError("Only one of path or uid should be provided")
    
    result = nuxeo.documents.delete(path=path, uid=uid)
    return {"status": "success", "message": f"Document deleted successfully"}
```

## Utility Functions

We'll use the existing `format_doc` function to format the output when it's a Document.

## Integration

These tools will be added to the `tools.py` file and registered with the MCP server in the `register_tools` function.

## Usage Examples

### Example 1: Create a folder

```python
create_document(
    name="my-folder",
    type="Folder",
    properties={"dc:title": "My Folder", "dc:description": "A test folder"},
    parent_path="/default-domain/workspaces"
)
```

### Example 2: Get a document

```python
get_document(
    path="/default-domain/workspaces/my-folder",
    fetch_blob=False
)
```

### Example 3: Update a document

```python
update_document(
    path="/default-domain/workspaces/my-folder",
    properties={"dc:title": "Updated Folder Title"}
)
```

### Example 4: Delete a document

```python
delete_document(
    path="/default-domain/workspaces/my-folder"
)
```

### Example 5: Get a document rendition

```python
get_document(
    path="/default-domain/workspaces/my-document",
    rendition="thumbnail"
)
```
