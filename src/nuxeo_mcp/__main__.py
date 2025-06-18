"""
Entry point for running the Nuxeo MCP Server as a module.

Example:
    python -m src.nuxeo_mcp
"""

from .server import main

if __name__ == "__main__":
    main()
