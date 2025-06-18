"""
Unit tests for the utility module.

These tests verify the functionality of the utility functions.
"""

import pytest
from nuxeo_mcp.utility import format_doc, format_property_value


@pytest.mark.unit
def test_format_doc() -> None:
    """Test that the format_doc function formats a document correctly."""
    # Create a test document
    doc = {
        'uid': 'dbaccb2c-7bbc-4326-9330-b1bc08dc9e09',
        'type': 'Root',
        'title': 'Test Document',
        'path': '/',
        'facets': ['Folderish', 'NXTag', 'NotCollectionMember'],
        'isProxy': False,
        'isCheckedOut': True,
        'isTrashed': False,
        'isVersion': False,
        'properties': {
            'dc:title': 'Test Document',
            'dc:description': 'This is a test document',
            'dc:creator': 'Administrator',
            'dc:created': '2023-01-01T00:00:00.000Z',
            'dc:modified': '2023-01-02T00:00:00.000Z',
            'dc:contributors': ['Administrator', 'Guest'],
            'common:icon': None,
            'nxtag:tags': []
        }
    }
    
    # Format the document
    formatted = format_doc(doc)
    
    # Check that the formatted document contains the expected information
    assert 'Document: Test Document' in formatted
    assert '**UID**: dbaccb2c-7bbc-4326-9330-b1bc08dc9e09' in formatted
    assert '**Type**: Root' in formatted
    assert '**Path**: /' in formatted
    assert '**Facets**: Folderish, NXTag, NotCollectionMember' in formatted
    assert '**Is Proxy**: False' in formatted
    assert '**Is Checked Out**: True' in formatted
    assert '**Is Trashed**: False' in formatted
    assert '**Is Version**: False' in formatted
    assert 'DC Namespace' in formatted
    assert 'COMMON Namespace' in formatted
    assert 'NXTAG Namespace' in formatted
    assert '| dc:title | Test Document |' in formatted
    assert '| dc:description | This is a test document |' in formatted
    assert '| dc:creator | Administrator |' in formatted
    assert '| dc:contributors | Administrator, Guest |' in formatted
    assert '| common:icon | *None* |' in formatted
    assert '| nxtag:tags | *Empty list* |' in formatted


@pytest.mark.unit
def test_format_doc_empty() -> None:
    """Test that the format_doc function handles empty documents."""
    assert format_doc({}) == "No document provided"
    assert format_doc(None) == "No document provided"


@pytest.mark.unit
def test_format_property_value() -> None:
    """Test that the format_property_value function formats property values correctly."""
    assert format_property_value(None) == "*None*"
    assert format_property_value([]) == "*Empty list*"
    assert format_property_value([1, 2, 3]) == "1, 2, 3"
    assert format_property_value({}) == "*Empty object*"
    assert format_property_value({'key': 'value'}) == "*Complex object*"
    assert format_property_value(True) == "True"
    assert format_property_value(False) == "False"
    assert format_property_value(42) == "42"
    assert format_property_value(3.14) == "3.14"
    assert format_property_value("") == "*Empty string*"
    assert format_property_value("Hello") == "Hello"
    assert format_property_value("Hello|World") == "Hello\\|World"
