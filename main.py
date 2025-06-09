#!/usr/bin/env python3
"""
Entry point for the DEX MCP server.

This module serves as the main entry point and imports the server implementation
from the src package to maintain clean separation of concerns.
"""

from src.server import create_server

if __name__ == "__main__":
    server = create_server()
    server.run() 