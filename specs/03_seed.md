# Nuxeo Repository Seeding

This specification describes the seeding process for the Nuxeo repository to support testing of the MCP server.

## Overview

The `seed_nuxeo.py` script initializes a Nuxeo repository with sample documents that can be used to test the MCP server's capabilities. This ensures that there is consistent test data available for both manual testing and automated integration tests.

## Requirements

1. Connect to a Nuxeo server using configurable connection parameters
2. Create a folder structure for organizing test documents
3. Create a File document with a PDF attachment
4. Create a Note document with text content
5. Provide clear output of created document paths and IDs
6. Handle errors gracefully with appropriate logging

## Implementation

### Connection Parameters

The script accepts the following parameters:

- `--url`: Nuxeo server URL (default: `http://localhost:8080/nuxeo`)
- `--username`: Nuxeo username (default: `Administrator`)
- `--password`: Nuxeo password (default: `Administrator`)

### Document Structure

The script creates the following document structure:

```
/default-domain/workspaces/
└── MCP Test Folder {random-id}/
    ├── Sample File {random-id}
    └── Sample Note {random-id}
```

Where:
- `{random-id}` is a random number to ensure uniqueness across multiple runs

### Document Types

1. **Folder**:
   - Type: `Folder`
   - Properties:
     - `dc:title`: "MCP Test Folder {random-id}"
     - `dc:description`: "Folder for MCP testing"

2. **File**:
   - Type: `File`
   - Properties:
     - `dc:title`: "Sample File {random-id}"
     - `dc:description`: "Sample file for MCP testing"
   - Attachment:
     - A dummy PDF file with Lorem Ipsum content
     - Attached at `file:content` xpath

3. **Note**:
   - Type: `Note`
   - Properties:
     - `dc:title`: "Sample Note {random-id}"
     - `dc:description`: "Sample note for MCP testing"
     - `note:note`: Random Lorem Ipsum text
     - `note:mime_type`: "text/plain"

### Output

The script outputs:
- Log messages showing progress and any errors
- A summary of created documents with paths and IDs

## Usage

```bash
# Run with default settings
./seed_nuxeo.py

# Run with custom settings
./seed_nuxeo.py --url http://mynuxeo.example.com/nuxeo --username admin --password secret
```

## Error Handling

The script handles the following error conditions:
- Connection failures to the Nuxeo server
- Failures to create documents
- Failures to create or attach files
- Cleanup of temporary files in case of errors

## Future Enhancements

Potential future enhancements include:
- Support for creating more document types
- Support for creating more complex document hierarchies
- Support for creating documents with more complex metadata
- Support for creating documents with more complex attachments
- Integration with the test suite to automatically seed test data
