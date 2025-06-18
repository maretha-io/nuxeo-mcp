

Add a `utility.py` in nuxeo_mcp

Add a `format_doc` function that takes as input a Nuxeo Document as a dictionnary and outputs a markdown formatted text

The input will look like

{'changeToken': '1-0', 'contextParameters': {}, 'entity-type': 'document', 'facets': ['Folderish', 'NXTag', 'NotCollectionMember'], 'isCheckedOut': True, 'isProxy': False, 'isTrashed': False, 'isVersion': False, 'parentRef': '/', 'path': '/', 'properties': {'common:icon-expanded': None, 'common:icon': None, 'dc:description': None, 'dc:language': None, 'dc:coverage': None, 'dc:valid': None, 'dc:creator': None, 'dc:modified': None, 'dc:lastContributor': None, 'dc:rights': None, 'dc:expired': None, 'dc:format': None, 'dc:created': None, 'dc:title': None, 'dc:issued': None, 'dc:nature': None, 'dc:subjects': [], 'dc:contributors': [], 'dc:source': None, 'dc:publisher': None, 'nxtag:tags': []}, 'repository': 'default', 'title': 'dbaccb2c-7bbc-4326-9330-b1bc08dc9e09', 'type': 'Root', 'uid': 'dbaccb2c-7bbc-4326-9330-b1bc08dc9e09'}

The output should display:

 - doc UID
 - doc type
 - title
 - path
 - facets
 - flags (isProxy, isCheckedOut ... )
 - the documents properties

 The document properties should displayed in a table, grouping properties by namespaces

 