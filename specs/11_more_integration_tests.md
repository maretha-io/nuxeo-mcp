# Additional Integration Tests for Nuxeo MCP

This specification outlines additional integration tests for the Nuxeo MCP server, focusing on the `get_document` tool and its capabilities for handling different document types and blob operations.

## Overview

The additional tests will focus on:
1. Testing the `get_document` tool with Picture documents
2. Testing blob retrieval
3. Testing document conversion
4. Testing rendition retrieval

## Test Cases

### 1. Test Get Picture Document Metadata

This test will verify that the `get_document` tool can retrieve metadata for a Picture document.

```python
@pytest.mark.integration
def test_get_picture_document(nuxeo_container, nuxeo_url, nuxeo_credentials, seeded_folder_info):
    """Test retrieving a Picture document's metadata."""
    # Create NuxeoMCPServer instance
    server = NuxeoMCPServer(
        nuxeo_url=nuxeo_url,
        username=username,
        password=password,
        fastmcp_class=MockFastMCP,
    )
    
    # Find the get_document tool
    get_document_tool = None
    for tool in server.mcp.tools:
        if tool["name"] == "get_document":
            get_document_tool = tool["func"]
            break
    
    assert get_document_tool is not None, "get_document tool not found"
    
    # Get the path to the seeded Picture document
    # This assumes the seed script creates a Picture document
    picture_path = f"{seeded_folder_info['folder_path']}/Sample Picture"
    
    # Call the tool to get the Picture document metadata
    result = get_document_tool(path=picture_path)
    
    # Check the result
    assert "# Document: Sample Picture" in result, "Expected document title in result"
    assert "**Type**: Picture" in result, "Expected document type to be Picture"
    assert "**Path**:" in result, "Expected document path in result"
```

### 2. Test Get Picture Document Blob

This test will verify that the `get_document` tool can retrieve the blob for a Picture document.

```python
@pytest.mark.integration
def test_get_picture_document_blob(nuxeo_container, nuxeo_url, nuxeo_credentials, seeded_folder_info):
    """Test retrieving a Picture document's blob."""
    # Create NuxeoMCPServer instance
    server = NuxeoMCPServer(
        nuxeo_url=nuxeo_url,
        username=username,
        password=password,
        fastmcp_class=MockFastMCP,
    )
    
    # Find the get_document tool
    get_document_tool = None
    for tool in server.mcp.tools:
        if tool["name"] == "get_document":
            get_document_tool = tool["func"]
            break
    
    assert get_document_tool is not None, "get_document tool not found"
    
    # Get the path to the seeded Picture document
    picture_path = f"{seeded_folder_info['folder_path']}/Sample Picture"
    
    # Call the tool to get the Picture document with its blob
    result = get_document_tool(path=picture_path, fetch_blob=True)
    
    # Check the result
    assert "# Document: Sample Picture" in result, "Expected document title in result"
    assert "## Blob Information" in result, "Expected blob information section"
    assert "\"blob\":" in result, "Expected blob details"
    assert "\"mime_type\":" in result, "Expected MIME type in blob details"
    assert "\"size\":" in result, "Expected size in blob details"
```

### 3. Test Get Picture Document Conversion

This test will verify that the `get_document` tool can convert a Picture document to JPEG format.

```python
@pytest.mark.integration
def test_get_picture_document_conversion(nuxeo_container, nuxeo_url, nuxeo_credentials, seeded_folder_info):
    """Test converting a Picture document to JPEG format."""
    # Create NuxeoMCPServer instance
    server = NuxeoMCPServer(
        nuxeo_url=nuxeo_url,
        username=username,
        password=password,
        fastmcp_class=MockFastMCP,
    )
    
    # Find the get_document tool
    get_document_tool = None
    for tool in server.mcp.tools:
        if tool["name"] == "get_document":
            get_document_tool = tool["func"]
            break
    
    assert get_document_tool is not None, "get_document tool not found"
    
    # Get the path to the seeded Picture document
    picture_path = f"{seeded_folder_info['folder_path']}/Sample Picture"
    
    # Call the tool to get the Picture document converted to JPEG
    result = get_document_tool(path=picture_path, conversion_format="jpeg")
    
    # Check the result
    assert "# Document: Sample Picture" in result, "Expected document title in result"
    assert "## Blob Information" in result, "Expected blob information section"
    assert "\"conversion\":" in result, "Expected conversion details"
    assert "\"format\": \"jpeg\"" in result, "Expected JPEG format in conversion details"
    assert "\"mime_type\":" in result, "Expected MIME type in conversion details"
```

### 4. Test Get Picture Document Thumbnail Rendition

This test will verify that the `get_document` tool can retrieve the thumbnail rendition for a Picture document.

```python
@pytest.mark.integration
def test_get_picture_document_thumbnail(nuxeo_container, nuxeo_url, nuxeo_credentials, seeded_folder_info):
    """Test retrieving a Picture document's thumbnail rendition."""
    # Create NuxeoMCPServer instance
    server = NuxeoMCPServer(
        nuxeo_url=nuxeo_url,
        username=username,
        password=password,
        fastmcp_class=MockFastMCP,
    )
    
    # Find the get_document tool
    get_document_tool = None
    for tool in server.mcp.tools:
        if tool["name"] == "get_document":
            get_document_tool = tool["func"]
            break
    
    assert get_document_tool is not None, "get_document tool not found"
    
    # Get the path to the seeded Picture document
    picture_path = f"{seeded_folder_info['folder_path']}/Sample Picture"
    
    # Call the tool to get the Picture document's thumbnail rendition
    result = get_document_tool(path=picture_path, rendition="thumbnail")
    
    # Check the result
    assert "# Document: Sample Picture" in result, "Expected document title in result"
    assert "## Blob Information" in result, "Expected blob information section"
    assert "\"rendition\":" in result, "Expected rendition details"
    assert "\"name\": \"thumbnail\"" in result, "Expected thumbnail name in rendition details"
    assert "\"mime_type\":" in result, "Expected MIME type in rendition details"
```

## Implementation

These tests will be implemented in a new file `tests/test_document_tools.py` that will focus on testing the document-related tools in the Nuxeo MCP server.

The tests will use the existing fixtures from `conftest.py` to set up the Nuxeo server and seed it with test documents.
