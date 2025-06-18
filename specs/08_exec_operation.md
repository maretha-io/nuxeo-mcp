# Execute Nuxeo Operation Tool

This specification outlines the implementation of a tool for executing Nuxeo Operations.

## Overview

This tool will provide the capability to execute any Nuxeo Operation with various input types and parameters.

## Implementation Details

### Execute Operation Tool

This tool will execute a Nuxeo Operation with the specified parameters and input.

```python
@mcp.tool(
    name="execute_operation",
    description="Execute a Nuxeo Operation with the specified parameters and input")
def execute_operation(
    operation_id: str,
    params: Dict[str, Any] = None,
    input_type: str = None,
    input_value: str = None,
    file_path: str = None
) -> Dict[str, Any]:
    """
    Execute a Nuxeo Operation with the specified parameters and input.
    
    Args:
        operation_id: The ID of the operation to execute
        params: Dictionary of parameters to pass to the operation
        input_type: Type of input ('document_path', 'document_uid', 'file', 'none')
        input_value: Value of the input (document path, document UID, or None)
        file_path: Path to a file to upload as input (only used when input_type is 'file')
    
    Returns:
        The result of the operation execution
    """
    # Create a new operation
    operation = nuxeo.operations.new(operation_id)
    
    # Set parameters if provided
    if params:
        operation.params = params
    
    # Set input based on input_type
    if input_type == 'document_path':
        operation.input_obj = input_value
    elif input_type == 'document_uid':
        operation.input_obj = nuxeo.documents.get(uid=input_value)
    elif input_type == 'file' and file_path:
        # Upload the file and use it as input
        with open(file_path, 'rb') as f:
            uploaded = nuxeo.uploads.batch().upload(f, chunked=True)
        operation.input_obj = uploaded
    
    # Execute the operation
    result = operation.execute()
    
    # Format the result if it's a document or list of documents
    if hasattr(result, 'is_document') and result.is_document:
        return format_doc(result)
    elif isinstance(result, list) and all(hasattr(doc, 'is_document') and doc.is_document for doc in result):
        return format_docs(result)
    
    # Return the raw result for other types
    return result
```

## Utility Functions

We'll use the existing `format_doc` and `format_docs` functions to format the output when it's a Document or a list of Documents.

## Integration

This tool will be added to the `tools.py` file and registered with the MCP server in the `register_tools` function.

## Usage Examples

### Example 1: Execute an operation with a document path as input

```python
execute_operation(
    operation_id="NuxeoDrive.SetSynchronization",
    params={"enable": True},
    input_type="document_path",
    input_value="/My Folder"
)
```

### Example 2: Execute an operation with a document as parameter

```python
execute_operation(
    operation_id="Blob.AttachOnDocument",
    params={"document": "/foo"},
    input_type="file",
    file_path="/path/to/file.pdf"
)
```

### Example 3: Execute an operation with a file as input and document UID as parameter

```python
execute_operation(
    operation_id="Blob.AttachOnDocument",
    params={"document": "document-uid-here"},
    input_type="file",
    file_path="/path/to/file.pdf"
)
