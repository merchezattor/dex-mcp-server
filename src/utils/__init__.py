"""
Utility functions for the DEX MCP server.
"""

from .logging import setup_logging
from .lifecycle import setup_lifecycle_handlers

__all__ = ["setup_logging", "setup_lifecycle_handlers"] 