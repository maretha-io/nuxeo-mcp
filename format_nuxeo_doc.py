#!/usr/bin/env python3
"""
Script to demonstrate the format_doc function.

This script formats a sample Nuxeo document using the format_doc function
from the nuxeo_mcp.utility module.
"""

import json
import sys
from nuxeo_mcp.utility import format_doc


def main() -> None:
    """Main entry point."""
    # Sample Nuxeo document
    sample_doc = {
        'changeToken': '1-0',
        'contextParameters': {},
        'entity-type': 'document',
        'facets': ['Folderish', 'NXTag', 'NotCollectionMember'],
        'isCheckedOut': True,
        'isProxy': False,
        'isTrashed': False,
        'isVersion': False,
        'parentRef': '/',
        'path': '/',
        'properties': {
            'common:icon-expanded': None,
            'common:icon': None,
            'dc:description': None,
            'dc:language': None,
            'dc:coverage': None,
            'dc:valid': None,
            'dc:creator': None,
            'dc:modified': None,
            'dc:lastContributor': None,
            'dc:rights': None,
            'dc:expired': None,
            'dc:format': None,
            'dc:created': None,
            'dc:title': None,
            'dc:issued': None,
            'dc:nature': None,
            'dc:subjects': [],
            'dc:contributors': [],
            'dc:source': None,
            'dc:publisher': None,
            'nxtag:tags': []
        },
        'repository': 'default',
        'title': 'dbaccb2c-7bbc-4326-9330-b1bc08dc9e09',
        'type': 'Root',
        'uid': 'dbaccb2c-7bbc-4326-9330-b1bc08dc9e09'
    }
    
    # If a file path is provided as an argument, load the document from the file
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                sample_doc = json.load(f)
        except Exception as e:
            print(f"Error loading document from file: {e}")
            sys.exit(1)
    
    # Format the document
    formatted = format_doc(sample_doc)
    
    # Print the formatted document
    print(formatted)


if __name__ == "__main__":
    main()
