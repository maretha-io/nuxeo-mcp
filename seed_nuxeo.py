#!/usr/bin/env python3
"""
Seed script for Nuxeo Repository.

This script initializes a Nuxeo repository with sample documents for testing:
- Creates a folder
- Creates a file document with a PDF attachment
- Creates a note document with random text
"""

import os
import sys
import random
import tempfile
import argparse
import logging
from typing import Dict, Any, Optional, Union, List, Tuple
from nuxeo.client import Nuxeo
from nuxeo.models import Document, FileBlob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("nuxeo_seed")

# Sample text for generating random content
LOREM_IPSUM = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud 
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute 
irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla 
pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia 
deserunt mollit anim id est laborum.
"""

def create_dummy_pdf(content: Optional[str] = None) -> Optional[str]:
    """
    Create a dummy PDF file with some content.
    
    Args:
        content: Optional content to include in the PDF. If None, default content is used.
        
    Returns:
        Path to the created PDF file, or None if creation failed.
    """
    if content is None:
        content = f"Sample PDF Document\n\n{LOREM_IPSUM}"
    
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix=".pdf")
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(f"%PDF-1.4\n{content}\n%%EOF")
        return path
    except Exception as e:
        logger.error(f"Error creating dummy PDF: {e}")
        os.unlink(path)
        return None

def get_random_text(paragraphs: int = 3) -> str:
    """
    Generate random text from Lorem Ipsum.
    
    Args:
        paragraphs: Number of paragraphs to generate.
        
    Returns:
        Generated random text with the specified number of paragraphs.
    """
    words = LOREM_IPSUM.split()
    result: List[str] = []
    
    for _ in range(paragraphs):
        # Generate a paragraph with random length
        length = random.randint(20, 50)
        paragraph = " ".join(random.choices(words, k=length))
        result.append(paragraph)
    
    return "\n\n".join(result)

def seed_nuxeo_repository(url: str, username: str, password: str) -> bool:
    """
    Seed the Nuxeo repository with sample documents.
    
    Args:
        url: Nuxeo server URL
        username: Nuxeo username
        password: Nuxeo password
        
    Returns:
        True if seeding was successful, False otherwise.
    """
    logger.info(f"Connecting to Nuxeo server at {url}")
    nuxeo = Nuxeo(
        host=url,
        auth=(username, password),
    )
    
    # Check if connection is successful
    try:
        server_info = nuxeo.client.server_info()
        logger.info(f"Connected to Nuxeo server version: {server_info['productVersion']}")
    except Exception as e:
        logger.error(f"Failed to connect to Nuxeo server: {e}")
        return False
    
    # Create a folder in the root
    folder_name = f"MCP Test Folder {random.randint(1000, 9999)}"
    folder_path = f"/default-domain/workspaces/{folder_name}"
    
    logger.info(f"Creating folder: {folder_path}")
    try:
        folder = Document(
            name=folder_name,
            type="Folder",
            properties={
                "dc:title": folder_name,
                "dc:description": "Folder for MCP testing"
            }
        )
        
        # Create the folder in the workspaces
        folder = nuxeo.documents.create(folder, parent_path="/default-domain/workspaces")
        logger.info(f"Created folder with ID: {folder.uid}")
    except Exception as e:
        logger.error(f"Failed to create folder: {e}")
        return False
    
    # Create a file document with PDF attachment
    file_name = f"Sample File {random.randint(1000, 9999)}"
    logger.info(f"Creating file document: {file_name}")
    
    try:
        # Create a dummy PDF file
        pdf_path = create_dummy_pdf()
        if not pdf_path:
            logger.error("Failed to create dummy PDF file")
            return False
        
        # Create the file document
        file_doc = Document(
            name=file_name,
            type="File",
            properties={
                "dc:title": file_name,
                "dc:description": "Sample file for MCP testing"
            }
        )
        
        # Create the document in the folder
        file_doc = nuxeo.documents.create(file_doc, parent_path=folder_path)
        logger.info(f"Created file document with ID: {file_doc.uid}")
        
        # Attach the PDF file
        blob = FileBlob(pdf_path)
        

        # Create and upload a blob
        uploaded = nuxeo.uploads.batch().upload(blob, chunked=True)

        # Attach it to the file
        operation = nuxeo.operations.new('Blob.AttachOnDocument')
        operation.params = {'document': file_doc.uid}
        operation.input_obj = uploaded
        operation.execute()

        logger.info(f"Attached PDF to file document")
        
        # Clean up the temporary file
        os.unlink(pdf_path)
    except Exception as e:
        logger.error(f"Failed to create file document: {e}")
        if pdf_path and os.path.exists(pdf_path):
            os.unlink(pdf_path)
        return False
    
    # Create a note document with random text
    note_name = f"Sample Note {random.randint(1000, 9999)}"
    logger.info(f"Creating note document: {note_name}")
    
    try:
        note_content = get_random_text()
        note_doc = Document(
            name=note_name,
            type="Note",
            properties={
                "dc:title": note_name,
                "dc:description": "Sample note for MCP testing",
                "note:note": note_content,
                "note:mime_type": "text/plain"
            }
        )
        
        # Create the note in the folder
        note_doc = nuxeo.documents.create(note_doc, parent_path=folder_path)
        logger.info(f"Created note document with ID: {note_doc.uid}")
    except Exception as e:
        logger.error(f"Failed to create note document: {e}")
        return False
    
    logger.info("Successfully seeded Nuxeo repository with sample documents")
    
    # Print summary
    print("\nSummary of created documents:")
    print(f"Folder: {folder_path} (ID: {folder.uid})")
    print(f"File: {folder_path}/{file_name} (ID: {file_doc.uid})")
    print(f"Note: {folder_path}/{note_name} (ID: {note_doc.uid})")
    
    return True

def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Seed Nuxeo repository with sample documents")
    parser.add_argument("--url", default="http://localhost:8080/nuxeo", help="Nuxeo server URL")
    parser.add_argument("--username", default="Administrator", help="Nuxeo username")
    parser.add_argument("--password", default="Administrator", help="Nuxeo password")
    
    args = parser.parse_args()
    
    success = seed_nuxeo_repository(args.url, args.username, args.password)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
